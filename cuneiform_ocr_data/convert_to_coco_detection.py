import json
import shutil
from pathlib import Path

from PIL import Image

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.utils import create_directory


def create_coco(anns, imgs, out_path, test=True):
    name = "val2017" if test is True else "train2017"
    annotations = []
    images = []

    total_bboxes = 0
    unmapped_bboxes = 0

    obj_count = 0
    for counter, ann in enumerate(anns.iterdir()):
        id_ = ann.stem.split("gt_")[1]
        img_path = imgs / f"{id_}.jpg"
        width, height = Image.open(img_path).size

        local_path = str(img_path.name)
        images.append(
            dict(id=counter, file_name=local_path, height=height, width=width)
        )
        bbox_container = BoundingBoxesContainer.from_file(ann)

        for bbox in bbox_container.bounding_boxes:

            coco_ann = dict(
                image_id=counter,
                id=obj_count,
                category_id=0,
                bbox=[bbox.top_left_x, bbox.top_left_y, bbox.width, bbox.height],
                area=bbox.width * bbox.height,
                segmentation=[],  # bbox.as_clockwise_coordinates for having bounding box for segmentation too
                iscrowd=0,
            )
            annotations.append(coco_ann)
            obj_count += 1

    categories = [{"id": 0, "name": "null"}]

    coco_format_json = dict(
        images=images, annotations=annotations, categories=categories
    )

    # copy all files from imgs to val2017
    for file in imgs.iterdir():
        shutil.copyfile(file, out_path / "coco" / name / file.name)

    with open(
        out_path / f"coco/annotations/instances_{name}.json", "w", encoding="utf-8"
    ) as f:
        json.dump(coco_format_json, f, ensure_ascii=False, indent=4)

    print("Total bboxes: ", total_bboxes)
    print("Unmapped bboxes: ", unmapped_bboxes)


if __name__ == "__main__":
    data_test = Path("data/processed-data/detection/test")
    out_path = Path("cuneiform_ocr_data/data-coco")
    create_directory("data-coco", overwrite=True)
    create_directory(out_path / "coco" / "val2017")
    create_directory(out_path / "coco" / "train2017")
    create_directory(out_path / "coco" / "annotations")

    #create_coco(data_test / "annotations", data_test / "imgs", out_path)

    data_train = Path("data/processed-data/detection/train+deebscribe")

    out_path = Path("cuneiform_ocr_data/data-coco")
    create_coco(data_train / "annotations", data_train / "imgs", out_path, test=False)
