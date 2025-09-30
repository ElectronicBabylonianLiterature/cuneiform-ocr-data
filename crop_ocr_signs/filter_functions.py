import json
import re
import traceback

from cuneiform_ocr_data.sign_mappings.mappings import build_abz_to_signs_dict, build_sign_to_abz_dict
from crop_ocr_signs.connection import get_connection

########################################################
def generate_value_to_abz_dict(signs_coll, sign_to_abz_dict):
    """Get sign array with info"""
    value_to_abz_dict = dict()
    for entry in signs_coll.find(
            {"values": {"$exists": True, "$ne": [], "$type": "array"}},
            {"_id": 1, "values": 1} 
        ):
        try:
            values_with_subindex_one = [v["value"] + str(v.get("subIndex", "x")) for v in entry["values"]]
            values = [v[:-1] for v in values_with_subindex_one if v.endswith('1')]
            sign_name = entry["_id"]
            abz_num = sign_to_abz_dict[sign_name]
            for value in values:
               value_to_abz_dict[value] = abz_num
        except Exception as e:
            error_info = {
                "message": str(e),
                "traceback": traceback.format_exc()
            }
    return value_to_abz_dict


def write_fragment_text_lines(fragment_text_lines):
    with open("crop_ocr_signs/fragment_text_object.json", "w", encoding="utf-8") as f:
        json.dump(fragment_text_lines,f, indent=2)

def fragment_text_from_db():
    fragments = db['fragments']
    fragment_number = "1879,0708.124" 
    fragment_object = fragments.find_one({"_id": fragment_number})
    fragment_text_lines = fragment_object["text"]["lines"]
    return fragment_text_lines 
    

def write_abz_with_more_than_one_value_dict():
    abz_to_signs_dict = build_abz_to_signs_dict()
    ocred_abz_to_sign_dict = {k:v for k,v in abz_to_signs_dict.items() if k in signs_outputted_from_ocr}
    unsorted_abz_with_more_than_one_value = {k:v for k,v in ocred_abz_to_sign_dict.items() if len(v) > 1}
    abz_with_more_than_one_value = {key: unsorted_abz_with_more_than_one_value[key] for key in sorted(unsorted_abz_with_more_than_one_value, key=natural_key)}
    with open("crop_ocr_signs/convenience_methods/abz_with_more_than_one_value.json", "w", encoding="utf-8") as f:
        json.dump(abz_with_more_than_one_value, f, ensure_ascii=False, indent=4)


signs_outputted_from_ocr = ['ABZ1', 'ABZ279', 'ABZ384', 'ABZ537', 'ABZ15', 'ABZ13', 'ABZ342', 'ABZ354', 'ABZ381', 'ABZ206', 'ABZ318', 'ABZ449', 'ABZ69', 'ABZ597', 'ABZ75', 'ABZ231', 'ABZ295', 'ABZ58', 'ABZ545', 'ABZ214', 'ABZ144', 'ABZ533', 'ABZ151', 'ABZ70', 'ABZ324', 'ABZ139', 'ABZ343', 'ABZ461', 'ABZ52', 'ABZ142', 'ABZ399', 'ABZ99', 'ABZ427', 'ABZ586', 'ABZ579', 'ABZ480', 'ABZ470', 'ABZ101', 'ABZ68', 'ABZ211', 'ABZ172', 'ABZ86', 'ABZ128', 'ABZ59', 'ABZ328', 'ABZ230', 'ABZ366', 'ABZ296', 'ABZ74', 'ABZ61', 'ABZ331e+152i', 'ABZ313', 'ABZ371', 'ABZ376', 'ABZ232', 'ABZ457', 'ABZ5', 'ABZ383', 'ABZ396', 'ABZ589', 'ABZ353', 'ABZ55', 'ABZ308', 'ABZ167', 'ABZ73', 'ABZ411', 'ABZ536', 'ABZ112', 'ABZ334', 'ABZ367', 'ABZ319', 'ABZ7', 'ABZ570', 'ABZ306', 'ABZ397', 'ABZ212', 'ABZ147', 'ABZ80', 'ABZ104', 'ABZ575', 'ABZ207', 'ABZ532', 'ABZ145', 'ABZ84', 'ABZ335', 'ABZ60', 'ABZ401', 'ABZ115', 'ABZ170', 'ABZ330', 'ABZ79', 'ABZ38', 'ABZ312', 'ABZ78', 'ABZ111', 'ABZ97', 'ABZ535', 'ABZ12', 'ABZ595', 'ABZ72', 'ABZ85', 'ABZ322', 'ABZ314', 'ABZ554', 'ABZ339', 'ABZ9', 'ABZ6', 'ABZ143', 'ABZ468', 'ABZ62', 'ABZ191', 'ABZ331', 'ABZ437', 'ABZ87', 'ABZ94', 'ABZ138', 'ABZ398', 'ABZ598a', 'ABZ440', 'ABZ465', 'ABZ152', 'ABZ134', 'ABZ393', 'ABZ298', 'ABZ50']


def natural_key(s):
    "Sort by ABZ1, ABZ5...and not ABZ1, ABZ101"
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def construct_kv_pairs_of_disambiguated_abz_reading():
    """
    Disambiguate between 
    e.g.   "ABZ15": ["KA", "|KA\u00d7GIR\u2082|"], -> KA is the one being read. 
    Discard the latter one.
    Function takes first reading for each ABZ by default. E.g. 
      "ABZ60": ["PAP", "|PAP.PAP\u00d7\u0160E|"],
    -> 
    PAP will be obtained. 
    """
    dict_with_values_to_update = {
        "ABZ52": "|UD\u00d7(U.U.U)|",
        "ABZ58": "TU",
        "ABZ74": "BAR",
        "ABZ295": "PA",
        "ABZ331": "\u0160E\u0160", # ŠEŠ
        "ABZ384": "\u0160A\u2083", # ŠA₃
        "ABZ536": "KU",
        "ABZ545": "\u0160U\u2082", # ŠU₂
        "ABZ586": "ZA"
    }
    with open("crop_ocr_signs/convenience_methods/abz_with_more_than_one_value.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        dict_with_unique_reading = {k:v[0] for k, v in data.items()}
        dict_with_unique_reading.update(dict_with_values_to_update) 
        return dict_with_unique_reading


if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    signs = db['signs']
    sign_to_abz_dict = build_sign_to_abz_dict()
    value_to_abz_dict = generate_value_to_abz_dict(signs, sign_to_abz_dict)
