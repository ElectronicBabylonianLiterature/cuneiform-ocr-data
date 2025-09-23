# standard imports
import json
from collections import defaultdict
import os
from pathlib import Path

# package imports
from PIL import Image

# local imports
from crop_ocr_signs.extract_data import read_json_file
from crop_ocr_signs.filter_functions import natural_key
########################################################
# copied from convert_to_coco_det_and_rec to avoid unnecessary imports 
CLASSES = ['ABZ579', 'ABZ13', 'ABZ480', 'ABZ70', 'ABZ597', 'ABZ342', 'ABZ461', 'ABZ381', 'ABZ1', 'ABZ61', 'ABZ142', 'ABZ318', 'ABZ231', 'ABZ533', 'ABZ449', 'ABZ75', 'ABZ354', 'ABZ139', 'ABZ545', 'ABZ536', 'ABZ330', 'ABZ308', 'ABZ15', 'ABZ86', 'ABZ73', 'ABZ214', 'ABZ328', 'ABZ55', 'ABZ296', 'ABZ371', 'ABZ68', 'ABZ295', 'ABZ537', 'ABZ411', 'ABZ457', 'ABZ5', 'ABZ335', 'ABZ151', 'ABZ69', 'ABZ366', 'ABZ396', 'ABZ324', 'ABZ99', 'ABZ206', 'ABZ353', 'ABZ84', 'ABZ532', 'ABZ384', 'ABZ58', 'ABZ376', 'ABZ59', 'ABZ74', 'ABZ334', 'ABZ399', 'ABZ97', 'ABZ52', 'ABZ586', 'ABZ7', 'ABZ211', 'ABZ145', 'ABZ383', 'ABZ589', 'ABZ367', 'ABZ319', 'ABZ343', 'ABZ85', 'ABZ144', 'ABZ570', 'ABZ78', 'ABZ115', 'ABZ212', 'ABZ207', 'ABZ465', 'ABZ322', 'ABZ112', 'ABZ38', 'ABZ331', 'ABZ427', 'ABZ60', 'ABZ79', 'ABZ80', 'ABZ314', 'ABZ142a', 'ABZ595', 'ABZ232', 'ABZ535', 'ABZ279', 'ABZ172', 'ABZ312', 'ABZ6', 'ABZ554', 'ABZ230', 'ABZ128', 'ABZ468', 'ABZ167', 'ABZ401', 'ABZ575', 'ABZ12', 'ABZ313', 'ABZ148', 'ABZ339', 'ABZ104', 'ABZ331e+152i', 'ABZ472', 'ABZ306', 'ABZ134', 'ABZ2', 'ABZ441', 'ABZ412', 'ABZ147', 'ABZ471', 'ABZ397', 'ABZ62', 'ABZ111', 'ABZ455', 'ABZ72', 'ABZ538', 'ABZ143', 'ABZ101', 'ABZ440', 'ABZ437', 'ABZ393', 'ABZ298', 'ABZ50', 'ABZ483', 'ABZ559', 'ABZ87', 'ABZ94', 'ABZ152', 'ABZ138', 'ABZ164', 'ABZ565', 'ABZ205', 'ABZ598a', 'ABZ307', 'ABZ9', 'ABZ398', 'ABZ191', 'ABZ126', 'ABZ124', 'ABZ195', 'ABZ470', 'ABZ131', 'ABZ375', 'ABZ56', 'ABZ556', 'ABZ170']

def count_unique_fragments_in_ocred_json():
    ocred_json = read_json_file()
    filenames = {item["filename"] for item in ocred_json}
    count = len(filenames) 
    return count
 

def count_unique_fragments_from_cropped_photos():
    root_folder = Path("data_from_ocrjson")
    middle_bits = set()
    num_of_signs = defaultdict(lambda: {"count":0, "sign_name":""})
    # Search for all .jpg files recursively
    for jpg_file in root_folder.rglob("*.jpg"):
        filename = jpg_file.name
        sign_name, fragment_name = filename.split('_')[:2]
        middle_bits.add(fragment_name)
        if not num_of_signs[f"{jpg_file.parent.name}"]["sign_name"]: 
            num_of_signs[f"{jpg_file.parent.name}"]["sign_name"] = sign_name
        num_of_signs[f"{jpg_file.parent.name}"]["count"] += 1

    num_of_signs_sorted = {key: num_of_signs[key] for key in sorted(num_of_signs, key=natural_key)}

    return len(middle_bits), num_of_signs_sorted

def open_posix_path_jpg(p):
    with Image.open(p) as img:
        img.show()           # Opens with default viewer
        print(img.format)    # JPEG
        print(img.size)  

def count_crops_to_delete(file_path="crop_ocr_signs/verify_signs/no_partial_order_x1.txt"):
    """Count crops which have no partial ordering."""
    counts = defaultdict(int)

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            folder_name = Path(line).parts[1]
            counts[folder_name] += 1
    crops_to_delete = {key: counts[key] for key in sorted(counts, key=natural_key)}
    return crops_to_delete 

def calculate_crops_percentage(crops_to_delete, num_of_signs_dict):
    return { k: {"proportion": round(v/num_of_signs_dict[k]['count'], 3), "total": num_of_signs_dict[k]['count'] }for k, v in crops_to_delete.items() }

if __name__ == '__main__':
    cropped_signs_folder_name = "data_from_ocrjson"

    unique_fragments, num_of_signs_dict = count_unique_fragments_from_cropped_photos()
    # print(f"Count of unique fragments in cropped images: {unique_fragments}") # 18888
    # print(f"Count of cropped signs: {sum(num_of_signs_dict.values())}")  
    
    crops_to_delete = count_crops_to_delete() 

    crop_percentages = calculate_crops_percentage(crops_to_delete, num_of_signs_dict)
    output_folder_path = 'crop_ocr_signs/stats'
    os.makedirs(output_folder_path, exist_ok=True)
    with open(f"{output_folder_path}/no_partial_order_percentages.json", 'a', encoding='utf-8') as f:
        json.dump(crop_percentages, f)

