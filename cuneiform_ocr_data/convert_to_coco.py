import json
import shutil
from pathlib import Path

from PIL import Image

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory

custom_classes = [
    "ABZ579",
    "ABZ13",
    "ABZ480",
    "ABZ342",
    "ABZ70",
    "ABZ1",
    "ABZ142",
    "ABZ533",
    "ABZ461",
    "ABZ597",
    "ABZ449",
    "ABZ318",
    "ABZ381",
    "ABZ61",
    "ABZ231",
    "ABZ75",
    "ABZ139",
    "ABZ354",
    "ABZ536",
    "ABZ330",
    "ABZ308",
    "ABZ545",
    "ABZ69",
    "ABZ86",
    "ABZ295",
    "ABZ15",
    "ABZ214",
    "ABZ296",
    "ABZ73",
    "ABZ328",
    "ABZ68",
    "ABZ335",
    "ABZ55",
    "ABZ457",
    "ABZ411",
    "ABZ151",
    "ABZ537",
    "ABZ84",
    "ABZ371",
    "ABZ366",
    "ABZ5",
    "ABZ396",
    "ABZ353",
    "ABZ384",
    "ABZ206",
    "ABZ324",
    "ABZ99",
    "ABZ376",
    "ABZ58",
    "ABZ74",
    "ABZ383",
    "ABZ532",
    "ABZ334",
    "ABZ589",
    "ABZ145",
    "ABZ59",
    "ABZ343",
    "ABZ586",
    "ABZ7",
    "ABZ60",
    "ABZ52",
    "ABZ212",
    "ABZ211",
    "ABZ322",
    "ABZ399",
    "ABZ367",
    "ABZ78",
    "ABZ38",
    "ABZ207",
    "ABZ142a",
    "ABZ115",
    "ABZ112",
    "ABZ85",
    "ABZ97",
    "ABZ144",
    "ABZ331",
    "ABZ167",
    "ABZ401",
    "ABZ319",
    "ABZ595",
    "ABZ80",
    "ABZ427",
    "ABZ79",
    "ABZ306",
    "ABZ465",
    "ABZ312",
    "ABZ314",
    "ABZ2",
    "ABZ575",
    "ABZ397",
    "ABZ471",
    "ABZ172",
    "ABZ554",
    "ABZ339",
    "ABZ147",
    "ABZ6",
    "ABZ232",
    "ABZ412",
    "ABZ12",
    "ABZ535",
    "ABZ472",
    "ABZ440",
    "ABZ441",
    "ABZ393",
    "ABZ230",
    "ABZ128",
    "ABZ62",
    "ABZ570",
    "ABZ148",
    "ABZ331e+152i",
    "ABZ455",
    "ABZ104",
    "ABZ111",
    "ABZ313",
    "ABZ468",
    "ABZ134",
    "ABZ72",
    "ABZ538",
    "ABZ101",
    "ABZ406",
    "ABZ298",
    "ABZ483",
    "ABZ470",
    "ABZ191",
    "ABZ50",
    "ABZ9",
    "ABZ398",
    "ABZ87",
    "ABZ529",
    "ABZ205",
    "ABZ437",
    "ABZ152",
    "ABZ131",
    "ABZ565",
    "ABZ56",
    "ABZ10",
    "ABZ124",
    "ABZ279",
    "ABZ170",
    "ABZ598a",
    "ABZ143",
    "ABZ307",
    "ABZ94",
    "ABZ195",
    "ABZ209",
    "ABZ138",
    "ABZ164",
    "ABZ374",
    "ABZ297",
    "ABZ346",
    "ABZ337",
    "ABZ126",
    "ABZ280",
    "ABZ481",
    "ABZ57",
    "ABZ559",
    "ABZ105",
    "ABZ556",
    "ABZ574",
    "ABZ332",
    "ABZ215",
    "ABZ133",
    "ABZ309",
]
not_found_class = ["unknown"]
classes = [*custom_classes, *not_found_class]


def create_coco(anns, imgs, out_path, mapping=None):
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
            total_bboxes += 1
            if mapping is None:
                category_id = 0
            else:
                try:
                    sign = mapping[bbox.clean_sign]
                    category_id = classes.index(sign)
                except (ValueError, KeyError):
                    print(f"Class {bbox.clean_sign} not found in mapping")
                    category_id = classes.index("unknown")
                    unmapped_bboxes += 1
                    # continue
                    # unless you want to include them

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

    if mapping is None:
        categories = [{"id": 0, "name": "null"}]
    else:
        categories = [{"id": i, "name": sign} for i, sign in enumerate(classes)]

    coco_format_json = dict(
        images=images, annotations=annotations, categories=categories
    )
    create_directory(out_path / "coco" / "val2017")
    create_directory(out_path / "coco" / "annotations")
    # copy all files from imgs to val2017
    for file in imgs.iterdir():
        shutil.copyfile(file, out_path / "coco" / "val2017" / file.name)

    with open(
        out_path / "coco/annotations/instances_val2017.json", "w", encoding="utf-8"
    ) as f:
        json.dump(coco_format_json, f, ensure_ascii=False, indent=4)

    print("Total bboxes: ", total_bboxes)
    print("Unmapped bboxes: ", unmapped_bboxes)


if __name__ == "__main__":
    data = Path("data/processed-data/detection/test")

    out_path = Path("cuneiform_ocr_data/data-coco")
    mapping = build_ebl_dict()
    # mapping = None
    create_coco(data / "annotations", data / "imgs", out_path, mapping)
