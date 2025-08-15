# standard imports
from collections import defaultdict
import os
import json
import base64
from io import BytesIO
from pathlib import Path
import traceback

# package imports
from PIL import Image
from tqdm import tqdm

# local imports
from connection import get_connection
from retrieve_sign_from_abz import convert_abz_array_to_sign_name_array
from extract_data import get_annotated_fragments_ids, JSON_FILE_NAME, read_json_file, transform_signs_array_to_signs_dict
from analyse_data import signs_outputted_from_ocr
from utils.filter_functions import remove_completions_from_transliteration
########################################################

def filter_transliteration_by_ocr_target_signs(transliteration):
    ocr_target_signs = signs_outputted_from_ocr
    return [abl for abl in transliteration if abl in ocr_target_signs ]


def appears_in_order(sequence, lst):
    """
    Check if all elements of 'sequence' appear in 'lst' in order.
    They do not have to be consecutive.
    """
    it = iter(lst)
    return all(item in it for item in sequence)

def safe_slice(lst, idx):
    """
    Return lst[idx-2 : idx+2] if possible.
    If idx-2 < 0, start from 0.
    If idx+2 > len(lst), end at len(lst).
    """
    start = max(idx - 2, 0)
    end = min(idx + 2, len(lst))
    return lst[start:end]

def get_crops_from_now_annotated_fragments(annotated_fragments_id):
    """Return crop images to delete if they belong to fragments that are now annotated."""
    root_folder = Path("data_from_ocrjson")
    images_to_delete = set()

    for jpg_file in root_folder.rglob("*.jpg"):
        filename = jpg_file.name
        fragment_name = filename.split('_')[1]
        if fragment_name in annotated_fragments_id:
            images_to_delete.add(str(jpg_file))

    return list(images_to_delete)

def write_cropped_images_to_delete(image_files_to_delete, text_file):
    with open(text_file, "w") as f:
        for file in image_files_to_delete:
            f.write(file + "\n")

def delete_cropped_images_based_on_list(text_file):
    with open(text_file) as f:
        for line in f:
            path = Path(line.strip())
            if path.exists():
                path.unlink()

def delete_crops_from_now_annotated_fragments(annotations):
    """
    Fragments which already have annotations have already been excluded from the sign crops I did in April, 
    
    but since then there would've been new annotations, so re-filter those crops. 
    """
    annotated_fragments_ids = get_annotated_fragments_ids(annotations)
    crops_to_delete = []
    crops_to_delete.extend(get_crops_from_now_annotated_fragments(annotated_fragments_ids))
    crops_to_delete_txt = "utils/cropped_images_to_delete.txt"
    write_cropped_images_to_delete(crops_to_delete, crops_to_delete_txt) 
    delete_cropped_images_based_on_list(crops_to_delete_txt)

if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    fragments = db['fragments']
 
    cropped_ocr_signs_folder = 'data_from_ocrjson'

    # delete_crops_from_now_annotated_fragments(annotations)

    # loop through OCRed signs to annotated sign 
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)

    folder_path = os.path.join(os.getcwd(),cropped_ocr_signs_folder)
    crops_to_delete = []
    for foldername in sorted(os.listdir(folder_path)):
        non_folder_elements = ('json', '.DS_Store')
        if any(x in foldername for x in non_folder_elements): continue
        print(foldername)
        for jpg in tqdm(sorted(os.listdir(os.path.join(folder_path, foldername)))):
            sign_name, fragment_number, index_in_ocred_json = jpg.split('.jpg')[0].split('_')
            # goal: check signs property (i.e. the transliteration) in Fragments and see if sign in OCRed_Signs.json is in the transliteration

            # get ocredSigns 
            ocred_signs_array = ocr_signs_dict[f"{fragment_number}.jpg"]["ocredSigns"].split()
            sign_name_array = convert_abz_array_to_sign_name_array(ocred_signs_array)
            try:
                # get transliteration
                fragment_object = fragments.find_one({"_id": fragment_number})
                if fragment_object:
                    transliteration = fragment_object[ "signs" ]
                    transliteration_without_completions = remove_completions_from_transliteration(transliteration, fragment_object["text"]["lines"])
                    transliteration_array_of_ocred_signs_only = filter_transliteration_by_ocr_target_signs(transliteration_without_completions.split())
                    transliteration_sign_name_array = convert_abz_array_to_sign_name_array(transliteration_array_of_ocred_signs_only)
                
                    sequence = safe_slice(sign_name_array, int(index_in_ocred_json))
                    if not appears_in_order(sequence, transliteration_sign_name_array):
                        crops_to_delete.append(jpg)
            except Exception as e:
                error_info = {
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                print(error_info)
        folder_path = 'utils/images_to_delete'
        os.makedirs(folder_path, exist_ok=True)
        with open(f"{folder_path}/{foldername}", 'w', encoding='utf-8') as f:
            for item in crops_to_delete:
                f.write(f'{item}\n')
        breakpoint()
       

