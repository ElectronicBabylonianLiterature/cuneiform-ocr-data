import json
import pytest 

from cuneiform_ocr_data.sign_mappings.mappings import build_sign_to_abz_dict
from utils.connection import get_connection

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
            import traceback
            error_info = {
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            # print(error_info)
    return value_to_abz_dict


def remove_completions_from_transliteration(fragment_signs, fragment_text_lines):
    fragment_array = fragment_signs.split('\n')
    # for line in fragment_array:

    return 

@pytest.fixture 
def fragment_signs():
    return ''' 
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
    return '''
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

def test_remove_completions_from_transliteration(fragment_signs, target_signs):
    """ Check with { _id: "1879,0708.124" } """
    trimmed_transliteration = remove_completions_from_transliteration(fragment_signs)


    assert trimmed_transliteration == target_signs
  
def write_fragment_text_lines(fragment_text_lines):
    with open("utils/fragment_text_object.json", "w", encoding="utf-8") as f:
        json.dump(fragment_text_lines,f, indent=4)

def read_fragment_text_object():
    with open("utils/fragment_text_object.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

def fragment_text_from_db():
    fragments = db['fragments']
    fragment_number = "1879,0708.124" 
    fragment_object = fragments.find_one({"_id": fragment_number})
    fragment_text_lines = fragment_object["text"]["lines"]
    return fragment_text_lines 
    
if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    signs = db['signs']
    sign_to_abz_dict = build_sign_to_abz_dict()
    value_to_abz_dict = generate_value_to_abz_dict(signs, sign_to_abz_dict)

    # get fragment text and transliteration
    fragment_text_lines = read_fragment_text_object()
    tablet_indices = [[] for _ in range(len(fragment_text_lines))]
    for line_idx, line in enumerate(fragment_text_lines):
        content = [unit["value"] for unit in line["content"] if '...' not in unit["value"]]
        content = [part for item in content for part in item.split('-')]
        unit_after_break = 0
        unit_before_end_break = len(content)-1
        for i, unit_value in enumerate(content):
            if ']' in unit_value and i + 1 < len(content):
                unit_after_break = i + 1
                continue
        for i in range(unit_after_break, len(content)):
            if '[' in unit_value and i - 1 >= 0:
                unit_before_end_break = i - 1
            
        tablet_indices[line_idx].append((unit_after_break, unit_before_end_break))
        breakpoint()
    breakpoint()


        # if "]" in