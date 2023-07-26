from pathlib import Path

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer

if __name__ == "__main__":
    path = Path("../temp/heidelberg/annotations")
    bboxes = BoundingBoxesContainer.from_file(path / "gt_P397986.txt")
    bboxes = bboxes.shift_boxes(370, 60)
    BoundingBoxesContainer("P397986", bboxes.bounding_boxes).create_ground_truth_txt(
        path
    )
