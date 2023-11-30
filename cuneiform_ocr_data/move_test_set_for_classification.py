import random
import shutil
from pathlib import Path

from cuneiform_ocr_data.utils import create_directory, is_valid_data

random.seed(0)


def parse_filename(elem):
    elem = elem.split(".jpg")[0]
    elem = elem.split("-")
    if len(elem[0]) <= 2:     #for Sp-III-947.jpg
        elem = "-".join(elem)
        return elem
    if len(elem) > 1:
        elem = "-".join(elem[:-1])
    else:
        elem = elem[0]
    print(elem)
    return elem


if __name__ == "__main__":
    all_data = "data/processed-data/ebl+heidelberg"
    shutil.copytree(all_data, all_data + "-train")
    all_data = Path(all_data + "-train")
    destination = Path(
        "data/processed-data/ebl+heidelberg-test"
    )
    create_directory(destination / "annotations", overwrite=True)
    create_directory(destination / "imgs", overwrite=True)
    is_valid_data(all_data)
    # read newline seperated file into a list
    TEST_IMGS_PATH = Path(
        "data/processed-data/detection/test/test_imgs.txt"
    )
    with open(TEST_IMGS_PATH) as f:
        test_set = f.read().splitlines()
    # Only keep file stems which means complete image is excluded from train set for classification (could be optimized in future to only exclude the ecxtracted images not the complete images)

    test_set = list(set([parse_filename(elem) for elem in test_set]))

    for file in test_set:
        shutil.move(all_data / f"imgs/{file}.jpg", destination / "imgs")
        shutil.move(
            all_data / f"annotations/gt_{file}.txt", destination / "annotations"
        )
