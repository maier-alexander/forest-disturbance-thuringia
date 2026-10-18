from pathlib import Path

import numpy as np
import rasterio

PROCESSED_DIR = Path("data/processed")
INDEX_BANDS = {
    "NDVI": ("B08", "B04"),
    "NDMI": ("B08", "B11"),
    "NBR": ("B08", "B12")
}
BOA_OFFSETS = {
    "20180701": -1000,
    "20240709": -1000
}


def calculate_index(date, index_name):
    if index_name not in INDEX_BANDS:
        raise ValueError(f"Unknown index: {index_name}")

    band1, band2 = INDEX_BANDS[index_name]
    path1 = PROCESSED_DIR / "masked" / f"{date}_{band1}_masked.tif"
    path2 = PROCESSED_DIR / "masked" / f"{date}_{band2}_masked.tif"

    with (
        rasterio.open(path1) as src1,
        rasterio.open(path2) as src2
    ):
        if (
            src1.shape != src2.shape
            or src1.crs != src2.crs
            or src1.transform != src2.transform
        ):
            raise ValueError("Raster grids do not match.")

        dn1 = src1.read(1)
        dn2 = src2.read(1)
        profile = src1.profile.copy()

    valid = (dn1 != 0) & (dn2 != 0)
    offset = BOA_OFFSETS[date]
    quantification = 10000

    ref1 = (dn1.astype(np.float32) + offset) / quantification
    ref2 = (dn2.astype(np.float32) + offset) / quantification
    numerator = ref1 - ref2
    denominator = ref1 + ref2

    valid = valid & np.isfinite(numerator) & np.isfinite(denominator) & (denominator != 0)
    if not np.any(valid):
        raise ValueError(f"No valid pixels: {date} {index_name}")

    index = np.full(dn1.shape, np.nan, dtype=np.float32)
    np.divide(numerator, denominator, out=index, where=valid)

    profile.update(driver="GTiff", dtype="float32", count=1, nodata=np.nan, compress="deflate")
    output_path = PROCESSED_DIR / "indices" / f"{date}_{index_name}.tif"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(index, 1)

    out_of_range = np.sum(valid & ((index < -1) | (index > 1)))
    print(f"{date} {index_name}: {np.sum(valid)} valid pixels, {out_of_range} outside [-1, 1]")
    return output_path


def main():
    for date in ["20180701", "20240709"]:
        for index_name in INDEX_BANDS:
            calculate_index(date, index_name)


if __name__ == "__main__":
    main()
