# Sentinel-2 Forest Disturbance Mapping in Thuringia

This project examines changes in forest vegetation in southern Thuringia, Germany, between July 2018 and July 2024 using Sentinel-2 satellite imagery. A Python-based workflow was developed to calculate spectral vegetation indices, identify potential forest canopy loss and compare the results with the German Aerospace Center's (DLR) Forest Canopy Cover Loss dataset.

## Research Question

Where have significant forest canopy changes occurred in a selected area of southern Thuringia between two comparable Sentinel-2 observation periods, and how do these changes spatially agree with the DLR Forest Canopy Cover Loss product?

## Study Area and Data

The study area covers approximately 25 × 25 km in the southern Thuringian Forest, around Steinach, Lauscha and Neuhaus am Rennweg. The region was selected because of its extensive forest cover and substantial forest disturbances in recent years.

| Dataset | Description |
|---|---|
| Sentinel-2 Level-2A | 1 July 2018 and 9 July 2024 |
| Sentinel-2 tiles | T32UPA and T32UPB |
| Spectral bands | B04 (Red), B08 (NIR), B11 (SWIR1), B12 (SWIR2) |
| Scene Classification Layer | Cloud, shadow and invalid-pixel masking |
| Thünen Institute | Forest mask representing forest areas in 2018 |
| DLR Forest Canopy Cover Loss | Monthly canopy-loss product used for comparison |

All raster processing was carried out in WGS 84 / UTM zone 32N (EPSG:32632) at a spatial resolution of 10 m.

## Methodology

The analysis consists of six processing steps:

1. **Preprocessing:** Sentinel-2 tiles were mosaicked, clipped to the study area and aligned to a common 10 m raster grid. SWIR bands were resampled using bilinear interpolation, while the categorical SCL was resampled using nearest neighbour. SCL classes 4, 5 and 6 were retained.

2. **Spectral indices:** NDVI, NDMI and NBR were calculated for both dates using surface reflectance values, accounting for the Level-2A quantification factor and band offsets.

3. **Change detection:** Changes were calculated as `Index_2024 - Index_2018`. Only pixels valid at both observation dates were included, and the analysis was restricted to forest areas identified by the 2018 Thünen forest mask.

4. **DLR reference:** The DLR Forest Canopy Cover Loss dataset was aligned to the study grid. Detected losses from August 2018 to June 2024 were included. July 2024 was excluded because the monthly product does not distinguish losses occurring before or after the second Sentinel-2 acquisition on 9 July.

5. **Classification and evaluation:** Thresholds for ΔNDMI and ΔNBR were selected by maximising the F1-score on spatially separated training blocks. Performance was assessed on held-out blocks using precision, recall and F1-score.

6. **Mapping:** Change maps and classification comparisons were generated in Python. Final cartographic layouts were prepared in ArcGIS Pro.

## Results

All three indices showed negative mean changes across the valid 2018 forest areas.

| Index | Mean change |
|---|---:|
| ΔNDVI | −0.106 |
| ΔNDMI | −0.179 |
| ΔNBR | −0.171 |

ΔNBR achieved slightly better agreement with the DLR reference than ΔNDMI and was therefore used for the final threshold-based classification.

| Metric | ΔNDMI | ΔNBR |
|---|---:|---:|
| Selected threshold | −0.150 | −0.125 |
| Test precision | 0.670 | 0.676 |
| Test recall | 0.694 | 0.732 |
| Test F1-score | 0.682 | 0.703 |

On the common valid comparison area of **42,948.42 ha**, the ΔNBR classification identified **21,969.34 ha** of potential canopy loss, compared with **19,828.01 ha** in the DLR reference. Both methods identified the same 14,784.62 ha as loss.

The spatial comparison shows considerable agreement, but also differences in several forest areas. These differences are particularly relevant when interpreting results from only two satellite observations.

## Maps

**Spectral changes in forest vegetation (2018–2024)**

![Spectral changes in forest vegetation](outputs/maps/spectral_changes_final.png)

Changes in NDVI, NDMI and NBR across forest areas present in 2018. Negative values indicate a decrease in the respective spectral index.

**Forest canopy loss – comparison with DLR**

![Forest canopy loss comparison](outputs/maps/forest_loss_comparison_final.png)

Comparison of the ΔNBR-based classification, the DLR canopy-loss reference and their spatial agreement. Both classifications are displayed on the same valid comparison area.

## Project Structure

```text
forest-disturbance-thuringia/
├── data/
│   ├── raw/
│   │   ├── sentinel2/
│   │   ├── study_area/
│   │   └── reference/
│   └── processed/
├── src/
│   ├── preprocess.py
│   ├── indices.py
│   ├── change.py
│   ├── reference.py
│   ├── evaluate.py
│   └── visualize.py
├── outputs/
│   └── maps/
├── main.py
├── requirements.txt
├── learning_log.md
└── README.md
```

## Running the Project

The workflow uses Python, NumPy, Rasterio, GeoPandas and Matplotlib. Required package versions are listed in `requirements.txt`.

Install the dependencies from the project root:

```bash
python -m pip install -r requirements.txt
```

Run the complete pipeline:

```bash
python main.py
```

Individual processing steps can also be executed separately, for example:

```bash
python src/indices.py
```

The workflow expects the original satellite and reference datasets in `data/raw/`. These files are not included in the repository due to their size. Intermediate GeoTIFFs are written to `data/processed/`, while the generated maps are saved in `outputs/maps/`.

Reproducing the analysis requires obtaining the source datasets and placing the necessary files in the corresponding directories.

## Limitations

The analysis uses two individual Sentinel-2 acquisitions rather than a continuous time series. Changes occurring between the observations, including temporary canopy loss followed by vegetation recovery, may therefore remain undetected.

Changes in spectral indices do not necessarily indicate canopy loss. Vegetation moisture, seasonal conditions and other surface changes can influence the results.

The DLR dataset is used as a satellite-based comparison reference, not as independent ground truth. The reported evaluation metrics describe agreement with this product rather than independently validated classification accuracy.

Although training and test pixels were separated into spatial blocks, neighbouring blocks may still exhibit spatial autocorrelation.

## Data Sources

- [Copernicus Data Space Ecosystem – Sentinel-2](https://dataspace.copernicus.eu/)
- [Thünen Institute – Forest Mask 2018](https://atlas.thuenen.de/layers/geonode:fnews_holzbodenmaske_2018_32632)
- [DLR – Forest Canopy Cover Loss](https://geoservice.dlr.de/web/datasets/fccl)

---

**Author:** Alexander Maier

B.Sc. Geography, Friedrich Schiller University Jena