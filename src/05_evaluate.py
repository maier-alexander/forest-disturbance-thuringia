from pathlib import Path
import rasterio
import numpy as np
from rasterio.enums import Resampling
from rasterio.warp import reproject

PROCESSED_DIR = Path("data/processed")
FOREST_DIR = PROCESSED_DIR / "forest"
WALD_PFAD = Path("data/raw/reference/thuenen/holzbodenkarte_2018_32632.tif")
DLR_PFAD = PROCESSED_DIR / "reference" / "dlr_loss_2018_2024.tif"
INDIZES = ["NDVI", "NDMI", "NBR"]
SCHWELLEN = np.arange(-0.50, -0.049, 0.025)


def pruefe_gitter(src, shape, crs, transform):

    if src.shape != shape or src.crs != crs or src.transform != transform:
        raise ValueError(f"Rastergitter stimmen nicht überein: {src.name}")


def maskiere_wald():

    referenz_pfad = PROCESSED_DIR / "change" / "delta_NBR.tif"

    with rasterio.open(referenz_pfad) as ref:
        ziel_shape = ref.shape
        ziel_transform = ref.transform
        ziel_crs = ref.crs
        profil = ref.profile.copy()

    wald = np.zeros(ziel_shape, dtype=np.uint8)

    with rasterio.open(WALD_PFAD) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=wald,
            src_nodata=255,
            dst_nodata=0,
            dst_transform=ziel_transform,
            dst_crs=ziel_crs,
            resampling=Resampling.nearest
        )

    wald_valid = wald == 1

    if not np.any(wald_valid):
        raise ValueError("Keine Waldpixel gefunden. Waldmaske und Rastergitter prüfen.")

    FOREST_DIR.mkdir(parents=True, exist_ok=True)

    wald_profil = profil.copy()
    wald_profil.update(dtype="uint8", count=1, nodata=0)

    with rasterio.open(FOREST_DIR / "forest_mask_2018.tif", "w", **wald_profil) as dst:
        dst.write(wald_valid.astype(np.uint8), 1)

    print(f"Waldpixel 2018: {np.sum(wald_valid)}")

    for index_name in INDIZES:

        pfad = PROCESSED_DIR / "change" / f"delta_{index_name}.tif"

        with rasterio.open(pfad) as src:

            pruefe_gitter(src, ziel_shape, ziel_crs, ziel_transform)
            delta = src.read(1)
            delta_profil = src.profile.copy()

        delta = delta.astype(np.float32)
        delta[~wald_valid] = np.nan
        delta_profil.update(dtype="float32", count=1, nodata=np.nan)

        zielpfad = FOREST_DIR / f"delta_{index_name}_forest.tif"

        with rasterio.open(zielpfad, "w", **delta_profil) as dst:
            dst.write(delta, 1)

        print(f"{index_name}: {np.sum(np.isfinite(delta))} gültige Waldpixel")
        print(f"Gespeichert: {zielpfad}")


def zeige_statistik(werte, perzentile):

    if werte.size == 0:
        raise ValueError("Keine gültigen Pixel für die Auswertung.")
    
    print(f"Pixel: {werte.size}")
    print(f"Mittelwert: {np.mean(werte):.3f}")
    print(f"Median: {np.median(werte):.3f}")

    for p in perzentile:
        print(f"Perzentil {p}: {np.percentile(werte, p):.3f}")

    for schwelle in [-0.2, -0.3, -0.4]:
        print(f"Anteil unter {schwelle}: {np.mean(werte < schwelle) * 100:.2f} %")


def analysiere_verteilung(index_name, werte):

    print(f"\n{index_name} | Waldflächen 2018")
    zeige_statistik(werte, [1, 5, 10, 25, 50, 75, 90, 95, 99])


def vergleiche_dlr(index_name, delta, dlr, valid):

    print(f"\n{index_name} | DLR-Vergleich")

    for name, gruppe in [("DLR-Verlust", 1), ("Kein DLR-Verlust", 0)]:
        print(f"\n{name}")
        zeige_statistik(delta[valid & (dlr == gruppe)], [25, 75])


def berechne_metriken(werte, referenz, schwelle):

    vorhersage = werte < schwelle

    tp = np.sum(vorhersage & referenz)
    fp = np.sum(vorhersage & ~referenz)
    fn = np.sum(~vorhersage & referenz)
    tn = np.sum(~vorhersage & ~referenz)

    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0

    return precision, recall, f1, tp, fp, fn, tn


def evaluiere_schwellen(index_name, delta, dlr, valid):

    zeilen = np.arange(delta.shape[0])[:, None]
    spalten = np.arange(delta.shape[1])[None, :]

    training = (zeilen // 250 + spalten // 250) % 2 == 0
    train_mask = valid & training
    test_mask = valid & ~training

    x_train = delta[train_mask]
    y_train = dlr[train_mask] == 1
    x_test = delta[test_mask]
    y_test = dlr[test_mask] == 1

    if (not np.any(y_train) or np.all(y_train)
            or not np.any(y_test) or np.all(y_test)):
        raise ValueError(f"Beide DLR-Klassen müssen in Training und Test vorhanden sein: {index_name}")

    beste_schwelle = None
    bester_f1 = -1

    for schwelle in SCHWELLEN:
        _, _, f1, _, _, _, _ = berechne_metriken(x_train, y_train, schwelle)
        
        if f1 > bester_f1:
            bester_f1 = f1
            beste_schwelle = schwelle

    precision, recall, f1, tp, fp, fn, tn = berechne_metriken(
        x_test, y_test, beste_schwelle
    )

    print(f"\n{index_name} | Schwellenwertoptimierung")
    print(f"Trainingspixel: {x_train.size}")
    print(f"Testpixel: {x_test.size}")
    print(f"Beste Schwelle: {beste_schwelle:.3f}")
    print(f"Training F1: {bester_f1:.3f}")
    print(f"Test Precision: {precision:.3f}")
    print(f"Test Recall: {recall:.3f}")
    print(f"Test F1: {f1:.3f}")
    print(f"TP: {tp} | FP: {fp} | FN: {fn} | TN: {tn}")


def klassifiziere_waldverlust(schwelle=-0.125):

    pfad = PROCESSED_DIR / "forest" / "delta_NBR_forest.tif"

    with rasterio.open(pfad) as src:
        delta = src.read(1)
        profil = src.profile.copy()

    valid = np.isfinite(delta)

    klassifikation = np.full(delta.shape, 255, dtype=np.uint8)
    klassifikation[valid] = (delta[valid] < schwelle).astype(np.uint8)

    profil.update(dtype="uint8", nodata=255)

    zielpfad = PROCESSED_DIR / "classification" / "forest_loss_NBR.tif"
    zielpfad.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(zielpfad, "w", **profil) as dst:
        dst.write(klassifikation, 1)

    anzahl = np.sum(klassifikation == 1)

    print(f"\nKlassifizierte Verlustpixel: {anzahl}")
    print(f"Potenzieller Kronendachverlust: {anzahl / 100:.2f} ha")
    print(f"Gespeichert: {zielpfad}")


def main():

    ausgaben = [FOREST_DIR / "forest_mask_2018.tif"] + [
        FOREST_DIR / f"delta_{index_name}_forest.tif" for index_name in INDIZES
    ]

    if not all(pfad.exists() for pfad in ausgaben):
        maskiere_wald()

    with rasterio.open(DLR_PFAD) as src_dlr:
        dlr = src_dlr.read(1)
        shape = src_dlr.shape
        crs = src_dlr.crs
        transform = src_dlr.transform

    klassen = np.unique(dlr)

    if not np.all(np.isin(klassen, [0, 1, 255])) or not np.all(np.isin([0, 1], klassen)):
        raise ValueError("DLR-Referenz muss die Klassen 0, 1 und optional 255 enthalten.")

    for index_name in INDIZES:
        pfad = FOREST_DIR / f"delta_{index_name}_forest.tif"

        with rasterio.open(pfad) as src:
            pruefe_gitter(src, shape, crs, transform)
            delta = src.read(1)

        valid = np.isfinite(delta) & np.isin(dlr, [0, 1])

        analysiere_verteilung(index_name, delta[np.isfinite(delta)])

        if index_name in ["NDMI", "NBR"]:
            vergleiche_dlr(index_name, delta, dlr, valid)
            evaluiere_schwellen(index_name, delta, dlr, valid)

    klassifiziere_waldverlust()


if __name__ == "__main__":
    main()
