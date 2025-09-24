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
from crop_ocr_signs.connection import get_connection
from crop_ocr_signs.extract_data import get_annotated_fragments_ids, read_json_file, transform_signs_array_to_signs_dict
from crop_ocr_signs.filter_functions import signs_outputted_from_ocr

"""
Filter signs with partial order 
"""
########################################################

CROPPED_OCR_SIGNS_FOLDER = 'data_from_ocrjson'

def filter_transliteration_by_ocr_target_signs(transliteration):
    ocr_target_signs = signs_outputted_from_ocr
    return [ abl for abl in transliteration if abl in ocr_target_signs ]


def appears_in_order(sequence, lst):
    """
    Check if all elements of 'sequence' appear in 'lst' in order.
    They do not have to be consecutive.
    """
    it = iter(lst)
    return all(item in it for item in sequence)

def get_all_crops():
    root_folder = Path(CROPPED_OCR_SIGNS_FOLDER)
    all_crops_generator = root_folder.rglob("*.jpg")
    return all_crops_generator

def get_crops_from_now_annotated_fragments(annotated_fragments_id):
    """Return crop images to delete if they belong to fragments that are now annotated."""
    images_to_delete = set()

    for jpg_file in get_all_crops():
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
    crops_to_delete_txt = "crop_ocr_signs/verify_signs/delete_because_annotated.txt"
    write_cropped_images_to_delete(crops_to_delete, crops_to_delete_txt) 
    delete_cropped_images_based_on_list(crops_to_delete_txt)

def get_processed_transliteration(fragment_object):
    """Process transliteration by filtering transliteration by target signs"""

    transliteration = fragment_object[ "signs" ]
    transliteration_array_of_ocred_signs_only = filter_transliteration_by_ocr_target_signs(transliteration.split())

    return transliteration_array_of_ocred_signs_only

def is_ordered_subsequence(sub, full):
    iter_full = iter(full)
    return all(elem in iter_full for elem in sub)

def get_out_of_order_indices(partial_tuples, full):
    iter_full = iter(full)
    out_of_order = []
    for elem, idx  in partial_tuples:
        if elem in full:
            # if element not found in the remaining iterator, it's out of order
            try:
                while next(iter_full) != elem:
                    pass
            except StopIteration:
                out_of_order.append(idx)
    return out_of_order

def check_local_order(partials, full, out_of_order_indices, window=1):
    results = {}
    partials_to_check = [(p,idx) for idx, p in enumerate(partials) if str(idx) in out_of_order_indices ]
    for i, partial_tuple in enumerate(partials_to_check):
        partial, idx = partial_tuple
        # get local context
        start = max(0, i - window)
        end = min(len(partial), i + window + 1)
        context = partial[start:end]

        results[str(idx)] = is_ordered_subsequence(context, full) 

    return results

def get_out_of_order_crops(crops_of_fragment, cropped_ocred_signs_and_index_array, transliteration_array):
    """
    Get crops which do not have local ordering. 
    E.g. 
    partial (OCR_ed signs not in global ordering)= ['BI', 'EN', 'BI', 'KA']
    full (transliterated signs) = ['BI', 'AN', 'UD', 'EN', 'IM', 'BI', 'RI', 'A', 'KA', 'RA']
    For 'EN', we check up to X (1 or 2 etc.) signs before and after if they are in non-consecutive order. And it is. 
    """
    cropped_ocred_signs = [t[0] for t in cropped_ocred_signs_and_index_array]
    out_of_order_indices = get_out_of_order_indices(cropped_ocred_signs_and_index_array, transliteration_array)
    in_order_array = check_local_order(cropped_ocred_signs, transliteration_array, out_of_order_indices)
    out_of_local_order_crops = [p for p in crops_of_fragment if in_order_array.get(p.name.split('_')[2].split(".jpg")[0]) == False]

    return out_of_local_order_crops

def get_crops_groupped_by_fragments():
    """Get dict of fragment_number:[list of crops]"""
    all_crops = get_all_crops()
    crop_sets_groupped_by_fragment = defaultdict(set)
    for crop in all_crops:
        fragment = crop.name.split("_")[1]
        crop_sets_groupped_by_fragment[fragment].add(crop)
    crops_groupped_by_fragment = {k:list(v) for k, v in crop_sets_groupped_by_fragment.items()} 

    return crops_groupped_by_fragment

def get_ocred_signs(fragment_number, ocr_signs_dict):
    """Get OCR-read signs from the json file eBL_OCRed_Signs.json"""
    ocred_signs_array = ocr_signs_dict[f"{fragment_number}.jpg"]["ocredSigns"].split()
    cropped_ocred_signs_indices = [posix_path.name.split('_')[2].split(".jpg")[0] for posix_path in crops_of_fragment]
    cropped_ocred_signs_and_index_array = [(sign,str(i)) for i, sign in enumerate(ocred_signs_array) if str(i) in cropped_ocred_signs_indices]
    # sign_name_array = convert_abz_array_to_sign_name_array(cropped_ocred_signs_array)
    return cropped_ocred_signs_and_index_array

if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    fragments = db['fragments']
    output_folder_path = 'crop_ocr_signs/verify_signs'
    # delete_crops_from_now_annotated_fragments(annotations) # Done 

    crops_groupped_by_fragment = get_crops_groupped_by_fragments()
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)

    crops_to_delete = []
    for iter_idx, fragment_number in tqdm(enumerate(list(crops_groupped_by_fragment.keys()))):
        try:
            crops_of_fragment = crops_groupped_by_fragment[fragment_number]
            # get ocredSigns 
            cropped_ocred_signs_and_index_array = get_ocred_signs(fragment_number, ocr_signs_dict)

            # get transliteration
            fragment_object = fragments.find_one({"_id": fragment_number})
            if not fragment_object: continue
            transliteration_array = get_processed_transliteration(fragment_object)

            # 0. exclude ocr readings that are not in the tablet: already done in the cropping stage
            # 1. check ocr readings appear in order, if so no deletions needed.  
            cropped_ocred_signs = [t[0] for t in cropped_ocred_signs_and_index_array]
            if is_ordered_subsequence(cropped_ocred_signs, transliteration_array): continue

            # 2. failing that, get out of order crops and check if they are in order locally
            out_of_local_order_crops = get_out_of_order_crops(crops_of_fragment, cropped_ocred_signs_and_index_array, transliteration_array)  
            crops_to_delete.extend(out_of_local_order_crops)
            
        except Exception as e:
            error_info = {
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            with open(f"{output_folder_path}/crop_comparison_err.log", "a") as f:
                json.dump(error_info, f)
                f.write("\n")
            continue

    os.makedirs(output_folder_path, exist_ok=True)
    with open(f"{output_folder_path}/no_partial_order.txt", 'a', encoding='utf-8') as f:
        for item in crops_to_delete:
            f.write(f'{item}\n')
       

