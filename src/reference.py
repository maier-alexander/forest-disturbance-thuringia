from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject

PROCESSED_DIR = Path("data/processed")
DLR_PATH = Path("data/raw/reference/dlr/FCCL_DE_P1M.tif")


def create_dlr_reference():
    reference_path = PROCESSED_DIR / "forest" / "forest_mask_2018.tif"

    with rasterio.open(reference_path) as ref:
        target_shape = ref.shape
        target_transform = ref.transform
        target_crs = ref.crs
        profile = ref.profile.copy()
        forest = ref.read(1) == 1

    dlr = np.full(target_shape, np.nan, dtype=np.float32)

    with rasterio.open(DLR_PATH) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=dlr,
            src_nodata=src.nodata,
            dst_nodata=np.nan,
            dst_transform=target_transform,
            dst_crs=target_crs,
            resampling=Resampling.nearest
        )

    loss = (dlr >= 12) & (dlr <= 82)
    no_loss = (dlr == 0) | ((dlr >= 84) & (dlr <= 98))
    reference = np.full(target_shape, 255, dtype=np.uint8)
    reference[forest & no_loss] = 0
    reference[forest & loss] = 1

    if not np.any(reference == 1) or not np.any(reference == 0):
        raise ValueError("DLR reference must contain both loss and no-loss pixels.")

    profile.update(dtype="uint8", nodata=255, compress="deflate")
    output_path = PROCESSED_DIR / "reference" / "dlr_loss_2018_2024.tif"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(reference, 1)

    loss_count = np.sum(reference == 1)
    no_loss_count = np.sum(reference == 0)
    print(f"DLR reference: {loss_count} loss pixels, {no_loss_count} no-loss pixels")
    print(f"DLR loss area (all reference-valid pixels): {loss_count / 100:.2f} ha")
    return output_path


def main():
    create_dlr_reference()


if __name__ == "__main__":
    main()
