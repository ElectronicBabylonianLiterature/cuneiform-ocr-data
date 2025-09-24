# standard imports 
from collections import defaultdict
from typing import List, Dict, Union

# package imports
from pydantic import BaseModel
from tqdm import tqdm

# local imports
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

def get_annotations_for_signs(cropped_ocred_signs_and_index_array, ocr_signs_dict, fragment_number):
    """
    For crops of a tablet, e.g. 
        [('ABZ214', '1'), ('ABZ99', '2'), ('ABZ214', '3'), ('ABZ15', '4'), ('ABZ128', '5'), ('ABZ86', '8'), ('ABZ212', '9'), ('ABZ84', '11'), ('ABZ61', '12')]
    in K.13973, 
    find the corresponding coordinates for each. 

    For spotchecking, run `convenience_methods`, show_crop_in_image.py 
    """
    ocr_coordinates_list = ocr_signs_dict[f"{fragment_number}.jpg"]["ocredSignsCoordinates"]
    abz_sign_dict = make_disambiguated_dict()
    
    annotations = [] 
    for sign, idx in cropped_ocred_signs_and_index_array:
        annotation = defaultdict()
        annotation["geometry"] = ocr_coordinates_list[int(idx)]
        annotation["data"] = {
            "id": f"{sign}_{idx}",
            "type": "OCR",
            "ocr": True,
            "signName": abz_sign_dict[sign]
        } 
        annotation_object = Annotation(**annotation)
        annotations.append(annotation_object)
        breakpoint()


if __name__ == '__main__':
    verified_crops_folder = 'signs_40k_ocr_no_partial_order'
    crops_groupped_by_fragment = get_crops_groupped_by_fragments(verified_crops_folder)
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)

    for fragment_number in tqdm(list(crops_groupped_by_fragment.keys())):
        crops_of_fragment = crops_groupped_by_fragment[fragment_number]
        # get ocredSigns and match with coordinates
        cropped_ocred_signs_and_index_array = get_ocred_signs(fragment_number, ocr_signs_dict, crops_of_fragment)
        get_annotations_for_signs(cropped_ocred_signs_and_index_array,ocr_signs_dict, fragment_number)

        