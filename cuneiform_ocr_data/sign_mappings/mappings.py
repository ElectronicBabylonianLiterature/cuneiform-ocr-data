from pathlib import Path

import pandas as pd


def build_ebl_dict():
    mapping = pd.read_csv(
        Path(Path(__file__).resolve().parent / "ebl.txt"),
        header=None,
        delimiter=" ",
        keep_default_na=False,
    ).values.tolist()
    mapping_dict = dict()
    for elem in mapping:
        sign, abz, _ = elem
        mapping_dict[sign] = abz
    return mapping_dict

def build_mzl_dict():
    mzl = pd.read_csv(
        Path(__file__).resolve().parent / "mzl.txt",
        header=None,
        keep_default_na=False,
    ).values.tolist()
    mzl_dict = dict()
    for elem in mzl:
        sign, number = elem[0].split(" ")
        mzl_dict[number] = sign
    return mzl_dict

def build_abz_dict():
    mapping = pd.read_csv(
        Path(Path(__file__).resolve().parent / "ebl.txt"),
        header=None,
        delimiter=" ",
        keep_default_na=False,
    ).values.tolist()
    mapping_dict = dict()
    for elem in mapping:
        sign, abz, _ = elem
        mapping_dict[abz] = sign
    return mapping_dict

def build_sign_to_abz_dict():
    mapping = pd.read_csv(
        Path(Path(__file__).resolve().parent / "ebl.txt"),
        header=None,
        delimiter=" ",
        keep_default_na=False,
    ).values.tolist()
    mapping_dict = dict()
    for elem in mapping:
        sign, abz, _ = elem
        mapping_dict[sign] = abz
    return mapping_dict

def build_sign_dict():
    sim_dict = {}
    with open('cuneiform_ocr_data/sign_mappings/ebl.txt', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split()
            if not parts:
                continue
            sign_name = parts[0]
            sign = parts[2]
            sim_dict[sign_name] = sign
    return sim_dict