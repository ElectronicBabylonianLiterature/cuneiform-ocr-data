import os
import shutil
from pathlib import Path
from typing import Union, Sequence

import mmcv

mmcv.use_backend("pillow")
from PIL import Image


def create_directory(path: Union[str, Path], overwrite: bool = False) -> None:
    if overwrite:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
    else:
        if os.path.exists(path):
            raise FileExistsError(f"Directory {path} already exists")
        else:
            os.makedirs(path)


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


def _validate_img(file):
    try:
        img = Image.open(file)
        if mmcv.imread(file) is None:
            print(f"Could not read {file}")
        k = mmcv.imfrombytes(open(file, "rb").read())
        if k is None:
            print(f"Could not read {file}")
        img.verify()
        img.close()
    except (IOError, SyntaxError):
        print("Bad file:", file)
        os.remove(file)


def validate_imgs(imgs_path: Path):
    for dir in imgs_path.iterdir():
        if dir.is_dir():
            for sign_dir in dir.iterdir():
                for dir in sign_dir.iterdir():
                    for file in dir.iterdir():
                        _validate_img(file)


def remove_duplicate(path):
    """
    Read all files in path and delete duplicate lines
    """
    for file in path.iterdir():
        lines = open(file).readlines()
        lines_unique = list(set(lines))
        if len(lines) != len(lines_unique):
            print(f"File {file} has duplicate lines")
            with open(file, "w") as f:
                f.writelines(lines_unique)
