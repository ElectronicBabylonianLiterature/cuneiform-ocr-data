# if main ...
import json
from pathlib import Path

from tqdm import tqdm

from cuneiform_ocr_data.bounding_boxes import BoundingBox, BoundingBoxesContainer
from cuneiform_ocr_data.utils import create_directory

if __name__ == "__main__":
    # can be used to manually validate files and delete bad ones for classification
    annotations = Path("data/raw-data/deepscribe/imagesWithHotspots.json")
    output = Path("data/raw-data/deepscribe/annotations")
    create_directory(output, overwrite=True)
    # open annotations and parse as json
    with open(annotations) as f:
        annotations = json.load(f)

    # check annotation
    an = list(filter(lambda x: "acb91e50-" in x["image_id"], annotations))
    for annotation in tqdm(annotations):
        bboxes = [BoundingBox.from_two_vertices(x["bbox"], "deepscribe")  for x in annotation["annotations"]]
        bbox_container = BoundingBoxesContainer(annotation["image_id"], bboxes)
        bbox_container.create_ground_truth_txt(output)
    print("Done")