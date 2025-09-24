from typing import Tuple

from crop_ocr_signs.connection import get_connection
from crop_ocr_signs.convenience_methods.show_crop_in_image import get_image_from_file_name
from crop_ocr_signs.extract_data import crop_image

def xywh_to_xyxy(coords: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """Convert (x, y, width, height) to (x1, y1, x2, y2)."""
    x, y, w, h = coords
    return x, y, x + w, y + h

def check_ocr_coordinates_match_sign():
    """
    fragment_number
    """
    photo_file_name = "K.2210.jpg"
    geometry = {
        "x": 51.4807302231237,
        "y": 19.2471406891957,
        "width": 13.5496957403651,
        "height": 3.79020616648776
    }
    target_sign = "SAG"
    geometry_tuple = (geometry["x"], geometry["y"], geometry["width"], geometry["height"])
    coordinates_xyxy = xywh_to_xyxy(geometry_tuple)


    client = get_connection()
    db = client['ebl']
    image = get_image_from_file_name(photo_file_name, db)
    if image:
        crop = crop_image(image, coordinates_xyxy)
        crop.show()

if __name__ == '__main__':
    check_ocr_coordinates_match_sign() 