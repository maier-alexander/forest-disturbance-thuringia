
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from rasterio.plot import plotting_extent

FOREST_DIR = Path("data/processed/forest")
OUTPUT_DIR = Path("outputs/maps")


def visualize_delta():
    fig, axes = plt.subplots(1, 3, figsize=(16, 6), layout="constrained")

    for ax, index_name in zip(axes, ["NDVI", "NDMI", "NBR"]):
        path = FOREST_DIR / f"delta_{index_name}_forest.tif"

        with rasterio.open(path) as src:
            delta = src.read(1)
            extent = plotting_extent(src)

        delta = np.ma.masked_invalid(delta)
        image = ax.imshow(
            delta,
            cmap="RdYlGn",
            vmin=-0.5,
            vmax=0.5,
            extent=extent,
            interpolation="nearest"
        )
        ax.set_title(f"Δ{index_name} (2024 − 2018)")
        ax.set_xlabel("UTM Easting (m)")
        ax.set_ylabel("UTM Northing (m)")
        ax.set_aspect("equal")

    fig.colorbar(
        image,
        ax=axes,
        orientation="horizontal",
        shrink=0.7,
        label="Index change (2024 − 2018)"
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "delta_indices_forest.png"
    fig.savefig(output_path, dpi=250)
    plt.close(fig)
    print(f"Saved: {output_path}")


def visualize_comparison():
    classification_path = Path("data/processed/classification/forest_loss_NBR.tif")
    dlr_path = Path("data/processed/reference/dlr_loss_2018_2024.tif")

    with (
        rasterio.open(classification_path) as src_classification,
        rasterio.open(dlr_path) as src_dlr
    ):
        if (
            src_classification.shape != src_dlr.shape
            or src_classification.crs != src_dlr.crs
            or src_classification.transform != src_dlr.transform
        ):
            raise ValueError("Raster grids do not match.")

        classification = src_classification.read(1)
        dlr = src_dlr.read(1)
        extent = plotting_extent(src_classification)
        profile = src_classification.profile.copy()

    if not np.all(np.isin(np.unique(classification), [0, 1, 255])) or not np.all(np.isin(np.unique(dlr), [0, 1, 255])):
        raise ValueError("Unexpected classification or DLR reference values.")

    valid = np.isin(classification, [0, 1]) & np.isin(dlr, [0, 1])
    if not np.any(valid):
        raise ValueError("No comparable pixels found.")

    comparison = np.full(classification.shape, 255, dtype=np.uint8)
    comparison[valid] = 0
    comparison[valid & (classification == 1) & (dlr == 1)] = 1
    comparison[valid & (classification == 1) & (dlr == 0)] = 2
    comparison[valid & (classification == 0) & (dlr == 1)] = 3

    comparison_dir = Path("data/processed/comparison")
    comparison_dir.mkdir(parents=True, exist_ok=True)

    profile.update(
        driver="GTiff",
        dtype="uint8",
        count=1,
        nodata=255,
        compress="deflate"
    )

    for filename, raster in [
        ("own_loss_comparable.tif", classification),
        ("dlr_loss_comparable.tif", dlr),
        ("spatial_agreement.tif", comparison)
    ]:
        output_raster = np.full(raster.shape, 255, dtype=np.uint8)
        output_raster[valid] = raster[valid]

        output_path = comparison_dir / filename

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(output_raster, 1)

        print(f"Saved: {output_path}")

    binary_colors = ListedColormap(["#D3D3D3", "#D13A36"])
    comparison_colors = ListedColormap([
        "#D3D3D3", "#27945D", "#F0A13B", "#4585CB"
    ])
    binary_colors.set_bad("white")
    comparison_colors.set_bad("white")

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.subplots_adjust(bottom=0.22, wspace=0.28)

    data = [classification, dlr, comparison]
    titles = [
        "Own classification (ΔNBR)",
        "DLR canopy cover loss",
        "Spatial agreement"
    ]
    colormaps = [binary_colors, binary_colors, comparison_colors]
    max_values = [1, 1, 3]

    for ax, raster, title, colors, maximum in zip(
        axes, data, titles, colormaps, max_values
    ):
        masked = np.ma.masked_where(~valid, raster)
        ax.imshow(
            masked,
            cmap=colors,
            vmin=0,
            vmax=maximum,
            extent=extent,
            interpolation="nearest"
        )
        ax.set_title(title)
        ax.set_xlabel("UTM Easting (m)")
        ax.set_ylabel("UTM Northing (m)")
        ax.set_aspect("equal")

    legend = [
        Patch(color="#D3D3D3", label="Both: no loss"),
        Patch(color="#27945D", label="Both: loss"),
        Patch(color="#F0A13B", label="Own classification only"),
        Patch(color="#4585CB", label="DLR only"),
        Patch(facecolor="white", edgecolor="gray", label="NoData")
    ]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, 0.02), ncol=5)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "forest_loss_comparison.png"
    fig.savefig(output_path, dpi=250, bbox_inches="tight")
    plt.close(fig)

    print(f"Comparable pixels: {np.sum(valid)}")
    print(f"Both loss: {np.sum(comparison == 1)} | Own only: {np.sum(comparison == 2)} | DLR only: {np.sum(comparison == 3)}")
    print(f"Both no loss: {np.sum(comparison == 0)}")
    print(f"Saved: {output_path}")


def main():
    visualize_delta()
    visualize_comparison()


if __name__ == "__main__":
    main()
