import hashlib
from datetime import datetime
from pathlib import Path

import cv2

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory


def validate_sign_mapping():
    mapping = build_ebl_dict()
    path = Path("../../temp/xfragmented/lmu/annotations")
    unmapped = {}
    for file in path.iterdir():
        bboxes = BoundingBoxesContainer.from_file(file)
        for bbox in bboxes.bounding_boxes:
            # if sign has ? at the end it means it is partially broken
            sign = bbox.sign.split("?")[0]
            if mapping.get(sign) is None and not sign.isdigit():
                unmapped[bbox.sign] = unmapped.get(bbox.sign, 0) + 1

    for sign, count in unmapped.items():
        print(f"Sign: {sign}, {count} not in mapping")
    print(f"Number of unmapped signs: {len(unmapped)}")


def hash(string) -> str:
    hasher = hashlib.sha1(string.encode("utf-8"))
    return str(hasher.hexdigest())


def crop_signs_from_images():
    mapping = build_ebl_dict()
    path = Path("data/processed-data/ebl+heidelberg-train")
    images = path / "imgs"
    annotations = path / "annotations"
    output_imgs = Path("data/processed-data/ebl+heidelberg-train-cropped")
    create_directory(output_imgs, overwrite=True)

    errors = 0
    for counter, image_path in enumerate(images.iterdir()):
        print(f"{counter} of {len(list(images.iterdir()))}")
        annotation_file = next(annotations.glob(f"*{image_path.stem}.txt"), None)
        if annotation_file is None:
            raise Exception("Not found annotations for image:", image_path.name)
        bounding_boxes_container = BoundingBoxesContainer.from_file(annotation_file)
        image = cv2.imread(str(image_path))
        for bbox in filter(
            lambda bbox: bbox.has_sign, bounding_boxes_container.bounding_boxes
        ):
            if bbox.has_sign:
                crop_img = image[
                    bbox.top_left_y : bbox.top_left_y + bbox.height,
                    bbox.top_left_x : bbox.top_left_x + bbox.width,
                ]
                sign = bbox.clean_sign
                try:
                    cv2.imwrite(
                        str(
                            output_imgs
                            / f"{mapping[sign]}_{hash(sign + str(datetime.now()))}.jpg"
                        ),
                        crop_img,
                    )
                except Exception as e:
                    print(ValueError(f"{bounding_boxes_container.image_id}, {bbox}"))
                    errors += 1
                    # raise ValueError(f"{bounding_boxes_container.image_id}, {bbox}") from e
    print(f"Errors: {errors}")


if __name__ == "__main__":
    crop_signs_from_images()
