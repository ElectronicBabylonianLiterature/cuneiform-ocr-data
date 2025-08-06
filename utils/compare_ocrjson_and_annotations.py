# standard imports
import os
import json
import base64
from io import BytesIO

# package imports
from PIL import Image
from tqdm import tqdm
from shapely.geometry import box

# local imports
from connection import get_connection
from cuneiform_ocr_data.sign_mappings.mappings import build_abz_dict
from models.models import SignCoordinates, Coordinates
from extract_data import get_annotated_fragments_ids, return_fragments_to_match
########################################################
JSON_FILE_NAME = "eBL_OCRed_Signs.json"


def read_json_file():
    with open(JSON_FILE_NAME) as f:
        return json.load(f)

def transform_signs_array_to_signs_dict(ocr_signs_array):
    return {item["filename"]: item for item in ocr_signs_array}


def decode_binary_to_image(img_binary):
    return Image.open(BytesIO(img_binary))

def crop_image(image, coordinates):
    return image.crop(coordinates)

def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def retrieve_image_from_filename(file_name, db):
    """Find photo base64string and return image object (Pillow)"""
    photos = gridfs.GridFS(db, collection="photos")
    photo_file = photos.find_one({"filename": file_name})
    if photo_file:
        file_data = photo_file.read()
        image = decode_binary_to_image(file_data)
        return image
    return None



if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    fragments_to_match = return_fragments_to_match(db)

    folder = 'data_from_ocrjson'

    # loop through OCRed signs to annotated sign 
    ocr_signs_array = read_json_file()

    folder_path = os.path.join(os.getcwd(),folder)

    for foldername in os.listdir(folder_path):
        if 'json' in foldername: continue
        print(foldername)
        for jpg in os.listdir(os.path.join(folder_path, foldername)):
            breakpoint()
            sign_name, fragment_number, index_in_ocred_json = jpg.split('.jpg')[0].split('_')
            breakpoint()