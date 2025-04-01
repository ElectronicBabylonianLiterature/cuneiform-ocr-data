
from cuneiform_ocr_data.sign_mappings.mappings import build_abz_dict

if __name__ == '__main__':
    abl = "ABZ411"
    abz_sign_dict = build_abz_dict()
    sign_reading = abz_sign_dict[abl]
    print(sign_reading)




