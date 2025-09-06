# standard imports 
import os
from pathlib import Path

# package imports
from tqdm import tqdm

# local imports
from cuneiform_ocr_data.sign_mappings.mappings import build_abz_dict
from utils.filter_functions import TARGET_SIGNS_STRING, construct_kv_pairs_of_disambiguated_abz_reading

def make_disambiguated_dict():
    abz_sign_dict = build_abz_dict()
    disambiguated_kv_pairs = construct_kv_pairs_of_disambiguated_abz_reading()
    abz_sign_dict.update(disambiguated_kv_pairs)
    return abz_sign_dict

def convert_abz_array_to_sign_name_array(ocred_signs_array):
    abz_sign_dict = make_disambiguated_dict()
    invalid_signs = ['X']
    return [abz_sign_dict[abl] for abl in ocred_signs_array if abl not in invalid_signs]

def update_sign_name(file, abz_folder, abz_sign_dict):
    """
    Sign image crops had used the old, ambiguous dict
    
        e.g.   "ABZ15": ["KA", "|KA\u00d7GIR\u2082|"]. -> KA is the one we want.

        Update the latter one with the former.
    """
    old_img_name_parts = file.stem.split('_')
    old_img_name_parts[0] = abz_sign_dict[abz_folder]
    new_path = file.with_name("_".join(old_img_name_parts) + file.suffix)
    return new_path

def change_sign_img_names():
    root_folder = "data_from_ocrjson"
    abz_sign_dict = make_disambiguated_dict()
    abz_folders = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))]
    abz_folders
    for abz_folder in tqdm(abz_folders):
        files_for_that_abz = [ file_path for file_path in Path(f"{root_folder}/{abz_folder}").iterdir() ]
        for file in files_for_that_abz: 
            new_path = update_sign_name(file, abz_folder, abz_sign_dict)
            file.rename(new_path)


def update_sign_img_names_in_file(txt_file):
    abz_sign_dict = make_disambiguated_dict()
    new_paths = []
    with open(txt_file, 'r', encoding="utf-8") as f:
        for line in f:            
            file = Path(line.strip())
            abz_folder = file.parent.name
            new_path = update_sign_name(file, abz_folder, abz_sign_dict) 
            new_paths.append(new_path)
    with open("utils/images_to_delete/no_partial_order_x1.txt", "w", encoding="utf-8") as f:
        for p in new_paths:
            f.write(str(p) + "\n")

if __name__ == '__main__':
    abl = "ABZ480"
    # abz_sign_dict = convert_abz_array_to_sign_name_array(TARGET_SIGNS_STRING)
    # sign_reading = abz_sign_dict[abl]
    # print(sign_reading)

    txt_file = "utils/images_to_delete/no_partial_order_x1_old_naming.txt"
    update_sign_img_names_in_file(txt_file)




