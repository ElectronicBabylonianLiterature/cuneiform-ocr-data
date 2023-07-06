import os
from pathlib import Path

import mmcv

mmcv.use_backend("pillow")
from PIL import Image


def validate_img(file):
    try:
        img = Image.open(file)
        if mmcv.imread(file) is None:
            print(f"Could not read {file}")
        k = mmcv.imfrombytes(open(file, "rb").read())
        if k is None:
            print(f"Could not read {file}")
        img.verify()
        img.close()
    except (IOError, SyntaxError) as e:
        print("Bad file:", file)
        os.remove(file)


if __name__ == "__main__":
    imgs_path = Path("data/ebl")
    for dir in imgs_path.iterdir():
        if dir.is_dir():
            for sign_dir in dir.iterdir():
                for dir in sign_dir.iterdir():
                    for file in dir.iterdir():
                        validate_img(file)
