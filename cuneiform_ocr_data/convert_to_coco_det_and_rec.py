import json
import shutil
from pathlib import Path

from PIL import Image

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory

classes = ['ABZ13', 'ABZ579', 'ABZ480', 'ABZ70', 'ABZ597', 'ABZ342', 'ABZ461', 'ABZ61', 'ABZ381', 'ABZ142', 'ABZ1', 'ABZ318', 'ABZ231', 'ABZ449', 'ABZ533', 'ABZ75', 'ABZ354', 'ABZ545', 'ABZ536', 'ABZ139', 'ABZ330', 'ABZ308', 'ABZ15', 'ABZ86', 'ABZ328', 'ABZ214', 'ABZ73', 'ABZ295', 'ABZ55', 'ABZ296', 'ABZ371', 'ABZ537', 'ABZ151', 'ABZ335', 'ABZ68', 'ABZ5', 'ABZ411', 'ABZ69', 'ABZ366', 'ABZ457', 'ABZ396', 'ABZ324', 'ABZ353', 'ABZ84', 'ABZ99', 'ABZ206', 'ABZ58', 'ABZ376', 'ABZ384', 'ABZ532', 'ABZ334', 'ABZ383', 'ABZ74', 'ABZ399', 'ABZ59', 'ABZ145', 'ABZ367', 'ABZ7', 'ABZ586', 'ABZ589', 'ABZ211', 'ABZ52', 'ABZ97', 'ABZ144', 'ABZ212', 'ABZ319', 'ABZ78', 'ABZ343', 'ABZ465', 'ABZ85', 'ABZ115', 'ABZ207', 'ABZ331', 'ABZ570', 'ABZ38', 'ABZ427', 'ABZ322', 'ABZ60', 'ABZ314', 'ABZ79', 'ABZ80', 'ABZ142a', 'ABZ232', 'ABZ535', 'ABZ112', 'ABZ554', 'ABZ339', 'ABZ279', 'ABZ172', 'ABZ575', 'ABZ6', 'ABZ595', 'ABZ148', 'ABZ230', 'ABZ468', 'ABZ128', 'ABZ306', 'ABZ12', 'ABZ312', 'ABZ134', 'ABZ147', 'ABZ104', 'ABZ397', 'ABZ331e+152i', 'ABZ441', 'ABZ111', 'ABZ2', 'ABZ412', 'ABZ167', 'ABZ62', 'ABZ455', 'ABZ313', 'ABZ472', 'ABZ401', 'ABZ471', 'ABZ72', 'ABZ538', 'ABZ440', 'ABZ101', 'ABZ143', 'ABZ50', 'ABZ483', 'ABZ94', 'ABZ393', 'ABZ437', 'ABZ298', 'ABZ205', 'ABZ559', 'ABZ164', 'ABZ565', 'ABZ87', 'ABZ126', 'ABZ307', 'ABZ138', 'ABZ152', 'ABZ195', 'ABZ191', 'ABZ124']
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
    data_test = Path("data/processed-data/detection/without_deebscribe/test")
    out_path = Path("cuneiform_ocr_data/data-coco")
    create_directory("data-coco", overwrite=True)
    create_directory(out_path / "coco" / "val2017")
    create_directory(out_path / "coco" / "train2017")
    create_directory(out_path / "coco" / "annotations")

    create_coco(data_test / "annotations", data_test / "imgs", out_path, mapping)

    #data_train = Path("data/processed-data/detection/total+deebscribe/train")

    #out_path = Path("cuneiform_ocr_data/data-coco")
    #create_coco(
        #data_test / "annotations", data_train / "imgs", out_path, mapping, test=False
    #)
