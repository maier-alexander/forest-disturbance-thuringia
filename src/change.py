from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject

PROCESSED_DIR = Path("data/processed")
FOREST_DIR = PROCESSED_DIR / "forest"
FOREST_PATH = Path("data/raw/reference/thuenen/holzbodenkarte_2018_32632.tif")
INDEX_NAMES = ["NDVI", "NDMI", "NBR"]


def calculate_delta(index_name, date_old, date_new):
    path_old = PROCESSED_DIR / "indices" / f"{date_old}_{index_name}.tif"
    path_new = PROCESSED_DIR / "indices" / f"{date_new}_{index_name}.tif"

    with (
        rasterio.open(path_old) as src_old,
        rasterio.open(path_new) as src_new
    ):
        if (
            src_old.shape != src_new.shape
            or src_old.crs != src_new.crs
            or src_old.transform != src_new.transform
        ):
            raise ValueError("Raster grids do not match.")

        index_old = src_old.read(1)
        index_new = src_new.read(1)
        profile = src_old.profile.copy()

    valid = (
        np.isfinite(index_old)
        & np.isfinite(index_new)
        & (index_old >= -1)
        & (index_old <= 1)
        & (index_new >= -1)
        & (index_new <= 1)
    )
    if not np.any(valid):
        raise ValueError(f"No valid pixels: {index_name}")

    delta = np.full(index_old.shape, np.nan, dtype=np.float32)
    delta[valid] = index_new[valid] - index_old[valid]

    profile.update(driver="GTiff", dtype="float32", count=1, nodata=np.nan, compress="deflate")
    output_path = PROCESSED_DIR / "change" / f"delta_{index_name}.tif"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(delta, 1)

    print(f"Delta {index_name}: {np.sum(valid)} valid pixels, mean {np.nanmean(delta):.3f}")
    return output_path


def check_grid(src, shape, crs, transform):
    if src.shape != shape or src.crs != crs or src.transform != transform:
        raise ValueError(f"Raster grids do not match: {src.name}")


def apply_forest_mask():
    reference_path = PROCESSED_DIR / "change" / "delta_NBR.tif"

    with rasterio.open(reference_path) as ref:
        target_shape = ref.shape
        target_transform = ref.transform
        target_crs = ref.crs
        profile = ref.profile.copy()

    forest = np.zeros(target_shape, dtype=np.uint8)

    with rasterio.open(FOREST_PATH) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=forest,
            src_nodata=255,
            dst_nodata=0,
            dst_transform=target_transform,
            dst_crs=target_crs,
            resampling=Resampling.nearest
        )

    valid_forest = forest == 1
    if not np.any(valid_forest):
        raise ValueError("No forest pixels found. Check forest mask and raster grid.")

    FOREST_DIR.mkdir(parents=True, exist_ok=True)
    forest_profile = profile.copy()
    forest_profile.update(dtype="uint8", count=1, nodata=0)

    with rasterio.open(FOREST_DIR / "forest_mask_2018.tif", "w", **forest_profile) as dst:
        dst.write(valid_forest.astype(np.uint8), 1)

    print(f"2018 forest mask: {np.sum(valid_forest)} forest pixels")

    for index_name in INDEX_NAMES:
        path = PROCESSED_DIR / "change" / f"delta_{index_name}.tif"

        with rasterio.open(path) as src:
            check_grid(src, target_shape, target_crs, target_transform)
            delta = src.read(1)
            delta_profile = src.profile.copy()

        delta = delta.astype(np.float32)
        delta[~valid_forest] = np.nan
        delta_profile.update(dtype="float32", count=1, nodata=np.nan)
        output_path = FOREST_DIR / f"delta_{index_name}_forest.tif"

        with rasterio.open(output_path, "w", **delta_profile) as dst:
            dst.write(delta, 1)

        print(f"{index_name}: {np.sum(np.isfinite(delta))} valid forest pixels")


def main():
    for index_name in INDEX_NAMES:
        calculate_delta(index_name, "20180701", "20240709")

    apply_forest_mask()


if __name__ == "__main__":
    main()
