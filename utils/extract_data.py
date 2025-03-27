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

def generate_ocr_signs_to_coordinates_tuples(ocr_signs_entry):
    ocr_signs_string = ocr_signs_entry["ocredSigns"]
    ocr_signs_array = ocr_signs_string.split()
    return list(zip(ocr_signs_array, ocr_signs_entry["ocredSignsCoordinates"]))

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
#    non_empty_fragments_query = {"text.lines.0": {"$exists": True}}
#    annotated_fragments_ids = get_annotated_fragments_ids(annotations)
#    filter_query = {"_id": {"$nin": list(annotated_fragments_ids)}}
#    fragments_to_match = fragments.find({**non_empty_fragments_query, **filter_query})

    # update "signs" for one fragment (test) (to do at the end in any case)
    file_name = "eBL_OCRed_Signs.json"
    ocr_signs_array = read_json_file(file_name)
    ocred_signs_for_one_file = ocr_signs_array[0].get("ocredSigns")
    fragment_name = ocr_signs_array[0].get("filename").split(".jpg")[0]

    # doc = fragments.find_one_and_update({'_id': fragment_name},{'$set': {'signs': ocred_signs_for_one_file}},return_document=ReturnDocument.AFTER)


    # extract photos
    photos = gridfs.GridFS(db, collection="photos")
    for ocr_signs_fragment in ocr_signs_array[:1]:
        filename = ocr_signs_fragment.get("filename")
        # find photo base64string
        photo_file = photos.find_one({"filename": filename})

        file_data = photo_file.read()

        image = decode_binary_to_image(file_data)

        sign_coord_tuples = generate_ocr_signs_to_coordinates_tuples(ocr_signs_fragment)
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
            breakpoint()
            crop.show()

