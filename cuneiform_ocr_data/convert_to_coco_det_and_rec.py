import json
import shutil
from pathlib import Path

from PIL import Image

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory

classes = [
    "ABZ579",
    "ABZ13",
    "ABZ480",
    "ABZ70",
    "ABZ342",
    "ABZ597",
    "ABZ461",
    "ABZ142",
    "ABZ381",
    "ABZ1",
    "ABZ61",
    "ABZ318",
    "ABZ533",
    "ABZ231",
    "ABZ449",
    "ABZ75",
    "ABZ354",
    "ABZ545",
    "ABZ139",
    "ABZ330",
    "ABZ536",
    "ABZ308",
    "ABZ86",
    "ABZ15",
    "ABZ328",
    "ABZ214",
    "ABZ73",
    "ABZ295",
    "ABZ55",
    "ABZ537",
    "ABZ69",
    "ABZ371",
    "ABZ296",
    "ABZ457",
    "ABZ151",
    "ABZ411",
    "ABZ68",
    "ABZ335",
    "ABZ366",
    "ABZ5",
    "ABZ324",
    "ABZ396",
    "ABZ353",
    "ABZ99",
    "ABZ206",
    "ABZ84",
    "ABZ532",
    "ABZ376",
    "ABZ58",
    "ABZ384",
    "ABZ74",
    "ABZ334",
    "ABZ59",
    "ABZ383",
    "ABZ145",
    "ABZ399",
    "ABZ7",
    "ABZ589",
    "ABZ586",
    "ABZ97",
    "ABZ211",
    "ABZ343",
    "ABZ367",
    "ABZ52",
    "ABZ212",
    "ABZ85",
    "ABZ115",
    "ABZ319",
    "ABZ207",
    "ABZ78",
    "ABZ144",
    "ABZ465",
    "ABZ38",
    "ABZ570",
    "ABZ322",
    "ABZ331",
    "ABZ60",
    "ABZ427",
    "ABZ112",
    "ABZ80",
    "ABZ314",
    "ABZ79",
    "ABZ142a",
    "ABZ232",
    "ABZ312",
    "ABZ535",
    "ABZ554",
    "ABZ595",
    "ABZ128",
    "ABZ339",
    "ABZ12",
    "ABZ172",
    "ABZ331e+152i",
    "ABZ147",
    "ABZ575",
    "ABZ167",
    "ABZ230",
    "ABZ279",
    "ABZ401",
    "ABZ306",
    "ABZ468",
    "ABZ6",
    "ABZ472",
    "ABZ148",
    "ABZ2",
    "ABZ104",
    "ABZ313",
    "ABZ397",
    "ABZ134",
    "ABZ412",
    "ABZ441",
    "ABZ62",
    "ABZ455",
    "ABZ440",
    "ABZ471",
    "ABZ111",
    "ABZ538",
    "ABZ72",
    "ABZ101",
    "ABZ393",
    "ABZ50",
    "ABZ298",
    "ABZ437",
    "ABZ94",
    "ABZ143",
    "ABZ483",
    "ABZ205",
    "ABZ565",
    "ABZ191",
    "ABZ124",
    "ABZ152",
    "ABZ87",
    "ABZ138",
    "ABZ559",
    "ABZ164",
    "ABZ126",
    "ABZ598a",
    "ABZ195",
    "ABZ307",
    "ABZ9",
    "ABZ556",
]
# not_found_class = ["unknown"]
# classes = [*custom_classes, *not_found_class]


def create_coco(anns, imgs, out_path, mapping=None, test=True):
    # only have val=test and train
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
            total_bboxes += 1
            if mapping is None:
                category_id = 0
            else:
                try:
                    sign = mapping[bbox.clean_sign]
                    category_id = classes.index(sign)
                except (ValueError, KeyError):
                    print(f"Class {bbox.clean_sign} not found in mapping")
                    # category_id = classes.index("unknown")
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
    mapping = build_ebl_dict()
    data_test = Path("data/processed-data/detection/total+deebscribe/test")
    out_path = Path("cuneiform_ocr_data/data-coco")
    create_directory("data-coco", overwrite=True)
    create_directory(out_path / "coco" / "val2017")
    create_directory(out_path / "coco" / "train2017")
    create_directory(out_path / "coco" / "annotations")

    create_coco(data_test / "annotations", data_test / "imgs", out_path, mapping)

    data_train = Path("data/processed-data/detection/total+deebscribe/train")

    out_path = Path("cuneiform_ocr_data/data-coco")
    create_coco(
        data_test / "annotations", data_train / "imgs", out_path, mapping, test=False
    )
