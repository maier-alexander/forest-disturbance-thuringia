
import rasterio
from rasterio.merge import merge
from rasterio.windows import Window
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.warp import reproject
from rasterio.transform import from_origin
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import math



RAW_DIR = Path("data/raw/sentinel2")
PROCESSED_DIR = Path("data/processed")


def finde_band(datum, tile, band, aufloesung):

    muster = f"{tile}_{datum}T*_{band}_{aufloesung}m.jp2"
    treffer = list(RAW_DIR.rglob(muster))

    if len(treffer) == 0:
        raise FileNotFoundError("Fehler: Keine Datei mit diesem Namen gefunden.")
    elif len(treffer) > 1:
        raise ValueError("Fehler: Es wurden mehrere passende Dateien gefunden.")

    return treffer[0]


aoi = gpd.read_file("data/raw/aoi_extend_shp/AOI_extend.shp")
aoi_utm = aoi.to_crs("EPSG:32632")


def merge_to_mosaik(datum, band, aufloesung):

    pfad_a = finde_band(datum, "T32UPA", band, aufloesung)
    pfad_b = finde_band(datum, "T32UPB", band, aufloesung)

    bounds = tuple(aoi_utm.total_bounds)

    with (
        rasterio.open(pfad_a) as src_a,
        rasterio.open(pfad_b) as src_b
    ):
        
        mosaik, transform = merge(
            [src_a, src_b],
            bounds=bounds,
            res=(int(aufloesung), int(aufloesung)),
            target_aligned_pixels=True
        )
    
    return mosaik, transform
    

def speichere_raster(dateipfad, mosaik_maskiert, transform):

    dateipfad.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(
        dateipfad, "w",
        driver="GTiff",
        height=mosaik_maskiert.shape[1],
        width=mosaik_maskiert.shape[2],
        count=mosaik_maskiert.shape[0],
        dtype=mosaik_maskiert.dtype,
        crs="EPSG:32632",
        transform=transform,
        compress="deflate",
        nodata=0
    ) as dst:

        dst.write(mosaik_maskiert)


def erstelle_referenzgitter(aoi_utm, aufloesung=10):

    xmin, ymin, xmax, ymax = aoi_utm.total_bounds

    xmin = math.floor(xmin / aufloesung) * aufloesung
    ymin = math.floor(ymin / aufloesung) * aufloesung
    xmax = math.ceil(xmax / aufloesung) * aufloesung
    ymax = math.ceil(ymax / aufloesung) * aufloesung

    breite = round((xmax - xmin) / aufloesung)
    hoehe = round((ymax - ymin) / aufloesung)

    transform = from_origin(xmin, ymax, aufloesung, aufloesung)

    return (hoehe, breite), transform, aoi_utm.crs


def band_ausrichten(datum, band, aufloesung):

    mosaik, quelle_transform = merge_to_mosaik(datum, band, aufloesung)

    ziel_shape, ziel_transform, ziel_crs = erstelle_referenzgitter(
        aoi_utm, aufloesung=10
    )

    if band == "SCL":
        dtype = np.uint8
        methode = Resampling.nearest

    elif band in ["B04", "B08"]:
        dtype = np.float32
        methode = Resampling.nearest

    elif band in ["B11", "B12"]:
        dtype = np.float32
        methode = Resampling.bilinear

    else:
        raise ValueError(f"Unbekanntes Band: {band}")

    ziel = np.zeros(
        (1, ziel_shape[0], ziel_shape[1]),
        dtype=dtype
    )

    reproject(
        source=mosaik[0],
        destination=ziel[0],
        src_transform=quelle_transform,
        src_crs="EPSG:32632",
        src_nodata=0,
        dst_transform=ziel_transform,
        dst_crs=ziel_crs,
        dst_nodata=0,
        resampling=methode
    )

    aoi_maske = geometry_mask(
        aoi_utm.geometry,
        out_shape=ziel_shape,
        transform=ziel_transform,
        invert=True
    )

    ziel[0, ~aoi_maske] = 0

    return ziel, ziel_transform, ziel_crs


def maskiere_baender(datum):

    scl_pfad = PROCESSED_DIR / f"{datum}_SCL.tif"

    with rasterio.open(scl_pfad) as src_scl:
        scl = src_scl.read(1)
        scl_shape = src_scl.shape
        scl_crs = src_scl.crs
        scl_transform = src_scl.transform

    scl_valid = np.isin(scl, [4, 5, 6])

    print(f"\nSCL-Maskierung für {datum}")
    print(f"Gültige SCL-Pixel: {scl_valid.sum()}")

    for band in ["B04", "B08", "B11", "B12"]:

        band_pfad = PROCESSED_DIR / f"{datum}_{band}.tif"

        with rasterio.open(band_pfad) as src:

            if (
                src.shape != scl_shape
                or src.crs != scl_crs
                or src.transform != scl_transform
            ):
                raise ValueError(
                    f"Rastergitter stimmen nicht überein: {band}"
                )

            raster = src.read()
            transform = src.transform

        zusaetzlich_maskiert = np.sum((raster[0] != 0) & (~scl_valid))

        raster[0, ~scl_valid] = 0

        zielpfad = PROCESSED_DIR / "masked" / f"{datum}_{band}_masked.tif"

        speichere_raster(zielpfad, raster, transform)

        print(
            f"{band}: {zusaetzlich_maskiert} zusätzliche Pixel maskiert"
        )
        print(f"Gespeichert: {zielpfad}")


def main():

    baender = {
        "B04": 10,
        "B08": 10,
        "B11": 20,
        "B12": 20,
        "SCL": 20
    }

    for datum in ["20180701", "20240709"]:
        for band, aufloesung in baender.items():

            raster, transform, crs = band_ausrichten(
                datum, band, aufloesung
            )

            dateipfad = PROCESSED_DIR / f"{datum}_{band}.tif"

            speichere_raster(dateipfad, raster, transform)

            print(f"Gespeichert: {dateipfad}")

    for datum in ["20180701", "20240709"]:
        maskiere_baender(datum)
    

    for datum in ["20180701", "20240709"]:

        with rasterio.open(PROCESSED_DIR / f"{datum}_SCL.tif") as src:
            scl_valid = np.isin(src.read(1), [4, 5, 6])
            referenz_shape = src.shape
            referenz_crs = src.crs
            referenz_transform = src.transform

        for band in ["B04", "B08", "B11", "B12"]:

            pfad = PROCESSED_DIR / "masked" / f"{datum}_{band}_masked.tif"

            with rasterio.open(pfad) as src:
                daten = src.read(1)

                rastergitter_ok = (
                    src.shape == referenz_shape
                    and src.crs == referenz_crs
                    and src.transform == referenz_transform
                )

                fehlerhafte_pixel = np.sum(
                    (daten != 0) & (~scl_valid)
                )

                print(
                    datum, band,
                    "Rastergitter:", rastergitter_ok,
                    "Maskenfehler:", fehlerhafte_pixel,
                    "NoData:", src.nodata
                )


if __name__ == "__main__":
    main()
