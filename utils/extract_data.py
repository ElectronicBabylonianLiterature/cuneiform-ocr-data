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
Image.MAX_IMAGE_PIXELS = 300000000

def get_annotated_fragments_ids(fragments_collection):
    """Get fragment ids in a Python set"""
    annotated_fragments_ids = set()
    for fragment in fragments_collection.find():
        annotated_fragments_ids.add(fragment.get('fragmentNumber'))
    return annotated_fragments_ids

def read_json_file(file_name):
    with open(file_name) as f:
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

def retrieve_image_from_filename(file_name, photos):
    """Find photo base64string and return image object (Pillow)"""
    photo_file = photos.find_one({"filename": file_name})
    file_data = photo_file.read()
    image = decode_binary_to_image(file_data)
    return image


if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    fragments = db['fragments']
    annotations = db['annotations']

    # exclude fragments with no transliteration and fragments already annotated
    non_empty_fragments_query = {"text.lines.0": {"$exists": True}}
    annotated_fragments_ids = get_annotated_fragments_ids(annotations)
    filter_query = {"_id": {"$in": list(annotated_fragments_ids)}}
    fragments_to_match = fragments.find({**non_empty_fragments_query, **filter_query})
    count = fragments.count_documents({**non_empty_fragments_query, **filter_query})
    print(count)


    # match signs in json with signs in fragments with transliteration
    file_name = "eBL_OCRed_Signs.json"
    ocr_signs_array = read_json_file(file_name)
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)
    metadata_list = []
    for fragment in tqdm(fragments_to_match):
        fragment_name = fragment.get('_id')
        file_name = f"{fragment_name}.jpg"
        ocr_signs_item_to_match = ocr_signs_dict.get(file_name)
        if not ocr_signs_item_to_match: continue
        filtered_signs_with_position = match_signs_from_fragment(fragment["signs"], ocr_signs_item_to_match["ocredSigns"])
        # TODO: get basic stats for this 'naive' match. Then attempet spatial join by getting geometry data from `annotations`

        # extract photos
        photos = gridfs.GridFS(db, collection="photos")
        image = retrieve_image_from_filename(file_name, photos)
        for sign, index in filtered_signs_with_position:
            coordinates_list = ocr_signs_item_to_match["ocredSignsCoordinates"]
            coordinates = coordinates_list[index]
            crop = crop_image(image, coordinates)

            # generate abz sign
            abz_sign_dict = build_abz_dict()
            sign_reading = abz_sign_dict[sign]

            # save to file with metadata
            folder_path = f"data/{sign}"
            os.makedirs(folder_path, exist_ok=True)
            crop_file_name = f"{sign_reading}_{fragment_name}_{index}.jpg"
            image_path = os.path.join(folder_path, crop_file_name)
            crop.save(image_path)

            metadata = {
                "source_image": file_name,
                "sign": sign,
                "sign_reading": sign_reading,
                "image_coordinates_index": index
            }
            metadata_list.append(metadata)

        metadata_file = "data/crops_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata_list, f, indent=4)

