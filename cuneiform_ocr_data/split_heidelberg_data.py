from pathlib import Path

from cuneiform_ocr_data.prepare_and_split_data import prepare_data
from cuneiform_ocr_data.prepare_data import HEIDELBERG_VAL_SET

if __name__ == "__main__":
    data_path = Path(
        "/data/processed-data/heidelberg/heidelberg-merged-extracted-cleaned-2"
    )
    output_path = Path(
        "/home/yunus/PycharmProjects/cuneiform-ocr-data/data/processed-data/heidelberg-split"
    )
    prepare_data(data_path, output_path, HEIDELBERG_VAL_SET, 1)
