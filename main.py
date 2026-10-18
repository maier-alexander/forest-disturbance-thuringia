from src import change, evaluate, indices, preprocess, reference, visualize


def main():
    steps = [
        ("Sentinel-2 preprocessing", preprocess.main),
        ("Vegetation indices", indices.main),
        ("Change detection and forest mask", change.main),
        ("DLR reference", reference.main),
        ("Evaluation and classification", evaluate.main),
        ("Maps", visualize.main)
    ]

    for number, (name, run) in enumerate(steps, start=1):
        print(f"\n{number}/{len(steps)} {name}")
        run()

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
