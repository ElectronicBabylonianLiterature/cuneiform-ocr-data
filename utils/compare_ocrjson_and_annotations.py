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

def remove_completions_from_transliteration():
    # check with { _id: "1879,0708.124" }

def test_remove_completions_from_transliteration():
    fragment_object = 'X ABZ401 X\nABZ401 ABZ461 ABZ457 ABZ73\nABZ401 ABZ461 ABZ457 ABZ73 ABZ597 ABZ470 X X X X X X X X X\nABZ480 ABZ99 ABZ87 ABZ15 ABZ55 ABZ376 ABZ80 ABZ85\nABZ61 ABZ231 ABZ1 ABZ461 ABZ61 ABZ483 ABZ115 ABZ296 ABZ401 ABZ296 ABZ314 ABZ342 ABZ13 ABZ360 ABZ114 ABZ457 ABZ78 ABZ393 ABZ231 ABZ537 ABZ69\nABZ69 ABZ1 ABZ354 ABZ112 ABZ401 ABZ461 ABZ457 ABZ73 ABZ597 ABZ470 ABZ480 ABZ449 ABZ106 ABZ401 ABZ296 ABZ401 ABZ296 ABZ314 ABZ342 ABZ381 ABZ206 ABZ13 ABZ323 ABZ533 ABZ68 ABZ533 ABZ480 ABZ87 ABZ111 ABZ533 ABZ231\nABZ69 ABZ411 ABZ411 ABZ318 ABZ61 ABZ231 ABZ1 ABZ461 ABZ570 ABZ296 ABZ314 ABZ342 ABZ480 ABZ384 ABZ75 ABZ68 ABZ381 ABZ84 ABZ381 ABZ393 ABZ61 ABZ480 ABZ366 ABZ60\nABZ61 ABZ231 ABZ461 ABZ570 150 ABZ449 ABZ296 ABZ536 ABZ533 ABZ322 ABZ533 ABZ230 ABZ533\nABZ411 ABZ401 ABZ461 ABZ457 ABZ73 ABZ597 ABZ470 ABZ480 ABZ449 ABZ106 ABZ401 ABZ296 ABZ314 ABZ342 ABZ208 ABZ401 ABZ597 150 ABZ296 ABZ69\nABZ381 ABZ354 ABZ7 ABZ366 ABZ10\nABZ13 ABZ360 ABZ114 ABZ80 ABZ172 ABZ1 ABZ38 ABZ331e+152i ABZ398\nABZ401 ABZ597 ABZ470 ABZ295 ABZ296 ABZ209 ABZ393 ABZ61 ABZ60 ABZ1 ABZ396 ABZ597 ABZ126 ABZ10\nABZ296 ABZ401 ABZ296 ABZ314 ABZ457 ABZ134 ABZ61 ABZ480 ABZ279\nABZ296 ABZ401 ABZ296 ABZ314'
    

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

    for foldername in sorted(os.listdir(folder_path)):
        non_folder_elements = ('json', '.DS_Store')
        if any(x in foldername for x in non_folder_elements): continue
        print(foldername)
        for jpg in sorted(os.listdir(os.path.join(folder_path, foldername))):
            sign_name, fragment_number, index_in_ocred_json = jpg.split('.jpg')[0].split('_')
            if fragment_number in annotated_fragments_ids: continue
            # goal: check signs property (i.e. the transliteration) in Fragments and see if sign in OCRed_Signs.json is in the transliteration

            # get ocredSigns 
            ocred_signs_array = ocr_signs_dict[f"{fragment_number}.jpg"]["ocredSigns"].split()
            sign_name_array = convert_abz_array_to_sign_name_array(ocred_signs_array)
            # get transliteration
            fragment_object = fragments.find_one({"_id": fragment_number})
            transliteration = fragment_object[ "signs" ]
            transliteration_array_of_ocred_signs_only = filter_transliteration_by_ocr_target_signs(transliteration.split())
            transliteration_sign_name_array = convert_abz_array_to_sign_name_array(transliteration_array_of_ocred_signs_only)
            breakpoint()
            
       

