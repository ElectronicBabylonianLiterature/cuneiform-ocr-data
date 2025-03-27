# standard imports
import json
# package imports
from pymongo import ReturnDocument
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

    doc = fragments.find_one_and_update({'_id': fragment_name},{'$set': {'signs': ocred_signs_for_one_file}},return_document=ReturnDocument.AFTER)

    breakpoint()


