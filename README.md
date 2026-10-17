# Sentinel-2 Forest Disturbance Mapping in Thuringia

## Project Overview

This project investigates forest disturbance in a selected area of the Thuringian Forest using Sentinel-2 satellite imagery.

The goal is to develop a reproducible Python workflow for detecting and analysing changes in forest vegetation between two time periods and comparing the results with an existing DLR forest canopy loss product.

## Research Question

Where have significant forest canopy changes occurred in a selected area of southern Thuringia between two comparable Sentinel-2 observation periods, and how do these changes spatially agree with the DLR Forest Canopy Cover Loss product?

## Study Area

- Location: southern Thuringian Forest, around Steinach, Lauscha and Neuhaus am Rennweg, north of Sonneberg
- Area of interest (AOI): approximately 25 km × 25 km
- Sentinel-2 tiles: T32UPA and T32UPB

The area was selected for its extensive forest cover and visible forest canopy changes between the observation periods.

## Data

| Dataset | Selection | Purpose |
| Sentinel-2 Level-2A | 01 July 2018; tiles T32UPA and T32UPB | Reference observation |
| Sentinel-2 Level-2A | 09 July 2024; tiles T32UPA and T32UPB | Comparison observation |
| Thünen Institute, *Bestockte Holzbodenkarte 2018* | 2018 forest extent | Forest mask |
| DLR, *Forest Canopy Cover Loss Germany, Monthly* (`FCCL_DE_P1M.tif`) | Monthly canopy-loss product, 10 m | Comparison with independently produced satellite-based results |

Required Sentinel-2 components: B04 (red), B08 (NIR), B11 (SWIR1), B12 (SWIR2) and the Scene Classification Layer (SCL). Their presence in the downloaded products has not yet been verified.

Sources: [Thünen forest mask](https://atlas.thuenen.de/layers/geonode:fnews_holzbodenmaske_2018_32632) · [DLR FCCL dataset](https://geoservice.dlr.de/web/datasets/fccl)

Raw datasets belong in `data/raw/` and are excluded from Git. Product identifiers and selection metadata are documented separately.

## Planned Workflow

1. Inspect and prepare the satellite products; mask clouds and shadows, align rasters and mosaic the two tiles.
2. Calculate NDVI, NDMI and NBR for both observation periods and analyse changes.
3. Restrict the analysis to the 2018 forest mask and compare detected changes with the DLR FCCL product.
4. Create maps and summary statistics, and discuss uncertainty and limitations.

The DLR product is a satellite-based comparison dataset, not independent ground truth. Its forest definition also uses the 2018 Thünen forest mask.

## Project Status

Initial planning and data acquisition completed. Next: verify the downloaded files and AOI geometry, publish the repository on GitHub, and begin raster exploration in Python.
