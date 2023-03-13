from datetime import datetime
from pathlib import Path

import requests

from cuneiform_ocr_data.path import create_directory

url = "http://labasi.acdh.oeaw.ac.at/data/api/signs/?limit=10&offset=10"
current = ""


def get_abz(url):
    abz_number = requests.get(url=url).json()["abz_number"]
    return f"ABZ{abz_number}"


OUTPUT = Path("../../data/processed-data/classification/labasi")


def get_signs(url):
    print(url)
    resp = requests.get(url=url)
    data = resp.json()
    for result in data["results"]:
        img_url = result["image"]
        if img_url is not None:
            sign_name = get_abz(result["sign"])
            try:
                create_directory(OUTPUT / sign_name, overwrite=False)
            except FileExistsError:
                pass

            resp = requests.get(url=img_url)
            name = f"{sign_name}_{result['identifier']}.{img_url.split('.')[-1]}"
            with open(OUTPUT / sign_name / name, "wb") as f:
                f.write(resp.content)
    if data["next"]:
        current = data["next"]
        get_signs(data["next"])


if __name__ == "__main__":
    url = "http://labasi.acdh.oeaw.ac.at/data/api/glyphs/?limit=100&offset=13000"
    try:
        get_signs(url)
    except ConnectionError as e:
        print(e)
        get_signs(current)
