import json
import shutil
from pathlib import Path

from PIL import Image

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory

custom_classes = ['ABZ579', 'ABZ13', 'ABZ342', 'ABZ70', 'ABZ480', 'ABZ461', 'ABZ142', 'ABZ1', 'ABZ533', 'ABZ597', 'ABZ449', 'ABZ231', 'ABZ318', 'ABZ381', 'ABZ61', 'ABZ75', 'ABZ354', 'ABZ139', 'ABZ536', 'ABZ330', 'ABZ308', 'ABZ86', 'ABZ328', 'ABZ545', 'ABZ15', 'ABZ69', 'ABZ295', 'ABZ214', 'ABZ73', 'ABZ296', 'ABZ55', 'ABZ68', 'ABZ537', 'ABZ371', 'ABZ457', 'ABZ151', 'ABZ335', 'ABZ411', 'ABZ366', 'ABZ353', 'ABZ5', 'ABZ84', 'ABZ396', 'ABZ206', 'ABZ324', 'ABZ384', 'ABZ58', 'ABZ376', 'ABZ99', 'ABZ532', 'ABZ74', 'ABZ383', 'ABZ59', 'ABZ334', 'ABZ145', 'ABZ586', 'ABZ589', 'ABZ343', 'ABZ211', 'ABZ7', 'ABZ399', 'ABZ212', 'ABZ78', 'ABZ367', 'ABZ322', 'ABZ60', 'ABZ115', 'ABZ38', 'ABZ319', 'ABZ207', 'ABZ112', 'ABZ85', 'ABZ52', 'ABZ97', 'ABZ144', 'ABZ80', 'ABZ427', 'ABZ79', 'ABZ142a', 'ABZ232', 'ABZ167', 'ABZ535', 'ABZ312', 'ABZ314', 'ABZ331', 'ABZ172', 'ABZ575', 'ABZ306', 'ABZ6', 'ABZ465', 'ABZ339', 'ABZ128', 'ABZ2', 'ABZ401', 'ABZ12', 'ABZ554', 'ABZ595', 'ABZ331e+152i', 'ABZ147', 'ABZ134', 'ABZ397', 'ABZ230', 'ABZ148', 'ABZ104', 'ABZ570', 'ABZ471', 'ABZ440', 'ABZ412', 'ABZ472', 'ABZ393', 'ABZ313', 'ABZ441', 'ABZ62', 'ABZ101', 'ABZ468', 'ABZ111', 'ABZ538', 'ABZ455', 'ABZ298', 'ABZ483', 'ABZ87', 'ABZ205', 'ABZ72', 'ABZ50', 'ABZ143', 'ABZ565', 'ABZ152', 'ABZ307', 'ABZ138', 'ABZ406', 'ABZ94', 'ABZ470', 'ABZ191', 'ABZ9', 'ABZ164', 'ABZ124', 'ABZ398', 'ABZ126', 'ABZ529', 'ABZ437', 'ABZ559', 'ABZ56', 'ABZ10', 'ABZ131', 'ABZ332']
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
