import json
import os.path as osp
from pathlib import Path

from PIL import Image
from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer
from cuneiform_ocr_data.prepare_and_split_data import prepare_data



if __name__ == '__main__':
    relative_to = Path("../data/processed-data/total")
    anns = Path("../data/processed-data/total/annotations")
    imgs = Path("../data/processed-data/total/imgs")
    out_file = Path("coco_format.json")

    prepare_data(relative_to, Path("./data/coco-split"), (0.5,), 1)

    annotations = []
    images = []

    obj_count = 0
    for counter, ann in enumerate(anns.iterdir()):
        id_ = ann.stem.split('gt_')[1]
        img_path = imgs / f"{id_}.jpg"
        height, width = Image.open(img_path).size


        local_path = img_path.relative_to(relative_to)
        images.append(dict(id=counter, file_name=str(local_path), height=height, width=width))

        bbox_container = BoundingBoxesContainer.from_file(ann)

        for bbox in bbox_container.bounding_boxes:
            coco_ann = dict(image_id=counter,
            id=obj_count,
            category_id=0,
            bbox=[bbox.top_left_x, bbox.top_left_y, bbox.width, bbox.height],
            area=bbox.width * bbox.height,
            segmentation=bbox.as_clockwise_coordinates,
            iscrowd=0)
            annotations.append(coco_ann)
            obj_count += 1

    coco_format_json = dict(
        images=images,
        annotations=annotations,
        categories=[{
            'id': 0,
            'name': 'null'
        }])
    with open(relative_to / out_file, 'w', encoding='utf-8') as f:
        json.dump(coco_format_json, f, ensure_ascii=False, indent=4)
