import json
import os.path as osp
import shutil
from pathlib import Path

from PIL import Image
from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.classification.utils import build_ebl_dict
from cuneiform_ocr_data.path import create_directory
from cuneiform_ocr_data.prepare_and_split_data import prepare_data

custom_classes = ['ABZ579', 'ABZ13', 'ABZ342', 'ABZ70', 'ABZ461', 'ABZ142', 'ABZ318', 'ABZ231', 'ABZ1', 'ABZ480', 'ABZ533', 'ABZ449', 'ABZ75', 'ABZ354', 'ABZ61', 'ABZ597', 'ABZ536', 'ABZ139', 'ABZ381', 'ABZ308', 'ABZ86', 'ABZ328', 'ABZ330', 'ABZ69', 'ABZ214', 'ABZ73', 'ABZ545', 'ABZ15', 'ABZ295', 'ABZ296', 'ABZ151', 'ABZ55', 'ABZ335', 'ABZ537', 'ABZ371', 'ABZ68', 'ABZ457', 'ABZ84', 'ABZ366', 'ABZ5', 'ABZ353', 'ABZ396', 'ABZ411', 'ABZ206', 'ABZ58', 'ABZ324', 'ABZ99', 'ABZ376', 'ABZ532', 'ABZ384', 'ABZ334', 'ABZ383', 'ABZ74', 'ABZ59', 'ABZ343', 'ABZ145', 'ABZ589', 'ABZ586', 'ABZ211', 'ABZ212', 'ABZ399', 'ABZ7', 'ABZ367', 'ABZ78', 'ABZ115', 'ABZ322', 'ABZ207', 'ABZ38', 'ABZ319', 'ABZ144', 'ABZ85', 'ABZ97', 'ABZ112', 'ABZ60', 'ABZ79', 'ABZ427', 'ABZ232', 'ABZ80', 'ABZ167', 'ABZ312', 'ABZ535', 'ABZ52', 'ABZ172', 'ABZ331', 'ABZ554', 'ABZ314', 'ABZ128', 'ABZ142a', 'ABZ12', 'ABZ331e+152i', 'ABZ401', 'ABZ147', 'ABZ440', 'ABZ6', 'ABZ575', 'ABZ570', 'ABZ134', 'ABZ465', 'ABZ230', 'ABZ306', 'ABZ148', 'ABZ339', 'ABZ397', 'ABZ472', 'ABZ441', 'ABZ412', 'ABZ104', 'ABZ595', 'ABZ455', 'ABZ313', 'ABZ298', 'ABZ62', 'ABZ101', 'ABZ393', 'ABZ483', 'ABZ471', 'ABZ111', 'ABZ87', 'ABZ538', 'ABZ468', 'ABZ138', 'ABZ565', 'ABZ152', 'ABZ406', 'ABZ72', 'ABZ205', 'ABZ126', 'ABZ2', 'ABZ50', 'ABZ94', 'ABZ529', 'ABZ307', 'ABZ143', 'ABZ124', 'ABZ164', 'ABZ559', 'ABZ437', 'ABZ9', 'ABZ398', 'ABZ131']
#not_found_class = ["SignClassNotInImageClassificationTrainData"]

#classes = [*custom_classes], *not_found_class]
classes = custom_classes

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
                except ValueError:
                    print(f"Class {bbox.clean_sign} not found in mapping")
                    #category_id = classes.index(not_found_class)
                    unmapped_bboxes += 1
                    continue
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
        "/home/yunus/PycharmProjects/cuneiform-ocr-data/cuneiform_ocr_data/cross_validation_data/data_icdar2015_split1"
    )
    mapping = build_ebl_dict()
    #mapping = None
    create_coco(
        path, path / "annotations/test", path / "textdet_imgs/test", Path("cross_validation_data/data_split11_coco"), mapping
    )