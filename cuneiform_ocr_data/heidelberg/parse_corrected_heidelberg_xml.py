import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer, BoundingBox
from cuneiform_ocr_data.sign_mappings.mappings import build_mzl_dict
from cuneiform_ocr_data.utils import create_directory


def convert_xml_bounding_box_to_bounding_box(file_path: Path, mzl_dict):
    tree = ET.parse(file_path)
    root = tree.getroot()
    bounding_boxes: List[BoundingBox] = []
    for obj in root.findall("object"):
        # numbers are with trailing 00 sometimes
        symbol = str(int(obj.find("symbol").text))
        xmin = int(float(obj.find("bndbox").find("xmin").text))
        ymin = int(float(obj.find("bndbox").find("ymin").text))
        xmax = int(float(obj.find("bndbox").find("xmax").text))
        ymax = int(float(obj.find("bndbox").find("ymax").text))
        conservation = obj.find("conservation").text
        assert conservation in ["partial", "intact"]
        sign = (
            f"{mzl_dict[str(int(symbol))]}{'?' if conservation  == 'partial' else ''}"
        )
        try:
            bbox = BoundingBox.from_two_vertices([xmin, ymin, xmax, ymax], sign=sign)
        except ValueError:
            print(
                f"Error in file: {file_path} invliad bbox: {xmin, ymin, xmax, ymax} with sign: {sign}"
            )
            break
        bounding_boxes.append(bbox)
    return BoundingBoxesContainer(file_path.stem, bounding_boxes)


if __name__ == "__main__":
    mzl_dict = build_mzl_dict()
    destination_path = Path("temp") / "annotations"
    create_directory(destination_path, overwrite=True)
    for file in Path(
        "../../data/raw-data/heidelberg/heidelberg-xml-manuel-fixed/heidelberg-xml"
    ).iterdir():
        bounding_boxes = convert_xml_bounding_box_to_bounding_box(file, mzl_dict)
        bounding_boxes.create_ground_truth_txt(destination_path)
