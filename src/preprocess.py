import math
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.merge import merge
from rasterio.transform import from_origin
from rasterio.warp import reproject

RAW_DIR = Path("data/raw/sentinel2")
PROCESSED_DIR = Path("data/processed")
STUDY_AREA_PATH = Path("data/raw/study_area/study_area.shp")


def find_band(date, tile, band, resolution):
    pattern = f"{tile}_{date}T*_{band}_{resolution}m.jp2"
    matches = list(RAW_DIR.rglob(pattern))

    if not matches:
        raise FileNotFoundError(f"No matching band found: {pattern}")
    elif len(matches) > 1:
        raise ValueError(f"Multiple matching bands found: {pattern}")

    return matches[0]


def merge_tiles(date, band, resolution, study_area):
    path_a = find_band(date, "T32UPA", band, resolution)
    path_b = find_band(date, "T32UPB", band, resolution)
    bounds = tuple(study_area.total_bounds)

    with (
        rasterio.open(path_a) as src_a,
        rasterio.open(path_b) as src_b
    ):
        if src_a.crs != study_area.crs or src_b.crs != study_area.crs:
            raise ValueError(f"Unexpected source CRS: {date} {band}")

        mosaic, transform = merge(
            [src_a, src_b],
            bounds=bounds,
            res=(int(resolution), int(resolution)),
            target_aligned_pixels=True
        )

    return mosaic, transform


def save_raster(output_path, raster, transform):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(
        output_path, "w",
        driver="GTiff",
        height=raster.shape[1],
        width=raster.shape[2],
        count=raster.shape[0],
        dtype=raster.dtype,
        crs="EPSG:32632",
        transform=transform,
        compress="deflate",
        nodata=0
    ) as dst:
        dst.write(raster)


def create_reference_grid(study_area, resolution=10):
    xmin, ymin, xmax, ymax = study_area.total_bounds

    xmin = math.floor(xmin / resolution) * resolution
    ymin = math.floor(ymin / resolution) * resolution
    xmax = math.ceil(xmax / resolution) * resolution
    ymax = math.ceil(ymax / resolution) * resolution

    width = round((xmax - xmin) / resolution)
    height = round((ymax - ymin) / resolution)
    transform = from_origin(xmin, ymax, resolution, resolution)

    return (height, width), transform, study_area.crs


def align_band(date, band, resolution, study_area):
    mosaic, source_transform = merge_tiles(date, band, resolution, study_area)
    target_shape, target_transform, target_crs = create_reference_grid(study_area)

    if band == "SCL":
        dtype = np.uint8
        method = Resampling.nearest

    elif band in ["B04", "B08"]:
        dtype = np.float32
        method = Resampling.nearest

    elif band in ["B11", "B12"]:
        dtype = np.float32
        method = Resampling.bilinear
        
    else:
        raise ValueError(f"Unknown band: {band}")

    target = np.zeros((1, target_shape[0], target_shape[1]), dtype=dtype)

    reproject(
        source=mosaic[0],
        destination=target[0],
        src_transform=source_transform,
        src_crs="EPSG:32632",
        src_nodata=0,
        dst_transform=target_transform,
        dst_crs=target_crs,
        dst_nodata=0,
        resampling=method
    )

    study_area_mask = geometry_mask(
        study_area.geometry,
        out_shape=target_shape,
        transform=target_transform,
        invert=True
    )
    target[0, ~study_area_mask] = 0

    return target, target_transform, target_crs


def mask_bands(date):
    with rasterio.open(PROCESSED_DIR / f"{date}_SCL.tif") as src:
        scl = src.read(1)
        shape = src.shape
        crs = src.crs
        transform = src.transform

    valid_scl = np.isin(scl, [4, 5, 6])

    if not np.any(valid_scl):
        raise ValueError(f"No valid SCL pixels: {date}")

    for band in ["B04", "B08", "B11", "B12"]:
        with rasterio.open(PROCESSED_DIR / f"{date}_{band}.tif") as src:
            if src.shape != shape or src.crs != crs or src.transform != transform:
                raise ValueError(f"Raster grids do not match: {date} {band}")
            raster = src.read()

        raster[0, ~valid_scl] = 0
        output_path = PROCESSED_DIR / "masked" / f"{date}_{band}_masked.tif"
        save_raster(output_path, raster, transform)

    print(f"{date}: SCL mask applied, {np.sum(valid_scl)} valid pixels")


def check_outputs(date):
    with rasterio.open(PROCESSED_DIR / f"{date}_SCL.tif") as src:
        valid_scl = np.isin(src.read(1), [4, 5, 6])
        shape = src.shape
        crs = src.crs
        transform = src.transform

    for band in ["B04", "B08", "B11", "B12"]:
        path = PROCESSED_DIR / "masked" / f"{date}_{band}_masked.tif"

        with rasterio.open(path) as src:
            if src.shape != shape or src.crs != crs or src.transform != transform:
                raise ValueError(f"Raster grids do not match: {date} {band}")
            if src.nodata != 0:
                raise ValueError(f"Unexpected NoData value: {date} {band}")
            data = src.read(1)

        if np.any((data != 0) & ~valid_scl):
            raise ValueError(f"Invalid pixels outside SCL mask: {date} {band}")

    print(f"{date}: 4 raster grids and masks verified")


def main():
    study_area = gpd.read_file(STUDY_AREA_PATH).to_crs("EPSG:32632")
    bands = {"B04": 10, "B08": 10, "B11": 20, "B12": 20, "SCL": 20}

    for date in ["20180701", "20240709"]:
        for band, resolution in bands.items():
            raster, transform, _ = align_band(date, band, resolution, study_area)
            output_path = PROCESSED_DIR / f"{date}_{band}.tif"
            save_raster(output_path, raster, transform)

        print(f"{date}: {len(bands)} bands aligned and saved")
        mask_bands(date)
        check_outputs(date)


if __name__ == "__main__":
    main()
