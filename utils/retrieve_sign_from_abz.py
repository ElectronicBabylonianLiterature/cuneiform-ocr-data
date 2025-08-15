
from cuneiform_ocr_data.sign_mappings.mappings import build_abz_dict
from utils.filter_functions import construct_kv_pairs_of_disambiguated_abz_reading

def convert_abz_array_to_sign_name_array(ocred_signs_array):
    abz_sign_dict = build_abz_dict()
    disambiguated_kv_pairs = construct_kv_pairs_of_disambiguated_abz_reading()
    abz_sign_dict.update(disambiguated_kv_pairs)
    invalid_signs = ['X']
    return [abz_sign_dict[abl] for abl in ocred_signs_array if abl not in invalid_signs]


if __name__ == '__main__':
    abl = "ABZ480"
    abz_sign_dict = convert_abz_array_to_sign_name_array()
    sign_reading = abz_sign_dict[abl]
    print(sign_reading)




