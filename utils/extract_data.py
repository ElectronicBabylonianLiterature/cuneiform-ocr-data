# standard imports
import os
import json
import base64
from io import BytesIO

# package imports
from pymongo import ReturnDocument
from PIL import Image
import gridfs
from tqdm import tqdm

# local imports
from connection import get_connection
from cuneiform_ocr_data.sign_mappings.mappings import build_abz_dict
########################################################
Image.MAX_IMAGE_PIXELS = 500000000
JSON_FILE_NAME = "eBL_OCRed_Signs.json"

def get_annotated_fragments_ids(annotations):
    """Get fragment ids in a Python set"""
    annotated_fragments_ids = set()
    for fragment in annotations.find():
        annotated_fragments_ids.add(fragment.get('fragmentNumber'))
    return annotated_fragments_ids

def return_fragments_to_match(db):
    """Exclude fragments with no transliteration and fragments already annotated"""
    fragments = db['fragments']
    annotations = db['annotations']
    non_empty_fragments_query = {"text.lines.0": {"$exists": True}}
    annotated_fragments_ids = get_annotated_fragments_ids(annotations)
    filter_query = {"_id": {"$nin": list(annotated_fragments_ids)}}
    fragments_to_match = fragments.find({**non_empty_fragments_query, **filter_query})
    print(fragments.count_documents({**non_empty_fragments_query, **filter_query}))
    return fragments_to_match

def read_json_file():
    with open(JSON_FILE_NAME) as f:
        return json.load(f)

def transform_signs_array_to_signs_dict(ocr_signs_array):
    return {item["filename"]: item for item in ocr_signs_array}


def match_signs_from_fragment(fragment_signs: str, ocr_signs: str):
    """Return signs (with position in list) which also occur in the fragment's signs"""
    fragment_signs_set = set(fragment_signs.split())
    fragment_signs_set.discard('X')
    ocr_signs_array = ocr_signs.split()
    ocr_signs_with_index = [(sign, i) for i, sign in enumerate(ocr_signs_array)]
    filtered_ocr_signs_with_index = [item for item in ocr_signs_with_index if item[0] in fragment_signs_set]
    return filtered_ocr_signs_with_index

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

def sort_cropped_signs(db, fragments_to_match, metadata_list, abz_sign_dict):
    """Crop desired signs in image, then save sign extracts with source file_name and position of signs."""
    for fragment in tqdm(fragments_to_match):
        fragment_name = fragment.get('_id')
        file_name = f"{fragment_name}.jpg"
        ocr_signs_item_to_match = ocr_signs_dict.get(file_name)
        if not ocr_signs_item_to_match: continue
        filtered_signs_with_position= match_signs_from_fragment(fragment["signs"], ocr_signs_item_to_match["ocredSigns"])

        # extract photos
        image = retrieve_image_from_filename(file_name, db)
        if not image:
            print(f"{file_name} has no image")
            continue
        for sign, index in filtered_signs_with_position:
            coordinates = ocr_signs_item_to_match["ocredSignsCoordinates"][index]
            crop = crop_image(image, coordinates)
            sign_reading = abz_sign_dict[sign]
            output_sign_crop(sign, sign_reading, fragment_name, index, crop)

            metadata = {
                "source_image": file_name,
                "sign": sign,
                "sign_reading": sign_reading,
                "image_coordinates_index": index
            }
            metadata_list.append(metadata)

def output_sign_crop(sign, sign_reading, fragment_name, index, crop):
    """Write to file"""
    folder_path = f"data/{sign}"
    os.makedirs(folder_path, exist_ok=True)
    crop_file_name = f"{sign_reading}_{fragment_name}_{index}.jpg"
    image_path = os.path.join(folder_path, crop_file_name)
    crop.save(image_path)


def save_metadata(metadata_list):
    metadata_file = "data/crops_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata_list, f, indent=4)


if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    fragments_to_match = return_fragments_to_match(db)

    # match signs in json with signs in fragments with transliteration
    ocr_signs_array = read_json_file()
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)
    abz_sign_dict = build_abz_dict()
    metadata_list = []
    sort_cropped_signs(db, fragments_to_match, metadata_list, abz_sign_dict)
    save_metadata(metadata_list)
