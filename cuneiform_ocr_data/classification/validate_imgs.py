from pathlib import Path
from cuneiform_ocr_data.utils import validate_imgs

if __name__ == "__main__":
    # can be used to manually validate files and delete bad ones for classification
    imgs_path = Path("cuneiform_ocr_data/classification/data/ebl")
    validate_imgs(imgs_path)
