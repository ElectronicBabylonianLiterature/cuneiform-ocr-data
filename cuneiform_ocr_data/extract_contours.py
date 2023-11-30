# pyre-ignore-all-errors[16]
import shutil
from pathlib import Path
from typing import List

import cv2
import numpy as np

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer, BoundingBox
from cuneiform_ocr_data.utils import create_directory


def calculate_cropped_coordinates(
    img: np.ndarray, contours: np.ndarray, index: int, bboxes: List[BoundingBox]
):
    cimg = np.zeros_like(img)
    bboxes_img = np.zeros_like(img)
    cv2.drawContours(cimg, contours, index, 1, -1)
    for bbox in bboxes:
        for x, y in bbox.as_clockwise_coordinates:
            bboxes_img[y, x] = 1
    if np.any(np.logical_and(cimg, bboxes_img)):
        pts = np.where(cimg == 1)
        padding = 15
        top_y = min(pts[0]) - padding
        bottom_y = max(pts[0]) + padding
        bottom_x = min(pts[1]) - padding
        top_x = max(pts[1]) + padding
        top_y = max(top_y, 0)
        bottom_x = max(bottom_x, 0)
        top_x = min(top_x, img.shape[1])
        bottom_y = min(bottom_y, img.shape[0])

        return BoundingBox.from_two_vertices([bottom_x, top_y, top_x, bottom_y])
    else:
        return None


def extract_contours(img: np.ndarray, bboxes):
    img_area = img.shape[0] * img.shape[1]
    im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh, bw_img = cv2.threshold(im_gray, 200, 255, cv2.THRESH_OTSU)
    # bw_img = cv2.adaptiveThreshold(im_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, _ = cv2.findContours(bw_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_index = {}

    for i, contour in enumerate(contours):
        contour_index[i] = cv2.contourArea(contour)

    sorted_index = sorted(contour_index, key=contour_index.get, reverse=True)
    largest_contour = contour_index[sorted_index[0]]

    THRESHOLD_LARGEST_CONTOUR = img_area * 0.025

    results = []
    if largest_contour >= THRESHOLD_LARGEST_CONTOUR:
        for i in sorted_index[0:20]:
            THRESHOLD_CONTOUR = largest_contour * 0.2
            if contour_index[i] >= THRESHOLD_CONTOUR:
                result = calculate_cropped_coordinates(img, contours, i, bboxes)
                result and results.append(result)
    return results


if __name__ == "__main__":
    """
    This script will extract contours from images and create new images and annotations.
    If struct bounding boxes (obverse, reverse, ...) are given in the annotations the contours can be extracted using
    these annotations. If not, the contours will be extracted automatically. One has to set the flag.
    """

    EXTRACT_CONTOURS_AUTOMATICALLY = False
    input_data = Path("data/raw-data/ebl/detection-11-30")
    output_data_path = Path(
        "data/processed-data/ebl/ebl-detection-extracted-30-11"
    )

    input_annotations_folder = input_data / "annotations"
    input_imgs_folder = input_data / "imgs"

    output_imgs = output_data_path / "imgs"
    output_annotations = output_data_path / "annotations"

    create_directory(output_data_path, overwrite=True)
    create_directory(output_imgs)
    create_directory(output_annotations)

    images = list(input_imgs_folder.iterdir())
    annotations = list(input_annotations_folder.iterdir())
    for counter, image_path in enumerate(images):
        print(f"{counter} of {len(images)}")
        annotation_file = next(
            input_annotations_folder.glob(f"*{image_path.stem}.txt"), None
        )
        if annotation_file is None:
            raise Exception("Not found annotations for image:", image_path.name)
        bounding_boxes_container = BoundingBoxesContainer.from_file(annotation_file)

        if EXTRACT_CONTOURS_AUTOMATICALLY:
            image = cv2.imread(str(image_path))
            try:
                contours = extract_contours(
                    image, bounding_boxes_container.bounding_boxes
                )
            except IndexError as e:
                print("Image:", image_path.name)
                print("IndexError", e)
                contours = []
        else:
            contours = bounding_boxes_container.contours
        if len(contours):
            image = cv2.imread(str(image_path))
            for counter, contour in enumerate(contours):
                bboxes_without_contour_types = list(
                    filter(
                        lambda bbox: contour.contains_bbox(bbox),
                        bounding_boxes_container.bounding_boxes,
                    )
                )
                bboxes_without_contour_types = list(
                    filter(
                        lambda bbox: not bbox.is_contour_type,
                        bboxes_without_contour_types,
                    )
                )
                recalculated_bboxes = [
                    bbox.recalculate(contour) for bbox in bboxes_without_contour_types
                ]
                recalculated_bboxes = BoundingBoxesContainer(
                    bounding_boxes_container.image_id, recalculated_bboxes
                )
                crop_img = image[
                    contour.top_left_y : contour.top_left_y + contour.height,
                    contour.top_left_x : contour.top_left_x + contour.width,
                    :,
                ]
                cv2.imwrite(
                    str(output_imgs / f"{image_path.stem}-{counter}.jpg"), crop_img
                )
                recalculated_bboxes.create_ground_truth_txt_from_file(
                    output_annotations / f"{annotation_file.stem}-{counter}.txt"
                )
        else:
            shutil.copy(image_path, output_imgs / image_path.name)
            shutil.copy(annotation_file, output_annotations / annotation_file.name)
    print("Done")
