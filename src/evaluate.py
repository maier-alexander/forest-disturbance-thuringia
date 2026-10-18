from pathlib import Path

import numpy as np
import rasterio

PROCESSED_DIR = Path("data/processed")
FOREST_DIR = PROCESSED_DIR / "forest"
DLR_PATH = PROCESSED_DIR / "reference" / "dlr_loss_2018_2024.tif"
INDEX_NAMES = ["NDVI", "NDMI", "NBR"]
THRESHOLDS = np.arange(-0.50, -0.049, 0.025)


def check_grid(src, shape, crs, transform):
    if src.shape != shape or src.crs != crs or src.transform != transform:
        raise ValueError(f"Raster grids do not match: {src.name}")


def show_statistics(values, percentiles):
    if values.size == 0:
        raise ValueError("No valid pixels available for evaluation.")

    print(f"Pixels: {values.size} | Mean: {np.mean(values):.3f} | Median: {np.median(values):.3f}")
    print("Percentiles: " + ", ".join(
        f"P{p}={np.percentile(values, p):.3f}" for p in percentiles
    ))


def analyze_distribution(index_name, values):
    print(f"\n{index_name} | 2018 forest area")
    show_statistics(values, [10, 25, 50, 75, 90])


def compare_dlr(index_name, delta, dlr, valid):
    print(f"\n{index_name} | DLR comparison")

    for label, group in [("DLR loss", 1), ("No DLR loss", 0)]:
        print(label)
        show_statistics(delta[valid & (dlr == group)], [25, 75])


def calculate_metrics(values, reference, threshold):
    prediction = values < threshold
    tp = np.sum(prediction & reference)
    fp = np.sum(prediction & ~reference)
    fn = np.sum(~prediction & reference)
    tn = np.sum(~prediction & ~reference)

    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0

    return precision, recall, f1, tp, fp, fn, tn


def evaluate_thresholds(index_name, delta, dlr, valid):
    rows = np.arange(delta.shape[0])[:, None]
    columns = np.arange(delta.shape[1])[None, :]
    training = (rows // 250 + columns // 250) % 2 == 0
    train_mask = valid & training
    test_mask = valid & ~training

    x_train = delta[train_mask]
    y_train = dlr[train_mask] == 1
    x_test = delta[test_mask]
    y_test = dlr[test_mask] == 1

    if not x_train.size or not x_test.size or not np.any(y_train) or np.all(y_train) or not np.any(y_test) or np.all(y_test):
        raise ValueError(f"Training and test sets must contain both DLR classes: {index_name}")

    best_threshold = None
    best_f1 = -1

    for threshold in THRESHOLDS:
        _, _, f1, _, _, _, _ = calculate_metrics(x_train, y_train, threshold)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

    precision, recall, f1, tp, fp, fn, tn = calculate_metrics(
        x_test, y_test, best_threshold
    )

    print(f"\n{index_name} | Threshold evaluation")
    print(f"Train: {x_train.size} pixels | Test: {x_test.size} pixels")
    print(f"Selected threshold: {best_threshold:.3f} | Training F1: {best_f1:.3f}")
    print(f"Test precision: {precision:.3f} | Recall: {recall:.3f} | F1: {f1:.3f}")
    print(f"Test confusion matrix: TP={tp}, FP={fp}, FN={fn}, TN={tn}")

    return best_threshold


def classify_forest_loss(delta, profile, threshold):
    valid = np.isfinite(delta)
    classification = np.full(delta.shape, 255, dtype=np.uint8)
    classification[valid] = (delta[valid] < threshold).astype(np.uint8)

    profile.update(dtype="uint8", count=1, nodata=255)
    output_path = PROCESSED_DIR / "classification" / "forest_loss_NBR.tif"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(classification, 1)

    count = np.sum(classification == 1)
    print(f"\nNBR classification (threshold {threshold:.3f}): {count} loss pixels, {count / 100:.2f} ha")
    return classification


def main():
    with rasterio.open(DLR_PATH) as src_dlr:
        dlr = src_dlr.read(1)
        shape = src_dlr.shape
        crs = src_dlr.crs
        transform = src_dlr.transform

    classes = np.unique(dlr)
    if not np.all(np.isin(classes, [0, 1, 255])) or not np.all(np.isin([0, 1], classes)):
        raise ValueError("DLR reference must contain classes 0 and 1, and optionally 255.")

    for index_name in INDEX_NAMES:
        path = FOREST_DIR / f"delta_{index_name}_forest.tif"

        with rasterio.open(path) as src:
            check_grid(src, shape, crs, transform)
            delta = src.read(1)
            profile = src.profile.copy()

        valid = np.isfinite(delta) & np.isin(dlr, [0, 1])
        analyze_distribution(index_name, delta[np.isfinite(delta)])

        if index_name in ["NDMI", "NBR"]:
            compare_dlr(index_name, delta, dlr, valid)
            threshold = evaluate_thresholds(index_name, delta, dlr, valid)

            if index_name == "NBR":
                classification = classify_forest_loss(delta, profile, threshold)
                comparable = np.isin(classification, [0, 1]) & np.isin(dlr, [0, 1])
                own_loss = np.sum((classification == 1) & comparable)
                dlr_loss = np.sum((dlr == 1) & comparable)
                print(f"Comparable area: {np.sum(comparable) / 100:.2f} ha")
                print(f"Own loss: {own_loss / 100:.2f} ha | DLR loss: {dlr_loss / 100:.2f} ha")


if __name__ == "__main__":
    main()
