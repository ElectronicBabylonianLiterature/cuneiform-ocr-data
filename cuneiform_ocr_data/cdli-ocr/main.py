from pathlib import Path

import pandas as pd

from cuneiform_ocr_data.bounding_boxes import BoundingBox, BoundingBoxesContainer
from cuneiform_ocr_data.classification.utils import build_ebl_dict

unmapped = set()
"""
not_even_in_custom_mapping = ['Dish',
'Four',
'Three']

custom_mapping = {
    'Nin' : "ABZ556",
    'i3': "ABZ231",
    'He2': "ABZ143",
'Dab5': "ABZ 536",
'Gid2': "ABZ371",
'Sza': "ABZ353",
'Iri': "ABZ38",
'Gu2': "ABZ106",
'Ga2': "ABZ233",
'U8': " ABZ494",
'Sze3': "ABZ536",
'Lu2': "ABZ330",
'Ge6' : "ABZ427",
'Utu': "ABZ381",
'Bi2': "ABZ172",
'Gal2' : "ABZ80",
'Nin9',
'One',
'U2',
'Gin2',
'Udu',
'Gub',
'Inim',
'zah3',
'Nesag',
'Ke4',
'Gish',
'Six',
'Gesz',
'Two',
'E2',
'Hul'}
"""

def parse_signs(signs: str, image_id: str, mapping):
    signs = signs.split("-")
    bboxes = []
    for sign in signs:
        elems = sign.split(":")
        sign_class = elems[0]
        coordinates = list(map(int,elems[1:]))
        if mapping is None:
            sign_class = "x"
        else:
            raise NotImplementedError
        bbox = BoundingBox.from_two_vertices(coordinates, sign_class)
        bboxes.append(bbox)
    return BoundingBoxesContainer(image_id, bboxes)


if __name__ == "__main__":
    annotations_csv = "data/raw-data/cdli-ocr/detection/annotation.csv"
    # read csv using panda
    df = pd.read_csv(annotations_csv)
    print(df.head())
    # iterate through rows of df
    #mapping = build_ebl_dict()
    mapping = None

    bboxes = []
    for index, row in df.iterrows():
        # turn series into list
        size, image_id, lines, line_coordinates, num_of_signs, signs = row.tolist()
        box = parse_signs(signs, image_id.split(".png")[0], mapping)
        box.create_ground_truth_txt(Path("data/processed-data/cdli-ocr/detection/annotations"))
        bboxes.append(box)

    print(unmapped)
    print("Lenght unmapped: ", len(unmapped))
    print("Done")
