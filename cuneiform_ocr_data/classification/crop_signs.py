import hashlib
from datetime import datetime
from pathlib import Path

import cv2

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory


def validate_sign_mapping(mapping, test_files_path):
    path = Path(test_files_path) / "annotations"
    unmapped = {}
    for file in path.iterdir():
        bboxes = BoundingBoxesContainer.from_file(file)
        for bbox in bboxes.bounding_boxes:
            # if sign has ? at the end it means it is partially broken
            sign = bbox.sign.split("?")[0]
            if mapping.get(sign) is None:
                unmapped[bbox.sign] = unmapped.get(bbox.sign, 0) + 1

    for sign, count in unmapped.items():
        print(f"Sign: {sign}, {count} not in mapping")
    print(f"Number of unmapped signs: {len(unmapped)}")


def hash(string) -> str:
    hasher = hashlib.sha1(string.encode("utf-8"))
    return str(hasher.hexdigest())


def crop_signs_from_images(mapping, test_files_path, exclude_partially_broken=True):
    path = Path(test_files_path)
    images = path / "imgs"
    annotations = path / "annotations"
    output_img_folder = "ebl-test"
    output_imgs = Path(f"data/processed-data/classification/{output_img_folder}")
    create_directory(output_imgs, overwrite=True)

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
            partially_broken = "?" in bbox.sign 
            if bbox.has_sign:
                if partially_broken and exclude_partially_broken == True: continue
                crop_img = image[
                    bbox.top_left_y : bbox.top_left_y + bbox.height,
                    bbox.top_left_x : bbox.top_left_x + bbox.width,
                ]
                sign = bbox.sign
                try:
                    cv2.imwrite(
                        str(
                            output_imgs
                            / f"{mapping[sign]}_{hash(sign + str(datetime.now()))}.jpg"
                        ),
                        crop_img,
                    )
                except Exception as e:
                    import traceback
                    import json
                    error_info = {
                        "image_id": bounding_boxes_container.image_id, 
                        "bbox": str(bbox),
                        "type": type(e).__name__,
                        "message": str(e),
                        "traceback": traceback.format_exc()
                    }
                    with open(f"{path.parent}/log_crop_signs.jsonl", "a") as f:
                        json.dump(error_info, f)
                        f.write("\n")


if __name__ == "__main__":
    mapping = build_ebl_dict()
    test_files_path = "data/processed-data/ebl/ebl-detection-extracted-17-04-25/test"
    # validate_sign_mapping(mapping, test_files_path)
    exclude_partially_broken = True
    crop_signs_from_images(mapping, test_files_path, exclude_partially_broken)
