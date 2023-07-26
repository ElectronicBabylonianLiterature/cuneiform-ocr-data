import shutil
from pathlib import Path
import pandas as pd

from cuneiform_ocr_data.sign_mappings.mappings import build_ebl_dict
from cuneiform_ocr_data.utils import create_directory


def revert_dict(d):
    reverted = {}
    for k, v in d.items():
        reverted.setdefault(v, []).append(k)
    return reverted


def read_cdp(path):
    df = pd.read_excel(path, keep_default_na=False)
    df = df[["filename", "sign_new"]].values.tolist()
    return {filename: sign for filename, sign in df}


if __name__ == "__main__":
    destination = Path("data/processed-data/classification/urschrei-CDP-processed")
    create_directory(destination, overwrite=True)
    ebl = build_ebl_dict()
    ebl_revert = revert_dict(ebl)

    map0 = read_cdp(
        "cuneiform_ocr_data/classification/cdp/corrected_instances_forimport.xlsx"
    )
    map1 = read_cdp("cuneiform_ocr_data/classification/cdp//instance_cleaned_wip.xls")

    empty_values = [k for k, v in map0.items() if v == ""]
    for empty_value in empty_values:
        map0[empty_value] = map1[empty_value]

    unmapped_files = []
    unmapped_signs = {}
    for file in Path("data/raw-data/urschrei-CDP").iterdir():
        file_id = file.stem
        mapped_to = map0.get(file_id)
        if mapped_to is None:
            unmapped_files.append(file_id)
        else:
            oracc_sign = [x for x in ebl_revert.values() if mapped_to in x]
            if len(oracc_sign) == 0:
                unmapped_signs[mapped_to] = unmapped_signs.get(mapped_to, 0) + 1
            else:
                abz_sign = oracc_sign[0][0]
                shutil.copy(file, destination / f"{ebl[mapped_to]}_cdp_{file_id}.png")

    unmapped_signs = {
        k: v
        for k, v in sorted(
            unmapped_signs.items(), key=lambda item: item[1], reverse=True
        )
    }
    print()
    print(f"Could not find file for {len(unmapped_files)}")
    print(f"Could not find mapping for {len(unmapped_signs)}")
    print("Unmapped Signs: ", unmapped_signs)
    print("Done")
