
from pathlib import Path
import rasterio
import numpy as np
from rasterio.warp import reproject
from rasterio.enums import Resampling


PROCESSED_DIR = Path("data/processed")
DLR_PFAD = Path("data/raw/reference/dlr/FCCL_DE_P1M.tif")


def erstelle_dlr_referenz():

    referenz_pfad = PROCESSED_DIR / "forest" / "forest_mask_2018.tif"

    with rasterio.open(referenz_pfad) as ref:
        ziel_shape = ref.shape
        ziel_transform = ref.transform
        ziel_crs = ref.crs
        profil = ref.profile.copy()
        wald = ref.read(1) == 1

    dlr = np.full(ziel_shape, np.nan, dtype=np.float32)

    with rasterio.open(DLR_PFAD) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=dlr,
            src_nodata=src.nodata,
            dst_nodata=np.nan,
            dst_transform=ziel_transform,
            dst_crs=ziel_crs,
            resampling=Resampling.nearest
        )

    verlust = (dlr >= 12) & (dlr <= 82)
    kein_verlust = (dlr == 0) | ((dlr >= 83) & (dlr <= 98))

    referenz = np.full(ziel_shape, 255, dtype=np.uint8)

    referenz[wald & kein_verlust] = 0
    referenz[wald & verlust] = 1

    profil.update(
        dtype="uint8",
        nodata=255,
        compress="deflate"
    )

    zielpfad = PROCESSED_DIR / "reference" / "dlr_loss_2018_2024.tif"
    zielpfad.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(zielpfad, "w", **profil) as dst:
        dst.write(referenz, 1)

    anzahl_verlust = np.sum(referenz == 1)
    anzahl_intakt = np.sum(referenz == 0)

    print(f"DLR-Verlustpixel: {anzahl_verlust}")
    print(f"DLR-Pixel ohne Verlust: {anzahl_intakt}")
    print(f"Ausgeschlossene Pixel: {np.sum(referenz == 255)}")
    print(f"DLR-Verlustfläche: {anzahl_verlust / 100:.2f} ha")
    print(f"Gespeichert: {zielpfad}")


def main():

    erstelle_dlr_referenz()


if __name__ == "__main__":
    main()
