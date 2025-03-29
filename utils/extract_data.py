# standard imports
import json
import base64
from io import BytesIO
# package imports
from pymongo import ReturnDocument
from PIL import Image
import gridfs
# local imports
from connection import get_connection
########################################################
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
    breakpoint()
    return filtered_ocr_signs_with_index


def generate_ocr_signs_to_coordinates_tuples(ocr_signs_entry, filtered_signs_with_position):
    """Return list of (ocr_sign, coordinates) tuples"""
    coordinates_list = ocr_signs_entry["ocredSignsCoordinates"]
    sign_coordinates_tuples = [(ocr_sign, coorddinates_list[i]) for ocr_sign, i in filtered_signs_with_position]
    return sign_coordinates_tuples

def decode_binary_to_image(img_binary):
    return Image.open(BytesIO(img_binary))

def crop_image(image, coordinates):
    return image.crop(coordinates)

def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

if __name__ == '__main__':
    client = get_connection()
    db = client['ebl']
    fragments = db['fragments']
    annotations = db['annotations']

    # exclude fragments with no transliteration and fragments already annotated
    non_empty_fragments_query = {"text.lines.0": {"$exists": True}}
    annotated_fragments_ids = get_annotated_fragments_ids(annotations)
    filter_query = {"_id": {"$nin": list(annotated_fragments_ids)}}
    fragments_to_match = fragments.find({**non_empty_fragments_query, **filter_query})

    # match signs in json with sings in fragments with transliteration
    file_name = "eBL_OCRed_Signs.json"
    ocr_signs_array = read_json_file(file_name)
    ocr_signs_dict = transform_signs_array_to_signs_dict(ocr_signs_array)
    for fragment in fragments_to_match:
        file_name = f"{fragment.get('_id')}.jpg"
        ocr_signs_item_to_match = ocr_signs_dict.get(file_name)
        if not ocr_signs_item_to_match: continue
        filtered_signs_with_position = match_signs_from_fragment(fragment["signs"], ocr_signs_item_to_match["ocredSigns"])

        breakpoint()

        # extract photos
        photos = gridfs.GridFS(db, collection="photos")
        for ocr_signs_fragment in ocr_signs_array[:1]:
            filename = ocr_signs_fragment.get("filename")
            # find photo base64string
            photo_file = photos.find_one({"filename": filename})
            file_data = photo_file.read()
            image = decode_binary_to_image(file_data)
            sign_coord_tuples = generate_ocr_signs_to_coordinates_tuples(ocr_signs_fragment, filtered_signs_with_position)
            for sign_coord_tuple in sign_coord_tuples:
                # TODO add tqdm progress bar
                sign_name, coordinates = sign_coord_tuple
                crop = crop_image(image, coordinates)
                sign_base_64 = encode_image_to_base64(crop)

                # to write: sign name, sign coord, source image
                metadata = {
                    "source_image": file_name,
                    "image_coordinates": coordinates
                }
                crop.show()

