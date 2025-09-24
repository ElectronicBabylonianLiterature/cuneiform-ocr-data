from typing import Tuple

import pytest

from crop_ocr_signs.connection import get_connection
from crop_ocr_signs.convenience_methods.show_crop_in_image import get_image_from_file_name
from crop_ocr_signs.extract_data import crop_image
################################################################

def xywh_to_xyxy(coords: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """Convert (x, y, width, height) to (x1, y1, x2, y2)."""
    x, y, w, h = coords
    return x, y, x + w, y + h

def from_relative_coordinates(
        relative_x,
        relative_y,
        relative_width,
        relative_height,
        image_width,
        image_height,
    ):
    absolute_x = int(round(relative_x / 100 * image_width))
    absolute_y = int(round(relative_y / 100 * image_height))
    absolute_width = int(round(relative_width / 100 * image_width))
    absolute_height = int(round(relative_height / 100 * image_height))

    return absolute_x, absolute_y, absolute_width, absolute_height

@pytest.mark.parametrize("photo_file_name, target_sign, geometry", [
    ("K.2210.jpg", "SAG", {
        "x": 51.4807302231237,
        "y": 19.2471406891957,
        "width": 13.5496957403651,
        "height": 3.79020616648776
    }),
    ('K.13973.jpg', 'BI', {
        "x": 20.486651649441068, 
        "y": 21.25577256559395, 
        "width": 12.258344883370038,
        "height": 6.828714212345857
    }) 
])
def test_check_ocr_coordinates_match_sign(photo_file_name, target_sign, geometry):
    client = get_connection()
    db = client['ebl']
    image = get_image_from_file_name(photo_file_name, db)

    geometry_tuple = (geometry["x"], geometry["y"], geometry["width"], geometry["height"])
    abs_geom = from_relative_coordinates(*geometry_tuple, *image.size) 
    abs_coords = xywh_to_xyxy(abs_geom)
    if image:
        crop = crop_image(image, abs_coords)
        crop.show()
        assert True
