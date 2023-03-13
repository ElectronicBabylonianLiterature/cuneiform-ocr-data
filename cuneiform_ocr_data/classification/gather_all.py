import shutil
from functools import reduce
from pathlib import Path
import random

from cuneiform_ocr_data.path import create_directory


def _prep_data(data, path, class_to_int, txt_file_name):
    txt = ""
    for k, v in data.items():
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
        "../../../cuneiform-ocr/cuneiform_ocr/classification/data/ebl", overwrite=True
    )
    random.seed(42)
    data_lmu = prepare_data(Path("../../data/processed-data/classification/lmu-no-broken"))
    data_heidelberg = prepare_data(
        Path("../../data/processed-data/classification/heidelberg-no-broken")
    )
    data_cdp = prepare_data(Path("../../data/processed-data/classification/urschrei-CDP-processed"))
    data_jooch = prepare_data(
        Path("../../data/processed-data/classification/Cuneiform Dataset JOOCH processed")
    )
    data_labasi = prepare_labasi_data(
        Path("../../data/processed-data/classification/labasi")
    )

    data = merge_value_list_multiple_dicts(
      data_lmu, data_heidelberg, data_cdp, data_jooch, data_labasi
    )

    print("Signs: ",len(data.keys()))
    print("Total Data:", len_values(data))
    MINIMUM_SAMPLE_SIZE = 40
    data = {k: v for k, v in data.items() if len(v) >= MINIMUM_SAMPLE_SIZE}
    class_to_int = {k: i for i, k in enumerate(data.keys())}
    print("ABZ Signs: ",data.keys())


    print("Number of imgs: ", len_values(data))
    print("Number of signs: ", len(data))

    with open(
        "../../../cuneiform-ocr/cuneiform_ocr/classification/data/ebl/classes.txt", "w"
    ) as f:
        f.write("\n".join(data.keys()))
    """
    Plot the number of images per sign
    print("Number of signs:", len(data))
    print("\n".join([f"{k} {v}" for k, v in data.items()]))
    print(f"First Index with then Items: {list(data.values()).index(10)}")
    ### matplotlib dict plot
    import matplotlib.pyplot as plt
    plt.bar(range(len(data.values())), data.values())
    plt.xticks(rotation=90)
    plt.show()
    """
    # sort dict by values
    data = {
        k: random.sample(v, len(v))
        for k, v in sorted(data.items(), key=lambda item: len(item[1]), reverse=True)
    }
    print({k: len(v) for k, v in data.items()})
    test_data = {}
    train_data = {}
    SPLIT = 0.2

    for k, v in data.items():
        if len(v) >= MINIMUM_SAMPLE_SIZE:
            split = int(SPLIT * len(v))
            test_data[k] = v[:split]
            train_data[k] = v[split:]
    print("Number of signs:", len(train_data.keys()))



    # copy each file of value of train_data dict to directory
    create_directory(
        "../../../cuneiform-ocr/cuneiform_ocr/classification/data/ebl/test_set/test_set",
        overwrite=True,
    )
    create_directory(
        "../../../cuneiform-ocr/cuneiform_ocr/classification/data/ebl/train_set/train_set",
        overwrite=True,
    )
    _prep_data(
        test_data,
        Path(
            "../../../cuneiform-ocr/cuneiform_ocr/classification/data/ebl/test_set/test_set"
        ),
        class_to_int,
        "test.txt",
    )
    _prep_data(
        train_data,
        Path(
            "../../../cuneiform-ocr/cuneiform_ocr/classification/data/ebl/train_set/train_set"
        ),
        class_to_int,
        "train.txt",
    )


