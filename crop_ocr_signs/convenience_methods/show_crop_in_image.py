# standard imports
from crop_ocr_signs.connection import get_connection

# local imports
from crop_ocr_signs.extract_data import crop_image, read_json_file, retrieve_image_from_filename, transform_signs_array_to_signs_dict
"""
Get crop from coordinates in OCRed json file. 
"""
########################################################
JSON_FILE_NAME = "eBL_OCRed_Signs.json"

def get_coordinates_for_cropped_sign(fragment_number, index, ocr_signs_dict):
    coordinates = ocr_signs_dict[fragment_number]["ocredSignsCoordinates"][index]
    return coordinates

def get_image_from_file_name(file_name, db):
    return retrieve_image_from_filename(file_name, db)

 
if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)

    photo_file_name = "K.13973.jpg"
    index = 0
    coordinates = get_coordinates_for_cropped_sign(photo_file_name, index, ocr_signs_dict)
    image = get_image_from_file_name(photo_file_name, db)
    if image:
        crop = crop_image(image, coordinates)
        crop.show()

