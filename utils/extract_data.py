# package imports
# file imports
from connection import get_connection
########################################################
def get_annotated_fragments_ids(fragments_collection):
    """Get fragment ids in a Python set"""
    annotated_fragments_ids = set()
    for fragment in fragments_collection.find():
        annotated_fragments_ids.add(fragment.get('fragmentNumber'))
    return annotated_fragments_ids


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
    breakpoint()

