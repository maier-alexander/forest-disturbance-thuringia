
from pathlib import Path
import rasterio
import numpy as np


PROCESSED_DIR = Path("data/processed")


def berechne_delta(index_name, datum_alt, datum_neu):

    pfad_alt = PROCESSED_DIR / "indices" / f"{datum_alt}_{index_name}.tif"
    pfad_neu = PROCESSED_DIR / "indices" / f"{datum_neu}_{index_name}.tif"

    with (
        rasterio.open(pfad_alt) as src_alt,
        rasterio.open(pfad_neu) as src_neu
    ):

        if (
            src_alt.shape != src_neu.shape
            or src_alt.crs != src_neu.crs
            or src_alt.transform != src_neu.transform
        ):
            raise ValueError("Rastergitter stimmen nicht überein.")

        index_alt = src_alt.read(1)
        index_neu = src_neu.read(1)

        profil = src_alt.profile.copy()

    valid = (
        np.isfinite(index_alt)
        & np.isfinite(index_neu)
        & (index_alt >= -1)
        & (index_alt <= 1)
        & (index_neu >= -1)
        & (index_neu <= 1)
    )

    delta = np.full(index_alt.shape, np.nan, dtype=np.float32)

    delta[valid] = index_neu[valid] - index_alt[valid]

    profil.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        nodata=np.nan,
        compress="deflate"
    )

    zielpfad = PROCESSED_DIR / "change" / f"delta_{index_name}.tif"
    zielpfad.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(zielpfad, "w", **profil) as dst:
        dst.write(delta, 1)

    print(f"\nDelta {index_name} | {datum_alt} → {datum_neu}")
    print(f"Gemeinsam gültige Pixel: {np.sum(valid)}")
    print(f"Minimum: {np.nanmin(delta):.3f}")
    print(f"Maximum: {np.nanmax(delta):.3f}")
    print(f"Mittelwert: {np.nanmean(delta):.3f}")
    print(f"Gespeichert: {zielpfad}")

    return zielpfad


def main():

    for index_name in ["NDVI", "NDMI", "NBR"]:
        berechne_delta(index_name, "20180701", "20240709")


if __name__ == "__main__":
    main()
