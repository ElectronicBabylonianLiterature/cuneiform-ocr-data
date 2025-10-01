import os
import random
import shutil
from pathlib import Path
import json 

from cuneiform_ocr_data.utils import create_directory, is_valid_data

random.seed(0)


if __name__ == "__main__":
    data_base_dir = "data/processed-data/ebl/ebl-detection-extracted-17-04-25"
    all_data = Path(os.environ.get("EBL_DETECTION_EXTRACTED_PATH", data_base_dir))
    DELETE_EMPTY_IMGS = os.environ.get("DELETE_EMPTY_IMGS", "") == "yes"
    if DELETE_EMPTY_IMGS:
        is_valid_data(all_data, delete_empty_imgs=True)
    else:
        is_valid_data(all_data)
    # copy data to new folder
    path = all_data / "train"
    shutil.copytree(all_data, path)

    test_path = Path(os.environ.get("TEST_PATH", "test"))
    create_directory(test_path / "imgs", overwrite=True)
    create_directory(test_path / "annotations", overwrite=True)
    test_imgs = []
    test_gts = []
    TEST_SET_SIZE = os.environ.get("TEST_SET_SIZE", 50)
    TEST_SET_SIZE = int(TEST_SET_SIZE)
    all_files = list((path / "imgs").iterdir())
    test_set = random.sample(all_files, TEST_SET_SIZE)

    for file in test_set:
        test_imgs.append(file.name)
        shutil.move(file, test_path / "imgs")
        shutil.move(path / f"annotations/gt_{file.stem}.txt", test_path / "annotations")

    # create txt file in test folder with all test images
    with open(test_path / "test_imgs.txt", "w") as f:
        f.write("\n".join(test_imgs))

    is_valid_data(path)
    is_valid_data(test_path)

