import json
import shutil
from pathlib import Path

from PIL import Image

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory

classes = ['ABZ579', 'ABZ13', 'ABZ480', 'ABZ70', 'ABZ597', 'ABZ342', 'ABZ461', 'ABZ381', 'ABZ1', 'ABZ61', 'ABZ142', 'ABZ318', 'ABZ231', 'ABZ533', 'ABZ449', 'ABZ75', 'ABZ354', 'ABZ139', 'ABZ545', 'ABZ536', 'ABZ330', 'ABZ308', 'ABZ15', 'ABZ86', 'ABZ73', 'ABZ214', 'ABZ328', 'ABZ55', 'ABZ296', 'ABZ371', 'ABZ68', 'ABZ295', 'ABZ537', 'ABZ411', 'ABZ457', 'ABZ5', 'ABZ335', 'ABZ151', 'ABZ69', 'ABZ366', 'ABZ396', 'ABZ324', 'ABZ99', 'ABZ206', 'ABZ353', 'ABZ84', 'ABZ532', 'ABZ384', 'ABZ58', 'ABZ376', 'ABZ59', 'ABZ74', 'ABZ334', 'ABZ399', 'ABZ97', 'ABZ52', 'ABZ586', 'ABZ7', 'ABZ211', 'ABZ145', 'ABZ383', 'ABZ589', 'ABZ367', 'ABZ319', 'ABZ343', 'ABZ85', 'ABZ144', 'ABZ570', 'ABZ78', 'ABZ115', 'ABZ212', 'ABZ207', 'ABZ465', 'ABZ322', 'ABZ112', 'ABZ38', 'ABZ331', 'ABZ427', 'ABZ60', 'ABZ79', 'ABZ80', 'ABZ314', 'ABZ142a', 'ABZ595', 'ABZ232', 'ABZ535', 'ABZ279', 'ABZ172', 'ABZ312', 'ABZ6', 'ABZ554', 'ABZ230', 'ABZ128', 'ABZ468', 'ABZ167', 'ABZ401', 'ABZ575', 'ABZ12', 'ABZ313', 'ABZ148', 'ABZ339', 'ABZ104', 'ABZ331e+152i', 'ABZ472', 'ABZ306', 'ABZ134', 'ABZ2', 'ABZ441', 'ABZ412', 'ABZ147', 'ABZ471', 'ABZ397', 'ABZ62', 'ABZ111', 'ABZ455', 'ABZ72', 'ABZ538', 'ABZ143', 'ABZ101', 'ABZ440', 'ABZ437', 'ABZ393', 'ABZ298', 'ABZ50', 'ABZ483', 'ABZ559', 'ABZ87', 'ABZ94', 'ABZ152', 'ABZ138', 'ABZ164', 'ABZ565', 'ABZ205', 'ABZ598a', 'ABZ307', 'ABZ9', 'ABZ398', 'ABZ191', 'ABZ126', 'ABZ124', 'ABZ195', 'ABZ470', 'ABZ131', 'ABZ375', 'ABZ56', 'ABZ556', 'ABZ170']
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
    data_test = Path("data/processed-data/detection/test")
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
