import json
import os.path as osp
import shutil
from pathlib import Path

from PIL import Image
from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.classification.utils import build_ebl_dict
from cuneiform_ocr_data.path import create_directory
from cuneiform_ocr_data.prepare_and_split_data import prepare_data

custom_classes = ['ABZ579', 'ABZ13', 'ABZ342', 'ABZ70', 'ABZ461', 'ABZ142', 'ABZ480', 'ABZ1', 'ABZ231', 'ABZ533', 'ABZ449', 'ABZ318', 'ABZ75', 'ABZ61', 'ABZ354', 'ABZ139', 'ABZ381', 'ABZ597', 'ABZ536', 'ABZ308', 'ABZ330', 'ABZ328', 'ABZ86', 'ABZ15', 'ABZ214', 'ABZ545', 'ABZ73', 'ABZ295', 'ABZ55', 'ABZ335', 'ABZ371', 'ABZ151', 'ABZ457', 'ABZ537', 'ABZ69', 'ABZ353', 'ABZ68', 'ABZ5', 'ABZ296', 'ABZ84', 'ABZ366', 'ABZ411', 'ABZ396', 'ABZ206', 'ABZ58', 'ABZ324', 'ABZ376', 'ABZ99', 'ABZ384', 'ABZ59', 'ABZ532', 'ABZ334', 'ABZ589', 'ABZ383', 'ABZ343', 'ABZ586', 'ABZ399', 'ABZ74', 'ABZ211', 'ABZ145', 'ABZ7', 'ABZ212', 'ABZ78', 'ABZ367', 'ABZ38', 'ABZ319', 'ABZ85', 'ABZ115', 'ABZ322', 'ABZ97', 'ABZ144', 'ABZ112', 'ABZ427', 'ABZ60', 'ABZ207', 'ABZ79', 'ABZ80', 'ABZ232', 'ABZ142a', 'ABZ312', 'ABZ52', 'ABZ331', 'ABZ128', 'ABZ314', 'ABZ535', 'ABZ575', 'ABZ134', 'ABZ465', 'ABZ167', 'ABZ172', 'ABZ339', 'ABZ6', 'ABZ331e+152i', 'ABZ306', 'ABZ12', 'ABZ2', 'ABZ148', 'ABZ397', 'ABZ554', 'ABZ570', 'ABZ441', 'ABZ147', 'ABZ472', 'ABZ104', 'ABZ440', 'ABZ230', 'ABZ595', 'ABZ455', 'ABZ313', 'ABZ298', 'ABZ412', 'ABZ62', 'ABZ468', 'ABZ101', 'ABZ111', 'ABZ483', 'ABZ538', 'ABZ471', 'ABZ87', 'ABZ143', 'ABZ565', 'ABZ205', 'ABZ152', 'ABZ72', 'ABZ138', 'ABZ401', 'ABZ50', 'ABZ406', 'ABZ307', 'ABZ126', 'ABZ124', 'ABZ164', 'ABZ529', 'ABZ559', 'ABZ94', 'ABZ437', 'ABZ56', 'ABZ393', 'ABZ398']

not_found_class = ["SignClassNotInImageClassificationTrainData"]

classes = [*custom_classes, *not_found_class]


def create_coco(relative_to, anns, imgs, out_path, mapping=None):
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
                    category_id = classes.index(mapping[bbox.clean_sign])
                except (ValueError, KeyError):
                    print(f"Class {bbox.clean_sign} not found in mapping")
                    category_id = classes.index("SignClassNotInImageClassificationTrainData")
                    unmapped_bboxes += 1
                    # continue
                    # unless you want to include them

            coco_ann = dict(
                image_id=counter,
                id=obj_count,
                category_id=category_id,
                bbox=[bbox.top_left_x, bbox.top_left_y, bbox.width, bbox.height],
                area=bbox.width * bbox.height,
                segmentation=[],  # bbox.as_clockwise_coordinates,
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

    with open(out_path / "coco/annotations/instances_val2017.json", "w", encoding="utf-8") as f:
        json.dump(coco_format_json, f, ensure_ascii=False, indent=4)

    print("Total bboxes: ", total_bboxes)
    print("Unmapped bboxes: ", unmapped_bboxes)


if __name__ == "__main__":
    out = Path("./data/coco-split")
    # prepare_data(Path("../data/processed-data/total"), out, (0.9,), 1)
    path = Path(
        "/home/yunus/PycharmProjects/cuneiform-ocr-data/cuneiform_ocr_data/data"
    )
    mapping = build_ebl_dict()
    #mapping = None
    create_coco(
        path, path / "annotations/test", path / "textdet_imgs/test", Path("cross_validation_data/data_split11_coco"), mapping
    )