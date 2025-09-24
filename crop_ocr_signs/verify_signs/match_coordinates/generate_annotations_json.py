# standard imports 
from collections import defaultdict
import json
from typing import List, Dict, Union

# package imports
from pydantic import BaseModel
from tqdm import tqdm

# local imports
from crop_ocr_signs.connection import get_connection
from crop_ocr_signs.convenience_methods.show_crop_in_image import get_image_from_file_name
from crop_ocr_signs.convenience_methods.update_with_disambiguated_reading import make_disambiguated_dict
from crop_ocr_signs.extract_data import read_json_file, transform_signs_array_to_signs_dict
from crop_ocr_signs.verify_signs.get_partial_order_signs import get_crops_groupped_by_fragments, get_ocred_signs 

"""
Match names of crops in folder `signs_40k_ocr_no_partial_order` to its geometry and generate Annotation objects. 
"""
################################

class Annotation(BaseModel):
    geometry: Dict[str, float]
    data: Dict[str, Union[str, bool]]
    # croppedSign: Dict[str, str]

class AnnotationObject(BaseModel):
    fragmentNumber: str 
    annotations: List[Annotation]

def xyxy_to_xywh(coords):
    """Convert (x1, y1, x2, y2) to (x, y, width, height)."""
    x1, y1, x2, y2 = coords
    return x1, y1, x2-x1, y2-y1

def convert_abs_coordinates_to_relative_geometry(abs_coordinates, image_width, image_height):
    """
    Get absolute coordinates from OCR, e.g. 
    [921, 472, 1163, 565] for SAG in K.2210
    and convert to the relative geometry found in the annotations DB collection:
    {
        "x": 51.4807302231237,
        "y": 19.2471406891957,
        "width": 13.5496957403651,
        "height": 3.79020616648776
    }
    """
    abs_xywh = xyxy_to_xywh(abs_coordinates) 
    absolute_x, absolute_y, absolute_width, absolute_height = abs_xywh 
    relative_x = absolute_x * 100 / image_width
    relative_y = absolute_y * 100 / image_height
    relative_width = absolute_width * 100 / image_width
    relative_height = absolute_height * 100 / image_height
    return {
        "x":relative_x,
        "y":relative_y,
        "width":relative_width,
        "height":relative_height
        }

def get_annotations_for_signs(db, cropped_ocred_signs_and_index_array, ocr_signs_dict, fragment_number):
    """
    For crops of a tablet, e.g. 
        [('ABZ214', '1'), ('ABZ99', '2'), ('ABZ214', '3'), ('ABZ15', '4'), ('ABZ128', '5'), ('ABZ86', '8'), ('ABZ212', '9'), ('ABZ84', '11'), ('ABZ61', '12')]
    in K.13973, 
    find the corresponding coordinates for each. 

    For spotchecking, run `convenience_methods`, show_crop_in_image.py 
    """
    photo_file_name = f"{fragment_number}.jpg"
    ocr_coordinates_list = ocr_signs_dict[photo_file_name]["ocredSignsCoordinates"]
    abz_sign_dict = make_disambiguated_dict()
    image = get_image_from_file_name(photo_file_name, db)
    
    annotations = [] 
    for sign, idx in cropped_ocred_signs_and_index_array:
        annotation = defaultdict()

        abs_coordinates = ocr_coordinates_list[int(idx)]
        relative_geom = convert_abs_coordinates_to_relative_geometry(abs_coordinates, *image.size)

        annotation["geometry"] = relative_geom 
        annotation["data"] = {
            "id": f"{sign}_{idx}",
            "type": "OCR",
            "ocr": True,
            "signName": abz_sign_dict[sign]
        } 
        annotation_object = Annotation(**annotation)
        annotations.append(annotation_object)
    return annotations


if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    verified_crops_folder = 'signs_40k_ocr_no_partial_order'
    crops_groupped_by_fragment = get_crops_groupped_by_fragments(verified_crops_folder)
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)

    all_annotation_objs = []
    for fragment_number in tqdm(list(crops_groupped_by_fragment.keys())[:3]):
        crops_of_fragment = crops_groupped_by_fragment[fragment_number]
        # get ocredSigns and match with coordinates
        cropped_ocred_signs_and_index_array = get_ocred_signs(fragment_number, ocr_signs_dict, crops_of_fragment)
        annotations = get_annotations_for_signs(db, cropped_ocred_signs_and_index_array,ocr_signs_dict, fragment_number)
        annotation_obj = AnnotationObject(**{
            "fragmentNumber": fragment_number,
            "annotations": annotations
        })
        all_annotation_objs.append(annotation_obj.dict())

    with open("annotations_from_crops.json", "w", encoding="utf-8") as f:
        json.dump(all_annotation_objs, f, ensure_ascii=False, indent=2)