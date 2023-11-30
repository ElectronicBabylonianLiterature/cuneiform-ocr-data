import json
import shutil
from pathlib import Path

from PIL import Image

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory

# this is in the mapping apriori
UNCLEAR_SIGN = "UnclearSign"
CUT_OFF = 90


def create_coco(anns, imgs, out_path, categories, categories_with_ids, name):
    annotations = []
    images = []

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
            try:
                category_id = categories.index(bbox.clean_sign)
            except ValueError:
                print(f"Class {bbox.clean_sign} not found in mapping")
                category_id = categories.index(UNCLEAR_SIGN)

            coco_ann = dict(
                image_id=counter,
                id=obj_count,
                category_id=category_id,
                bbox=[bbox.top_left_x, bbox.top_left_y, bbox.width, bbox.height],
                area=bbox.width * bbox.height,
                segmentation=[],  # bbox.as_clockwise_coordinates for having bounding box for segmentation too
                iscrowd=0,
            )
            annotations.append(coco_ann)
            obj_count += 1

    coco_format_json = dict(
        images=images, annotations=annotations, categories=categories_with_ids
    )
    for file in imgs.iterdir():
        shutil.copyfile(file, out_path / "coco" / name / file.name)

    with open(
        out_path / f"coco/annotations/instances_{name}.json", "w", encoding="utf-8"
    ) as f:
        json.dump(coco_format_json, f, ensure_ascii=False, indent=4)


def get_categories_from_training_set(annotations, mapping):
    # mapping contains UnclearSigns for unknown signs
    mapping = mapping
    categories = list(mapping.keys())
    categories.sort()
    categories_counting = {}
    for counter, ann in enumerate(annotations.iterdir()):
        bbox_container = BoundingBoxesContainer.from_file(ann)
        for bbox in bbox_container.bounding_boxes:
            try:
                category_id = categories.index(bbox.clean_sign)
            except ValueError:
                print(f"Class {bbox.clean_sign} not found in mapping")
                category_id = categories.index(UNCLEAR_SIGN)
            if category_id in categories_counting:
                categories_counting[category_id] += 1
            else:
                categories_counting[category_id] = 1
    categories_counting = {k: v for k, v in categories_counting.items() if v > CUT_OFF}
    categories_with_ids = [
        {"id": i, "name": categories[cat]}
        for i, cat in enumerate(categories_counting.keys())
    ]
    return [c["name"] for c in categories_with_ids], categories_with_ids


if __name__ == "__main__":
    mapping = build_ebl_dict()
    data_train = Path("data/processed-data/detection/without_deebscribe/train")
    out_path = Path("cuneiform_ocr_data/data-coco")
    if out_path.exists():
        shutil.rmtree(out_path)
    create_directory(out_path, overwrite=True)
    create_directory(out_path / "coco" / "val2017")
    create_directory(out_path / "coco" / "train2017")
    create_directory(out_path / "coco" / "annotations")

    categories, categories_with_ids = get_categories_from_training_set(
        data_train / "annotations", mapping
    )

    create_coco(
        data_train / "annotations",
        data_train / "imgs",
        out_path,
        categories,
        categories_with_ids,
        "train2017",
    )

    print([c["name"] for c in categories_with_ids])

    data_test = Path("data/processed-data/detection/without_deebscribe/test")
    create_coco(
        data_test / "annotations",
        data_test / "imgs",
        out_path,
        categories,
        categories_with_ids,
        "val2017",
    )
