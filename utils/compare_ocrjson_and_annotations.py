# standard imports
import os
import json
import base64
from io import BytesIO

# package imports
from PIL import Image

# local imports
from connection import get_connection
from retrieve_sign_from_abz import convert_abz_array_to_sign_name_array
from extract_data import get_annotated_fragments_ids, JSON_FILE_NAME, read_json_file, transform_signs_array_to_signs_dict
from analyse_data import signs_outputted_from_ocr
########################################################

def filter_transliteration_by_ocr_target_signs(transliteration):
    ocr_target_signs = signs_outputted_from_ocr
    return [abl for abl in transliteration if abl in ocr_target_signs ]


if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    fragments = db['fragments']
    annotations = db['annotations']
    cropped_ocr_signs_folder = 'data_from_ocrjson'
    # fragments which already have annotations have already been excluded from the sign crops I did in April, but since then there would've been new annotations, so redo filter 
    annotated_fragments_ids = get_annotated_fragments_ids(annotations)

    # loop through OCRed signs to annotated sign 
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)

    folder_path = os.path.join(os.getcwd(),cropped_ocr_signs_folder)

    for foldername in os.listdir(folder_path):
        if 'json' in foldername: continue
        print(foldername)
        for jpg in os.listdir(os.path.join(folder_path, foldername)):
            sign_name, fragment_number, index_in_ocred_json = jpg.split('.jpg')[0].split('_')
            if fragment_number in annotated_fragments_ids: continue
            # goal: check signs property (i.e. the transliteration) in Fragments and see if sign in OCRed_Signs.json is in the transliteration

            # get ocredSigns 
            ocred_signs_array = ocr_signs_dict[f"{fragment_number}.jpg"]["ocredSigns"].split()
            sign_name_array = convert_abz_array_to_sign_name_array(ocred_signs_array)
            # get transliteration
            fragment_object = fragments.find_one({"_id": fragment_number})
            transliteration = fragment_object[ "signs" ].split()
            transliteration_array_of_ocred_signs_only = filter_transliteration_by_ocr_target_signs(transliteration)
            breakpoint()
            transliteration_sign_name_array = convert_abz_array_to_sign_name_array(transliteration_array_of_ocred_signs_only)
            
            # ex K.13973
            # ocred: ['KI', 'BI', 'EN', 'BI', '|KA×GIR₂|', 'AB', 'RI', 'IŠ', 'ZI', 'MU']
            # transliteration of ocred signs only: ['BI', 'AN', 'UD', 'EN', 'DI', 'AN', 'NI₂', 'EN', 'BI', 'RI', 'A', '|KA×GIR₂|', 'RA', 'AB', 'ZI₃', 'NU', 'IGI', 'NI₂', 'MU', 'UD', 'RI', 'IŠ', 'TU', 'ZI', 'MU']
            # KI likely wrong: indeed, successfully filtered by function extract_data.match_signs_from_fragment 

