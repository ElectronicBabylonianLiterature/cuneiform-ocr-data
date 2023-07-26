from pathlib import Path

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer, BoundingBox

if __name__ == "__main__":
    path = Path(
        "/home/yunus/PycharmProjects/cuneiform-ocr-data2/data/processed-data/heidelberg/heidelberg/annotations"
    )
    p1, rec1 = "P336009", BoundingBox(295, 400, 500, 200)
    # p2, rec2 = "P314346", BoundingBox(100, 1300, 10000, 10000)
    for p, rec in [(p1, rec1)]:
        bboxes = BoundingBoxesContainer.from_file(path / f"gt_{p}.txt")
        bboxes = bboxes.delete_within_bbox(rec)
        BoundingBoxesContainer(f"{p}", bboxes.bounding_boxes).create_ground_truth_txt(
            path
        )
