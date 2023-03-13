from ast import literal_eval
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import numpy as np
import pandas as pd
from PIL.Image import Image

from cuneiform_sign_classification.preprocessing import build_mzl_dict
from cuneiform_sign_detection.bounding_boxes import BoundingBoxesContainer, BoundingBox
from cuneiform_ocr_data.utils import (
    create_directory,
)


def process(
    mzl_dict, save_data_path: Path, annotations_df: pd.DataFrame, download: bool = False
) -> None:
    """
    bbox format is [xmin, ymin, xmax, ymax]
    """

    annotations_path = save_data_path / "annotations"
    create_directory(save_data_path, overwrite=True)
    create_directory(annotations_path)

    annotations_df.bbox = annotations_df.bbox.apply(literal_eval).apply(np.array)

    cdlis = set(annotations_df.tablet_CDLI)
    print("Number of images: ", len(cdlis), "\n")
    for cdli in cdlis:
        cdli_annotations = annotations_df[annotations_df.tablet_CDLI == cdli]
        bboxes = cdli_annotations[["bbox", "mzl_label"]].to_numpy()
        bboxes_updated = []
        for bbox, sign in bboxes:
            sign = mzl_dict[str(sign)]
            bboxes_updated.append((bbox, sign))

        bounding_boxes = BoundingBoxesContainer(
            cdli,
            [
                BoundingBox.from_two_vertices(vertices, sign)
                for vertices, sign in bboxes_updated
            ],
        )

        bounding_boxes.create_ground_truth_txt(annotations_path)

        if download:
            image_path = save_data_path / "imgs"
            create_directory(image_path)
            failed_downloads = []
            download_path = f"https://cdli.ucla.edu/dl/photo/{cdli}.jpg"
            if "VAT" not in cdli:  # VAT images downloaded not download from cdli
                try:
                    im = Image.open(urlopen(download_path))
                    im.save(f"{image_path}/{cdli}.jpg")
                except HTTPError:
                    failed_downloads.append(cdli)
                    print(f"Failed: {cdli}")
                    continue
            print(f"Success: {cdli}")

            print("---------------Failed Downloads-------------------------")
            print("\n".join(failed_downloads))


if __name__ == "__main__":
    """
    Images fetched from cdli website: https://cdli.ucla.edu/dl/photo/{cdli_number}.jpg"
    VAT images have to be downloaded manually from: https://cunei.iwr.uni-heidelberg.de/cuneiformbrowser/model_weights/VAT_train_images.zip
    and manually copied to imgs folder after running this code
    Link from https://github.com/CompVis/cuneiform-sign-detection-dataset
    """
    save_data_path = Path("temp") / "heidelberg"
    train_bbox_annotations = pd.read_csv(
        "../../data/raw-data/heidelberg/annotations_csv/bbox_annotations_train_full.csv"
    )
    full_df = train_bbox_annotations.append(
        pd.read_csv(
            "../../data/raw-data/heidelberg/annotations_csv/bbox_annotations_test_full.csv"
        )
    )
    mzl_dict = build_mzl_dict()
    process(mzl_dict, save_data_path, full_df)
    # run validate_data once all images are present in imgs folder
