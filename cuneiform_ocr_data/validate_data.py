from pathlib import Path


def is_valid_file_size(path: Path, raise_error: bool) -> bool:
    if path.stat().st_size == 0:
        if raise_error:
            raise UserWarning(f"Image '{path.stem}' has size 0 bytes. Please check")
        else:
            return False
    else:
        return True


def is_valid_data(
    data_path: Path, images_folder="imgs", annotations_folder="annotations"
) -> bool:
    images_folder = data_path / images_folder
    annotations_folder = data_path / annotations_folder

    if not len(list(images_folder.iterdir())) == len(
        list(annotations_folder.iterdir())
    ):
        print("Number of Images doesn't match number of annotations")

    for image_file in images_folder.iterdir():
        is_valid_file_size(image_file, True)
        annotation = next(annotations_folder.glob(f"*{image_file.stem}*"), None)
        if not annotation:
            raise FileNotFoundError(
                f"{image_file.name} not found in {annotations_folder.name}"
            )

    for annotation in annotations_folder.iterdir():
        is_valid_file_size(annotation, True)
        annotation_id = annotation.stem.split("gt_")[1]
        image = next(images_folder.glob(f"*{annotation_id}*"), None)
        if not image:
            raise FileNotFoundError(f"{annotation_id} not found in {images_folder}")
    print("Looks good")
    return True


if __name__ == "__main__":
    is_valid_data(Path("../data/processed-data/total"))
