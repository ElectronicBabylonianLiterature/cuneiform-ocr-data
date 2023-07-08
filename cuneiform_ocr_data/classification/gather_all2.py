import shutil
from functools import reduce
from pathlib import Path
import random

from cuneiform_ocr_data.path import create_directory


def _prep_data(data, path, class_to_int, txt_file_name):
    txt = ""
    for k, v in data.items():
        print(f"{k} and {len(v)}")
        create_directory(f"{path}/{k}", overwrite=True)
        for file in v:
            shutil.copyfile(file, f"{path}/{k}/{file.name}")
            txt += f"{k}/{file.name} {class_to_int[k]}\n"
    # write txt file
    with open(f"{path.parent.parent}/{txt_file_name}", "w") as f:
        f.write(txt)


def prepare_data(path):
    # Prepare data where all sign images are in one folder and the class is in the filename
    data = {}
    for file in path.iterdir():
        sign = file.stem.split("_")[0]
        data[sign] = [*data.get(sign, []), file]
    return data


def prepare_labasi_data(path):
    data = {}
    for dir in path.iterdir():
        data[dir.name] = list(dir.iterdir())
    return data


def merge_value_list_dict(d1, d2):
    return {k: [*d1.get(k, []), *d2.get(k, [])] for k in set(d1) | set(d2)}


def merge_value_list_multiple_dicts(*dicts):
    return reduce(merge_value_list_dict, dicts)


def len_values(data):
    return sum([len(v) for v in data.values()])


if __name__ == "__main__":
    create_directory(
        "./data", overwrite=True
    )
    random.seed(42)
    data = prepare_data(
        Path("/home/yunus/PycharmProjects/cuneiform-ocr-3/debug")
    )
    classes = [
        'ABZ579', 'ABZ13', 'ABZ342', 'ABZ70', 'ABZ461', 'ABZ142', 'ABZ480', 'ABZ1',
        'ABZ231', 'ABZ533', 'ABZ449', 'ABZ318', 'ABZ75', 'ABZ61', 'ABZ354',
        'ABZ139', 'ABZ381', 'ABZ597', 'ABZ536', 'ABZ308', 'ABZ330', 'ABZ328',
        'ABZ86', 'ABZ15', 'ABZ214', 'ABZ545', 'ABZ73', 'ABZ295', 'ABZ55', 'ABZ335',
        'ABZ371', 'ABZ151', 'ABZ457', 'ABZ537', 'ABZ69', 'ABZ353', 'ABZ68', 'ABZ5',
        'ABZ296', 'ABZ84', 'ABZ366', 'ABZ411', 'ABZ396', 'ABZ206', 'ABZ58',
        'ABZ324', 'ABZ376', 'ABZ99', 'ABZ384', 'ABZ59', 'ABZ532', 'ABZ334',
        'ABZ589', 'ABZ383', 'ABZ343', 'ABZ586', 'ABZ399', 'ABZ74', 'ABZ211',
        'ABZ145', 'ABZ7', 'ABZ212', 'ABZ78', 'ABZ367', 'ABZ38', 'ABZ319', 'ABZ85',
        'ABZ115', 'ABZ322', 'ABZ97', 'ABZ144', 'ABZ112', 'ABZ427', 'ABZ60',
        'ABZ207', 'ABZ79', 'ABZ80', 'ABZ232', 'ABZ142a', 'ABZ312', 'ABZ52',
        'ABZ331', 'ABZ128', 'ABZ314', 'ABZ535', 'ABZ575', 'ABZ134', 'ABZ465',
        'ABZ167', 'ABZ172', 'ABZ339', 'ABZ6', 'ABZ331e+152i', 'ABZ306', 'ABZ12',
        'ABZ2', 'ABZ148', 'ABZ397', 'ABZ554', 'ABZ570', 'ABZ441', 'ABZ147',
        'ABZ472', 'ABZ104', 'ABZ440', 'ABZ230', 'ABZ595', 'ABZ455', 'ABZ313',
        'ABZ298', 'ABZ412', 'ABZ62', 'ABZ468', 'ABZ101', 'ABZ111', 'ABZ483',
        'ABZ538', 'ABZ471', 'ABZ87', 'ABZ143', 'ABZ565', 'ABZ205', 'ABZ152',
        'ABZ72', 'ABZ138', 'ABZ401', 'ABZ50', 'ABZ406', 'ABZ307', 'ABZ126',
        'ABZ124', 'ABZ164', 'ABZ529', 'ABZ559', 'ABZ94', 'ABZ437', 'ABZ56',
        'ABZ393', 'ABZ398'
    ]
    data_ = {}
    for elem in classes:
        data_[elem] = data.get(elem, [])

    data = data_
    print([f"{k} {len(v)}" for k, v in data.items()])
    # write classes as list to txt file


    class_to_int = {k: i for i, k in enumerate(data.keys())}
    print("ABZ Signs: ", data.keys())
    print("Number of imgs: ", len_values(data))
    print("Number of signs: ", len(data))


    create_directory(
        "data/ebl/test_set/test_set",
        overwrite=True,
    )
    create_directory(
        "data/ebl/train_set/train_set",
        overwrite=True,
    )
    _prep_data(
        data,
        Path(
            "data/ebl/test_set/test_set"
        ),
        class_to_int,
        "test.txt",
    )

    _prep_data(
        data,
        Path(
            "data/ebl/train_set/train_set"
        ),
        class_to_int,
        "train.txt",
    )

    with open("data/ebl/classes.txt", "w") as f:
        f.write(str(data.keys()))



