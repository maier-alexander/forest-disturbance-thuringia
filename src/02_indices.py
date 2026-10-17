
from pathlib import Path
import rasterio
import numpy as np


PROCESSED_DIR = Path("data/processed")

INDEX_BAENDER = {
    "NDVI": ("B08", "B04"),
    "NDMI": ("B08", "B11"),
    "NBR": ("B08", "B12")
}

BOA_OFFSETS = {
    "20180701": -1000,
    "20240709": -1000
}


def berechne_index(datum, index_name):

    if index_name not in INDEX_BAENDER:
        raise ValueError(f"Unbekannter Index: {index_name}")

    band1, band2 = INDEX_BAENDER[index_name]

    pfad1 = PROCESSED_DIR / "masked" / f"{datum}_{band1}_masked.tif"
    pfad2 = PROCESSED_DIR / "masked" / f"{datum}_{band2}_masked.tif"

    with (
        rasterio.open(pfad1) as src1,
        rasterio.open(pfad2) as src2
    ):

        if (
            src1.shape != src2.shape
            or src1.crs != src2.crs
            or src1.transform != src2.transform
        ):
            raise ValueError("Rastergitter stimmen nicht überein.")

        dn1 = src1.read(1)
        dn2 = src2.read(1)

        profil = src1.profile.copy()

    valid = (dn1 != 0) & (dn2 != 0)

    offset = BOA_OFFSETS[datum]
    quantifizierung = 10000

    ref1 = (dn1.astype(np.float32) + offset) / quantifizierung
    ref2 = (dn2.astype(np.float32) + offset) / quantifizierung

    zaehler = ref1 - ref2
    nenner = ref1 + ref2

    valid = valid & np.isfinite(nenner) & (nenner != 0)

    index = np.full(dn1.shape, np.nan, dtype=np.float32)

    np.divide(
        zaehler,
        nenner,
        out=index,
        where=valid
    )

    profil.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        nodata=np.nan,
        compress="deflate"
    )

    zielpfad = PROCESSED_DIR / "indices" / f"{datum}_{index_name}.tif"
    zielpfad.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(zielpfad, "w", **profil) as dst:
        dst.write(index, 1)

    print(f"\n{datum} | {index_name}")
    print(f"Gültige Pixel: {np.sum(valid)}")
    print(f"Minimum: {np.nanmin(index):.3f}")
    print(f"Maximum: {np.nanmax(index):.3f}")
    print(f"Mittelwert: {np.nanmean(index):.3f}")
    print(f"Gespeichert: {zielpfad}")

    return zielpfad


def main():

    for datum in ["20180701", "20240709"]:
        for index_name in INDEX_BAENDER:
            berechne_index(datum, index_name)


if __name__ == "__main__a":
    main()


for datum in ["20180701", "20240709"]:
    for index_name in ["NDVI", "NDMI", "NBR"]:
        with rasterio.open(
            PROCESSED_DIR / "indices" / f"{datum}_{index_name}.tif"
        ) as src:
            index = src.read(1)

        gueltig = np.isfinite(index)
        ausserhalb = gueltig & ((index < -1) | (index > 1))

        print(datum, index_name, "Außerhalb [-1, 1]:", ausserhalb.sum())