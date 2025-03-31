# standard imports
from enum import Enum
# local imports
from connection import get_connection
from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict, build_abz_dict

########################################################

def get_sign_objects(fragment_number):
    annotations = db['annotations']
    query = { "fragmentNumber": fragment_number}
    annotation_array = annotations.find_one(query)["annotations"]
    annotation_array_with_index = [(obj,i) for i,obj in enumerate(annotation_array)]
    return annotation_array_with_index

def get_sign_geometry(annotation_array_with_index, criterion, sign_value):

    array_obj = [item for item in annotation_array_with_index if item[0]["data"][criterion]==sign_value]
    geometries = [(obj["geometry"],i) for obj,i in array_obj]
    if geometries:
        sign_name = array_obj[0][0]["data"]["signName"]
    return geometries, sign_name

def get_sign_geometry_by_position(annotation_array, position):
    geometry = annotation_array[position][0]["geometry"]
    sign_name = annotation_array[position][0]["data"]["signName"]
    return geometry, sign_name

class Criteria(Enum):
    sign_name = "signName"
    sign_value = "value"

def convert_geometry(geometry):
    """Convert geometry with small coordinates to EPSG:4326"""
    return
if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']

    fragment_number = "K.1283"
    sign_value = "sag"
    sign_name_input = "IGI"
    annotation_array = get_sign_objects(fragment_number)
    geometries, sign_name = get_sign_geometry(annotation_array, Criteria.sign_name.value, sign_name_input)
    print(geometries)
    breakpoint()

    if sign_name:
        sign_abz_dict = build_ebl_dict()
        abz_reading = sign_abz_dict[sign_name]
        print(abz_reading)
