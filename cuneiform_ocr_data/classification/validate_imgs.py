from pathlib import Path


import mmcv

mmcv.use_backend("pillow")
from PIL import Image

if __name__ == "__main__":
    imgs_path = Path("./data")
    ## iterate through directory recursively with Path
    for counter, file in enumerate(imgs_path.rglob("*.jpg")):
        counter % 1000 == 0 and print(f"{counter} of {len(list(imgs_path.rglob('*.jpg')))}")
        try:
            img = Image.open(file)
            if mmcv.imread(file) is None:
                print(f"Could not read {file}")
            mmcv.imfrombytes(open(file, "rb").read())
            img.verify()
            img.close()  # to close img and free memory space
        except (IOError, SyntaxError) as e:
            print("Bad file:", file)
            # delete file
            file.unlink()
