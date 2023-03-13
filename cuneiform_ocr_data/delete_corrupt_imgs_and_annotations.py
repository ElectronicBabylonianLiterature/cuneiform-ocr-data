from pathlib import Path
from typing import Sequence
from typing import Union


def delete_corrupt_images_and_annotations(
    data_path: Path,
    delete_txt: Union[Sequence[str], Path],
    image_directory_name=Path("imgs"),
    annotations_directory_name=Path("annotations"),
) -> None:
    if isinstance(delete_txt, Path):
        with open(delete_txt, "r") as f:
            delete_txt = f.read().split()

    for file in delete_txt:
        img_filename = Path(file + ".jpg")
        gt = next(
            Path(data_path / annotations_directory_name).glob(f"gt_{file}.txt"), None
        )
        (data_path / image_directory_name / img_filename).unlink(missing_ok=True)
        if gt:
            gt and gt.unlink(missing_ok=True)
        else:
            print(f"{file} not found in annotations")
