import random
import shutil
from pathlib import Path

from cuneiform_ocr_data.utils import create_directory, is_valid_data

random.seed(0)


if __name__ == "__main__":
    all_data = "data/processed-data/ebl+heidelberg"
    shutil.copytree(all_data, all_data + "-train")
    all_data = Path(all_data + "-train")
    destination = Path("data/processed-data/ebl+heidelberg-test")
    create_directory(destination / "annotations", overwrite=True)
    create_directory(destination / "imgs", overwrite=True)
    is_valid_data(all_data)
    # read newline seperated file into a list
    TEST_IMGS_PATH = Path("data/processed-data/ebl/test/test_imgs.txt")
    with open(TEST_IMGS_PATH) as f:
        test_set = f.read().splitlines()
    # Only keep file stems which means complete image is excluded from train set for classification (could be optimized in future to only exclude the ecxtracted images not the complete images)
    test_set = list(set([elem.split(".jpg")[0].split("-")[0] for elem in test_set]))

    for file in test_set:
        shutil.move(all_data / f"imgs/{file}.jpg", destination / "imgs")
        shutil.move(
            all_data / f"annotations/gt_{file}.txt", destination / "annotations"
        )
