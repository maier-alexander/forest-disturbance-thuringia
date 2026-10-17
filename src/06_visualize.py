
from pathlib import Path
import rasterio
from rasterio.plot import plotting_extent
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch


CHANGE_DIR = Path("data/processed/forest")
OUTPUT_DIR = Path("outputs/maps")

def visualisiere_delta():

    fig, axes = plt.subplots(1, 3, figsize=(16, 6), layout="constrained")

    for ax, index_name in zip(axes, ["NDVI", "NDMI", "NBR"]):

        pfad = CHANGE_DIR / f"delta_{index_name}_forest.tif"

        with rasterio.open(pfad) as src:
            delta = src.read(1)
            extent = plotting_extent(src)

        delta = np.ma.masked_invalid(delta)

        bild = ax.imshow(
            delta,
            cmap="RdYlGn",
            vmin=-0.5,
            vmax=0.5,
            extent=extent,
            interpolation="nearest"
        )

        ax.set_title(f"Δ{index_name} (2024 − 2018)")
        ax.set_xlabel("UTM Ostwert (m)")
        ax.set_ylabel("UTM Nordwert (m)")
        ax.set_aspect("equal")

    fig.colorbar(
        bild,
        ax=axes,
        orientation="horizontal",
        shrink=0.7,
        label="Indexveränderung (2024 − 2018)"
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    zielpfad = OUTPUT_DIR / "delta_indices_forest.png"

    fig.savefig(zielpfad, dpi=250)
    plt.show()

    print(f"Gespeichert: {zielpfad}")


def visualisiere_vergleich():

    klassifikation_pfad = Path("data/processed/classification/forest_loss_NBR.tif")
    dlr_pfad = Path("data/processed/reference/dlr_loss_2018_2024.tif")

    with (
        rasterio.open(klassifikation_pfad) as src_klassifikation,
        rasterio.open(dlr_pfad) as src_dlr
    ):

        if (
            src_klassifikation.shape != src_dlr.shape
            or src_klassifikation.crs != src_dlr.crs
            or src_klassifikation.transform != src_dlr.transform
        ):
            raise ValueError("Rastergitter stimmen nicht überein.")

        klassifikation = src_klassifikation.read(1)
        dlr = src_dlr.read(1)
        extent = plotting_extent(src_klassifikation)

    valid = np.isin(klassifikation, [0, 1]) & np.isin(dlr, [0, 1])

    vergleich = np.full(klassifikation.shape, 255, dtype=np.uint8)

    vergleich[valid] = 0
    vergleich[valid & (klassifikation == 1) & (dlr == 1)] = 1
    vergleich[valid & (klassifikation == 1) & (dlr == 0)] = 2
    vergleich[valid & (klassifikation == 0) & (dlr == 1)] = 3

    farben_binaer = ListedColormap(["#D3D3D3", "#D13A36"])
    farben_vergleich = ListedColormap([
        "#D3D3D3", "#27945D", "#F0A13B", "#4585CB"
    ])

    farben_binaer.set_bad("white")
    farben_vergleich.set_bad("white")

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.subplots_adjust(bottom=0.22, wspace=0.28)

    daten = [klassifikation, dlr, vergleich]
    titel = [
        "Eigene Klassifikation (ΔNBR)",
        "DLR-Kronendachverlust",
        "Räumliche Übereinstimmung"
    ]
    farbskalen = [farben_binaer, farben_binaer, farben_vergleich]
    maximalwerte = [1, 1, 3]

    for ax, raster, name, farben, maximum in zip(
        axes, daten, titel, farbskalen, maximalwerte
    ):

        raster_maskiert = np.ma.masked_where(~valid, raster)

        ax.imshow(
            raster_maskiert,
            cmap=farben,
            vmin=0,
            vmax=maximum,
            extent=extent,
            interpolation="nearest"
        )

        ax.set_title(name)
        ax.set_xlabel("UTM Ostwert (m)")
        ax.set_ylabel("UTM Nordwert (m)")
        ax.set_aspect("equal")

    legende = [
        Patch(color="#D3D3D3", label="Beide: kein Verlust"),
        Patch(color="#27945D", label="Beide: Verlust"),
        Patch(color="#F0A13B", label="Nur eigene Klassifikation"),
        Patch(color="#4585CB", label="Nur DLR"),
        Patch(facecolor="white", edgecolor="gray", label="NoData")
    ]

    fig.legend(
        handles=legende,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.02),
        ncol=5
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    zielpfad = OUTPUT_DIR / "forest_loss_comparison.png"

    fig.savefig(zielpfad, dpi=250, bbox_inches="tight")
    plt.show()

    print(f"\nGemeinsam gültige Pixel: {np.sum(valid)}")
    print(f"Beide Verlust: {np.sum(vergleich == 1)}")
    print(f"Nur eigene Klassifikation: {np.sum(vergleich == 2)}")
    print(f"Nur DLR: {np.sum(vergleich == 3)}")
    print(f"Beide kein Verlust: {np.sum(vergleich == 0)}")
    print(f"Gespeichert: {zielpfad}")


def main():

    visualisiere_delta()
    visualisiere_vergleich()


if __name__ == "__main__":
    main()
