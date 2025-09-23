import json
import pytest 
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


def remove_completions_from_transliteration(FRAGMENT_SIGNS_STRING, fragment_text_lines):
    filtered_transliteration = ''
    fragment_array = [line.strip() for line in FRAGMENT_SIGNS_STRING.splitlines() if line.strip()]
    indices_to_retain = get_fragment_indices_to_retain(fragment_text_lines)
    try:
        for i, array_str in enumerate(fragment_array):
            array = array_str.split()
            filtered = [array[j] for j in indices_to_retain[i] if j < len(array)]
            filtered_transliteration += ' '.join(filtered) + '\n'
    except Exception as e:
        error_info = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
    return filtered_transliteration 

@pytest.fixture 
def fragment_signs():
    return FRAGMENT_SIGNS_STRING 

FRAGMENT_SIGNS_STRING = ''' 
X ABZ401 X
ABZ401 ABZ461 ABZ457 ABZ73
ABZ401 ABZ461 ABZ457 ABZ73 ABZ597 ABZ470 X X X X X X X X X
ABZ480 ABZ99 ABZ87 ABZ15 ABZ55 ABZ376 ABZ80 ABZ85
ABZ61 ABZ231 ABZ1 ABZ461 ABZ61 ABZ483 ABZ115 ABZ296 ABZ401 ABZ296 ABZ314 ABZ342 ABZ13 ABZ360 ABZ114 ABZ457 ABZ78 ABZ393 ABZ231 ABZ537 ABZ69
ABZ69 ABZ1 ABZ354 ABZ112 ABZ401 ABZ461 ABZ457 ABZ73 ABZ597 ABZ470 ABZ480 ABZ449 ABZ106 ABZ401 ABZ296 ABZ401 ABZ296 ABZ314 ABZ342 ABZ381 ABZ206 ABZ13 ABZ323 ABZ533 ABZ68 ABZ533 ABZ480 ABZ87 ABZ111 ABZ533 ABZ231
ABZ69 ABZ411 ABZ411 ABZ318 ABZ61 ABZ231 ABZ1 ABZ461 ABZ570 ABZ296 ABZ314 ABZ342 ABZ480 ABZ384 ABZ75 ABZ68 ABZ381 ABZ84 ABZ381 ABZ393 ABZ61 ABZ480 ABZ366 ABZ60
ABZ61 ABZ231 ABZ461 ABZ570 150 ABZ449 ABZ296 ABZ536 ABZ533 ABZ322 ABZ533 ABZ230 ABZ533
ABZ411 ABZ401 ABZ461 ABZ457 ABZ73 ABZ597 ABZ470 ABZ480 ABZ449 ABZ106 ABZ401 ABZ296 ABZ314 ABZ342 ABZ208 ABZ401 ABZ597 150 ABZ296 ABZ69
ABZ381 ABZ354 ABZ7 ABZ366 ABZ10
ABZ13 ABZ360 ABZ114 ABZ80 ABZ172 ABZ1 ABZ38 ABZ331e+152i ABZ398
ABZ401 ABZ597 ABZ470 ABZ295 ABZ296 ABZ209 ABZ393 ABZ61 ABZ60 ABZ1 ABZ396 ABZ597 ABZ126 ABZ10
ABZ296 ABZ401 ABZ296 ABZ314 ABZ457 ABZ134 ABZ61 ABZ480 ABZ279
ABZ296 ABZ401 ABZ296 ABZ314
'''

@pytest.fixture
def target_signs():
    return TARGET_SIGNS_STRING

@pytest.fixture
def fragment_text_object():
    return read_fragment_text_object()

TARGET_SIGNS_STRING = '''
X ABZ401 X
ABZ461 ABZ457
ABZ461 ABZ457 ABZ73 ABZ597 ABZ470 X X X X X X X X
ABZ55 ABZ376 ABZ80 ABZ85
ABZ115 ABZ296 ABZ401 ABZ296 ABZ314 ABZ342 ABZ13 ABZ360 ABZ114 ABZ457 ABZ78 ABZ393 ABZ231 ABZ537 ABZ69
ABZ296 ABZ401 ABZ296 ABZ314 ABZ342 ABZ381 ABZ206 ABZ13 ABZ323 ABZ533 ABZ68 ABZ533 ABZ480 ABZ87 ABZ111 ABZ533 ABZ231
ABZ314 ABZ342 ABZ480 ABZ384 ABZ75 ABZ68 ABZ381 ABZ84 ABZ381 ABZ393 ABZ61 ABZ480 ABZ366 ABZ60
150 ABZ449 ABZ296 ABZ536 ABZ533 ABZ322 ABZ533 ABZ230 ABZ533
ABZ457 ABZ73 ABZ597 ABZ470 ABZ480 ABZ449 ABZ106 ABZ401 ABZ296 ABZ314 ABZ342 ABZ208 ABZ401 ABZ597 150 ABZ296 ABZ69
ABZ381 ABZ354 ABZ7 ABZ366 ABZ10
ABZ114 ABZ80 ABZ172 ABZ1 ABZ38 ABZ331e+152i ABZ398
ABZ597 ABZ470 ABZ295 ABZ296 ABZ209 ABZ393 ABZ61 ABZ60 ABZ1 ABZ396 ABZ597 ABZ126 ABZ10
ABZ401 ABZ296 ABZ314 ABZ457 ABZ134 ABZ61 ABZ480 ABZ279
ABZ401 ABZ296
''' 

def test_remove_completions_from_transliteration(fragment_signs, target_signs, fragment_text_object):
    """ 
    Check with { _id: "1879,0708.124" } 
    Not yet taken into account composite signs e.g. E3, KIMIN
    """
    trimmed_transliteration = remove_completions_from_transliteration(fragment_signs, fragment_text_object)


    assert trimmed_transliteration.strip() == target_signs.strip()
  
def write_fragment_text_lines(fragment_text_lines):
    with open("crop_ocr_signs/fragment_text_object.json", "w", encoding="utf-8") as f:
        json.dump(fragment_text_lines,f, indent=4)

def read_fragment_text_object():
    with open("crop_ocr_signs/fragment_text_object.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

def fragment_text_from_db():
    fragments = db['fragments']
    fragment_number = "1879,0708.124" 
    fragment_object = fragments.find_one({"_id": fragment_number})
    fragment_text_lines = fragment_object["text"]["lines"]
    return fragment_text_lines 
    
def flatten_line_content(line_content):
    """Flatten content of each line in fragment_object["text"]["lines"] """
    content_split_on_dash = [part for item in line_content for part in item.split('-')]
    # content = [part for item in content_split_on_dash for part in item.split('.')]
    content_split_on_dot = [ part for el in content_split_on_dash for part in re.split(r'(?<!\.)\.(?!\.)', el) ]
    content_no_indent = [el for el in content_split_on_dot if el != '($___$)']
    flat_list = [
        part
            for el in content_no_indent
            for part in ([el[el.find('{')+1 : el.find('}')], el[el.find('}')+1:]] if '{' in el and '}' in el else [el])
        ]
    content_no_ellipses = deal_with_ellipses(flat_list) 
    return content_no_ellipses

def deal_with_ellipses(content):
    content = [el for el in content if el != '[...]']
    result = []
    i = 0
    while i < len(content):
        el = content[i]
        
        if el == '[...':
            if i + 1 < len(content):
                result.append('[' + content[i + 1])  
                i += 2  # skip the next element
                continue
        if el == '...]':
            result[-1] += ']'
            i += 1
            continue
        
        # Keep other elements as is
        result.append(el)
        i += 1
    return result

def get_element_indices_not_in_square_brackets(content):
    result_indices = []
    inside_brackets = False

    for i, el in enumerate(content):
        if el.startswith('[') and el.endswith(']'):
            continue
        if '[' in el:
            inside_brackets = True
        if not inside_brackets:
            result_indices.append(i)
        if ']' in el:
            inside_brackets = False

    return result_indices

def get_fragment_indices_to_retain(fragment_text_lines):
    tablet_indices = []
    for line in fragment_text_lines:
        line_content = [unit["value"] for unit in line["content"] ]
        content = flatten_line_content(line_content)
        content_indices = get_element_indices_not_in_square_brackets(content)
  
        tablet_indices.append(content_indices)
    return tablet_indices

def write_abz_with_more_than_one_value_dict():
    abz_to_signs_dict = build_abz_to_signs_dict()
    ocred_abz_to_sign_dict = {k:v for k,v in abz_to_signs_dict.items() if k in signs_outputted_from_ocr}
    unsorted_abz_with_more_than_one_value = {k:v for k,v in ocred_abz_to_sign_dict.items() if len(v) > 1}
    abz_with_more_than_one_value = {key: unsorted_abz_with_more_than_one_value[key] for key in sorted(unsorted_abz_with_more_than_one_value, key=natural_key)}
    with open("crop_ocr_signs/abz_with_more_than_one_value.json", "w", encoding="utf-8") as f:
        json.dump(abz_with_more_than_one_value, f, indent=4)


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
    with open("crop_ocr_signs/abz_with_more_than_one_value.json", "r", encoding="utf-8") as f:
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

    # get fragment text and filter transliteration
    fragment_text_lines = read_fragment_text_object()

    filtered_transliteration = remove_completions_from_transliteration(FRAGMENT_SIGNS_STRING, fragment_text_lines) 