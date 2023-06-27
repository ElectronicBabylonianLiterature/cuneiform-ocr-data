# Copyright (c) OpenMMLab. All rights reserved.
import os
import random
import shutil
from pathlib import Path
from typing import Sequence, Tuple, List

from cuneiform_ocr_data.validate_data import is_valid_data


def split_data(
    split: Tuple[float, ...],
    data: Sequence[Path],
) -> List[Sequence[Path]]:
    size = len(data)
    result = []
    start = 0
    for spli in split:
        end = int(spli * size)
        result.append(data[start:end])
        start = end
    result.append(data[start:])
    return result


def copy_image_and_corresponding_annotation(
    images_path: Sequence[Path],
    output_folder_annotations: Path,
    output_folder_imgs: Path,
    annotations_path_copy_from: Path,
):
    for file in images_path:
        shutil.copyfile(file, output_folder_imgs / file.name)
        annotation_path = next(annotations_path_copy_from.glob(f"gt_{file.stem}.txt"))
        shutil.copyfile(
            annotation_path, output_folder_annotations / annotation_path.name
        )


def prepare_data(
    data_path: Path,
    output_path: Path,
    split,
    random_seed,
) -> None:
    # split is a tuple and returns training and test if one number is given (0.5,)
    # and training, val, test if two numbers are given (0.5, 0.75)
    random.seed(random_seed)
    images_path = data_path / "imgs"
    annotations_path = data_path / "annotations"
    is_valid_data(data_path)
    data = sorted(images_path.iterdir(), key=lambda file: file.name)
    random.shuffle(data)

    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    def create_folders(anno, imgs, data):
        anns = output_path / anno
        imgs = output_path / imgs
        anns.mkdir(parents=True)
        imgs.mkdir(parents=True)
        copy_image_and_corresponding_annotation(data, anns, imgs, annotations_path)

    annotations = Path("annotations")
    imgs = Path("textdet_imgs")

    if isinstance(split[0], float):
        splits = split_data(split, data)

        print(len(data))
        print("Training :", len(splits[0]))
        print("Split 1:", len(splits[0]) + len(splits[1]))
        if len(splits) == 3:
            print("Split 2:", len(splits[0]) + len(splits[1]) + len(splits[2]))
    else:
        val_imgs = []

        for elem in split:
            # find all images in images_path where elem is in name
            val_imgs.extend(list(images_path.glob(f"*{elem}*")))

        train_imgs = list(set(list(images_path.iterdir())) - set(val_imgs))

        create_folders(annotations / "train", imgs / "train", train_imgs)

        create_folders(annotations / "test", imgs / "test", val_imgs)
        return None

    create_folders(annotations / "train", imgs / "train", splits[0])

    if len(splits) == 2:
        create_folders(annotations / "test", imgs / "test", splits[1])

    if len(splits) == 3:
        create_folders(annotations / "validation", imgs / "validation", splits[1])
        create_folders(annotations / "test", imgs / "test", splits[2])
