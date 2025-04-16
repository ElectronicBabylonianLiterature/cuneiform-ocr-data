# standard imports
import os
import json
JSON_FILE_NAME = "eBL_OCRed_Signs.json"

# local imports
from extract_data import read_json_file, transform_signs_array_to_signs_dict

########################################################
def get_ocred_signs_dict():
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)
    return ocr_signs_dict

def get_coordinates_for_cropped_sign(fragment_number, index, ocr_signs_dict):
    coordinates = ocr_signs_dict[fragment_number]["ocredSignsCoordinates"][index]
    return coordinates

def get_image_from_file_name(file_name, ocr_signs_dict):
    sign, fragment_number, index = file_name.split('_')
    coordinates = get_coordinates_for_cropped_sign(fragment_number, index,ocr_signs_dict)

if __name__ == '__main__':
    ocr_signs_dict =  get_ocred_signs_dict()
    image = get_image_from_file_name(file_name, ocr_signs_dict)
