# standard imports
import json
from collections import defaultdict
from pathlib import Path

# local imports
from extract_data import read_json_file
########################################################
# copied from convert_to_coco_det_and_rec to avoid unnecessary imports 
CLASSES = ['ABZ579', 'ABZ13', 'ABZ480', 'ABZ70', 'ABZ597', 'ABZ342', 'ABZ461', 'ABZ381', 'ABZ1', 'ABZ61', 'ABZ142', 'ABZ318', 'ABZ231', 'ABZ533', 'ABZ449', 'ABZ75', 'ABZ354', 'ABZ139', 'ABZ545', 'ABZ536', 'ABZ330', 'ABZ308', 'ABZ15', 'ABZ86', 'ABZ73', 'ABZ214', 'ABZ328', 'ABZ55', 'ABZ296', 'ABZ371', 'ABZ68', 'ABZ295', 'ABZ537', 'ABZ411', 'ABZ457', 'ABZ5', 'ABZ335', 'ABZ151', 'ABZ69', 'ABZ366', 'ABZ396', 'ABZ324', 'ABZ99', 'ABZ206', 'ABZ353', 'ABZ84', 'ABZ532', 'ABZ384', 'ABZ58', 'ABZ376', 'ABZ59', 'ABZ74', 'ABZ334', 'ABZ399', 'ABZ97', 'ABZ52', 'ABZ586', 'ABZ7', 'ABZ211', 'ABZ145', 'ABZ383', 'ABZ589', 'ABZ367', 'ABZ319', 'ABZ343', 'ABZ85', 'ABZ144', 'ABZ570', 'ABZ78', 'ABZ115', 'ABZ212', 'ABZ207', 'ABZ465', 'ABZ322', 'ABZ112', 'ABZ38', 'ABZ331', 'ABZ427', 'ABZ60', 'ABZ79', 'ABZ80', 'ABZ314', 'ABZ142a', 'ABZ595', 'ABZ232', 'ABZ535', 'ABZ279', 'ABZ172', 'ABZ312', 'ABZ6', 'ABZ554', 'ABZ230', 'ABZ128', 'ABZ468', 'ABZ167', 'ABZ401', 'ABZ575', 'ABZ12', 'ABZ313', 'ABZ148', 'ABZ339', 'ABZ104', 'ABZ331e+152i', 'ABZ472', 'ABZ306', 'ABZ134', 'ABZ2', 'ABZ441', 'ABZ412', 'ABZ147', 'ABZ471', 'ABZ397', 'ABZ62', 'ABZ111', 'ABZ455', 'ABZ72', 'ABZ538', 'ABZ143', 'ABZ101', 'ABZ440', 'ABZ437', 'ABZ393', 'ABZ298', 'ABZ50', 'ABZ483', 'ABZ559', 'ABZ87', 'ABZ94', 'ABZ152', 'ABZ138', 'ABZ164', 'ABZ565', 'ABZ205', 'ABZ598a', 'ABZ307', 'ABZ9', 'ABZ398', 'ABZ191', 'ABZ126', 'ABZ124', 'ABZ195', 'ABZ470', 'ABZ131', 'ABZ375', 'ABZ56', 'ABZ556', 'ABZ170']

def generate_statistics(metadata):
    stats = defaultdict(int)
    summary = dict()
    for d in metadata:
        sign = d["sign"]
        stats[sign] += 1
    summary["num_of_diff_signs"] = len(stats.keys())
    summary["sign_total"] = sum(stats.values())
    summary["fragments_total"] = len({item["source_image"] for item in metadata}) 
    return stats, summary

def load_json_metadata(cropped_signs_folder_name):
    with open(f"{cropped_signs_folder_name}/crops_metadata.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

def count_unique_fragments_in_ocred_json():
    ocred_json = read_json_file()
    filenames = {item["filename"] for item in ocred_json}
    count = len(filenames) 
    return count
 

def count_unique_fragments_from_cropped_photos():
    root_folder = Path("data_from_ocrjson")

    middle_bits = set()

    # Search for all .jpg files recursively
    for jpg_file in root_folder.rglob("*.jpg"):
        filename = jpg_file.name
        fragment_name = filename.split('_')[1]
        middle_bits.add(fragment_name)
    return len(middle_bits)


signs_outputted_from_ocr = ['ABZ1', 'ABZ279', 'ABZ384', 'ABZ537', 'ABZ15', 'ABZ13', 'ABZ342', 'ABZ354', 'ABZ381', 'ABZ206', 'ABZ318', 'ABZ449', 'ABZ69', 'ABZ597', 'ABZ75', 'ABZ231', 'ABZ295', 'ABZ58', 'ABZ545', 'ABZ214', 'ABZ144', 'ABZ533', 'ABZ151', 'ABZ70', 'ABZ324', 'ABZ139', 'ABZ343', 'ABZ461', 'ABZ52', 'ABZ142', 'ABZ399', 'ABZ99', 'ABZ427', 'ABZ586', 'ABZ579', 'ABZ480', 'ABZ470', 'ABZ101', 'ABZ68', 'ABZ211', 'ABZ172', 'ABZ86', 'ABZ128', 'ABZ59', 'ABZ328', 'ABZ230', 'ABZ366', 'ABZ296', 'ABZ74', 'ABZ61', 'ABZ331e+152i', 'ABZ313', 'ABZ371', 'ABZ376', 'ABZ232', 'ABZ457', 'ABZ5', 'ABZ383', 'ABZ396', 'ABZ589', 'ABZ353', 'ABZ55', 'ABZ308', 'ABZ167', 'ABZ73', 'ABZ411', 'ABZ536', 'ABZ112', 'ABZ334', 'ABZ367', 'ABZ319', 'ABZ7', 'ABZ570', 'ABZ306', 'ABZ397', 'ABZ212', 'ABZ147', 'ABZ80', 'ABZ104', 'ABZ575', 'ABZ207', 'ABZ532', 'ABZ145', 'ABZ84', 'ABZ335', 'ABZ60', 'ABZ401', 'ABZ115', 'ABZ170', 'ABZ330', 'ABZ79', 'ABZ38', 'ABZ312', 'ABZ78', 'ABZ111', 'ABZ97', 'ABZ535', 'ABZ12', 'ABZ595', 'ABZ72', 'ABZ85', 'ABZ322', 'ABZ314', 'ABZ554', 'ABZ339', 'ABZ9', 'ABZ6', 'ABZ143', 'ABZ468', 'ABZ62', 'ABZ191', 'ABZ331', 'ABZ437', 'ABZ87', 'ABZ94', 'ABZ138', 'ABZ398', 'ABZ598a', 'ABZ440', 'ABZ465', 'ABZ152', 'ABZ134', 'ABZ393', 'ABZ298', 'ABZ50']

if __name__ == '__main__':
    cropped_signs_folder_name = "data_from_ocrjson"
    metadata = load_json_metadata(cropped_signs_folder_name)
    stats, summary = generate_statistics(metadata)
    print(stats)
    print(summary)
    # print(len(CLASSES))
    # print(f"Count of unique fragments in OCRed Signs json: {count_unique_fragments_in_ocred_json()}") # 72423
    print(f"Count of unique fragments in cropped images: {count_unique_fragments_from_cropped_photos()}") # 18888
    breakpoint()
