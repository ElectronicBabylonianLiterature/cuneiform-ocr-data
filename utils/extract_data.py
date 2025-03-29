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
import geopandas as gpd
from shapely.geometry import box

# local imports
from connection import get_connection
from cuneiform_ocr_data.sign_mappings.mappings import build_abz_dict
from models.models import SignCoordinates, Coordinates
########################################################
Image.MAX_IMAGE_PIXELS = 300000000
JSON_FILE_NAME = "eBL_OCRed_Signs.json"

def get_annotated_fragments_ids(fragments_collection):
    """Get fragment ids in a Python set"""
    annotated_fragments_ids = set()
    for fragment in fragments_collection.find():
        annotated_fragments_ids.add(fragment.get('fragmentNumber'))
    return annotated_fragments_ids

def return_fragments_to_match(db):
    """Exclude fragments with no transliteration and fragments not already annotated"""
    fragments = db['fragments']
    annotations = db['annotations']
    non_empty_fragments_query = {"text.lines.0": {"$exists": True}}
    annotated_fragments_ids = get_annotated_fragments_ids(annotations)
    filter_query = {"_id": {"$in": list(annotated_fragments_ids)}}
    fragments_to_match = fragments.find({**non_empty_fragments_query, **filter_query})
    return fragments_to_match

def read_json_file():
    with open(JSON_FILE_NAME) as f:
        return json.load(f)

def transform_signs_array_to_signs_dict(ocr_signs_array):
    return {item["filename"]: item for item in ocr_signs_array}


def match_signs_from_annotations(annotations_fragment, ocr_signs_item_to_match: dict):
    """Return signs (with position in list) which also occur in the fragment's signs"""
    annotations_list = annotations_fragment.get("annotations")
    annotated_signs_coordinates = [SignCoordinates(i, obj["data"]["signName"], obj["geometry"])._asdict() for i, obj in enumerate(annotations_list)]

    ocr_signs_array = ocr_signs_item_to_match["ocredSigns"].split()
    ocr_signs_coordinates = [SignCoordinates(i, sign, Coordinates(*ocr_signs_item_to_match["ocredSignsCoordinates"][i])._asdict())._asdict() for i, sign in enumerate(ocr_signs_array)]

    join_df = join_signs_spatially(annotated_signs_coordinates, ocr_signs_coordinates)
    # TODO: convert join_df to filtered_ocr_signs_coordinates
    # TODO: filter if sign is X
    return filtered_ocr_signs_coordinates

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
    file_data = photo_file.read()
    image = decode_binary_to_image(file_data)
    return image

def join_signs_spatially(annotated_signs_coordinates, ocr_signs_coordinates):
    gdf_annotated = gpd.GeoDataFrame(annotated_signs_coordinates, geometry=[box(d["coordinates"]["x"], d["coordinates"]["y"], d["coordinates"]["x"] + d["coordinates"]["width"], d["coordinates"]["y"] + d["coordinates"]["height"]) for d in annotated_signs_coordinates], crs="EPSG:4326")
    gdf_ocr = gpd.GeoDataFrame(ocr_signs_coordinates, geometry=[box(d["coordinates"]["x"], d["coordinates"]["y"], d["coordinates"]["x"] + d["coordinates"]["width"], d["coordinates"]["y"] + d["coordinates"]["height"]) for d in ocr_signs_coordinates], crs="EPSG:4326")

    # TODO: convert the smaller coord system in annotated_signs_coordinates to the larger pixel coordinates!
    joined = gpd.sjoin(gdf_annotated, gdf_ocr, how="inner", predicate="intersects")

    significant_overlaps = filter_df_by_overlap_threshold(joined, gdf_ocr)
    breakpoint()


def filter_df_by_overlap_threshold(joined, gdf2):
    """Keep coordinates if intersection area/Union area (IoU) exceeds a certain threshold"""
    iou_threshold = 0.5
    significant_overlaps = []

    for _, row in joined.iterrows():
        box1 = row["geometry"]
        box2 = gdf2.loc[row["index_right"], "geometry"]

        intersection_area = box1.intersection(box2).area
        union_area = box1.area + box2.area - intersection_area
        iou = intersection_area / union_area if union_area > 0 else 0

        if iou > iou_threshold:
            significant_overlaps.append((*row, iou))
    return significant_overlaps

def sort_cropped_signs(db, fragments_to_match, metadata_list, abz_sign_dict):
    """Crop desired signs in image, then save sign extracts with source file_name and position of signs."""
    for fragment in tqdm(fragments_to_match):
        fragment_name = fragment.get('_id')
        file_name = f"{fragment_name}.jpg"
        ocr_signs_item_to_match = ocr_signs_dict.get(file_name)
        if not ocr_signs_item_to_match: continue
        annotations_fragment = db["annotations"].find_one({"fragmentNumber": fragment_name})
        filtered_signs_coordinates= match_signs_from_annotations(annotations_fragment, ocr_signs_item_to_match)

        # extract photos
        image = retrieve_image_from_filename(file_name, db)
        for index, sign, coordinates in filtered_signs_coordinates:
            crop = crop_image(image, coordinates)
            sign_reading = abz_sign_dict[sign]
            output_sign_crop(sign, sign_reading, fragment_name, index)

            metadata = {
                "source_image": file_name,
                "sign": sign,
                "sign_reading": sign_reading,
                "image_coordinates_index": index
            }
            metadata_list.append(metadata)

def output_sign_crop(sign, sign_reading, fragment_name, index):
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
