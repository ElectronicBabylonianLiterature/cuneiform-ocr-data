import shutil
from functools import reduce
from pathlib import Path

from cuneiform_ocr_data.utils import create_directory, validate_imgs


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
        "cuneiform-ocr/cuneiform_ocr_data/classification/data/ebl", overwrite=True
    )
    data_ebl = prepare_data(
        Path("data/processed-data/classification/ebl+heidelberg/ebl+heidelberg-train")
    )
    data_cdp = prepare_data(
        Path("data/processed-data/classification/urschrei-CDP-processed")
    )
    data_jooch = prepare_data(
        Path("data/processed-data/classification/Cuneiform Dataset JOOCH")
    )
    data_labasi = prepare_labasi_data(Path("data/processed-data/classification/labasi"))

    data = merge_value_list_multiple_dicts(data_ebl, data_cdp, data_jooch, data_labasi)
    data_test = prepare_data(
        Path("data/processed-data/classification/ebl+heidelberg/ebl+heidelberg-test")
    )

    NOT_TO_INCLUDE = ["NoABZ", "NoABZ0"]
    for elem in NOT_TO_INCLUDE:
        data.pop(elem, None)
        data_test.pop(elem, None)

    print("Signs: ", len(data.keys()))
    print("Total Data:", len_values(data))
    MINIMUM_SAMPLE_SIZE = 75
    # only keep signs with more than 50 samples
    data = {k: v for k, v in data.items() if len(v) >= MINIMUM_SAMPLE_SIZE}
    # sort by length of list which is value in dict
    data = {
        k: v
        for k, v in sorted(data.items(), key=lambda item: len(item[1]), reverse=True)
    }

    classes = [f"{k} {len(v)}" for k, v in data.items()]
    print([f"{k} {len(v)}" for k, v in data.items()])
    # write classes as list to txt file

    class_to_int = {k: i for i, k in enumerate(data.keys())}
    print("ABZ Signs: ", data.keys())
    print("Number of imgs: ", len_values(data))
    print("Number of signs: ", len(data))

    """
    #Plot the number of images per sign
    print("Number of signs:", len(data))
    print("\n".join([f"{k} {v}" for k, v in data.items()]))

    ### matplotlib dict plot
    data1 = {k: len(v) for k, v in data.items()}
    import matplotlib.pyplot as plt
    plt.bar(range(len(data1.values())), data1.values())
    plt.xticks(rotation=90)
    plt.show()
    """

    test_category_not_in_train = {}
    train_category_not_in_test = {}
    train_data = data
    test_data = {}
    for k, v in data_test.items():
        if k in train_data.keys():
            test_data[k] = v
        else:
            print(f"Test data contains sign {k} which is not in train data")
            test_category_not_in_train[k] = v
    for k, v in train_data.items():
        if k not in test_data.keys():
            test_data[
                k
            ] = []  # need empty directory even if train data is not present in test set
            print(f"Train data contains sign {k} which is not in test data")
            train_category_not_in_test[k] = train_data[k]

    print("Test instances not in train: ", len_values(test_category_not_in_train))
    print("Train instances not in test: ", len_values(train_category_not_in_test))
    print()
    print(
        "Test Category not in train: ",
        list(set(list(test_category_not_in_train.keys()))),
    )
    train_data.pop("NoABZ", None)
    test_data.pop("NoABZ", None)
    print("Number of train signs:", len(train_data.keys()))
    print("Number of train imgs: ", len_values(train_data))
    print("Number of test signs:", len(test_data.keys()))
    print("Number of test imgs: ", len_values(test_data))

    # copy each file of value of train_data dict to directory
    create_directory(
        "cuneiform_ocr_data/classification/data/ebl/test_set/test_set",
        overwrite=True,
    )
    create_directory(
        "cuneiform_ocr_data/classification/ebl/train_set/train_set",
        overwrite=True,
    )
    _prep_data(
        test_data,
        Path("cuneiform_ocr_data/classification/data/ebl/test_set/test_set"),
        class_to_int,
        "test.txt",
    )

    _prep_data(
        train_data,
        Path("cuneiform_ocr_data/classification/data/ebl/train_set/train_set"),
        class_to_int,
        "train.txt",
    )

    with open("cuneiform_ocr_data/classification/data/ebl/classes.txt", "w") as f:
        f.write(str(list(data.keys())))

    imgs_path = Path("cuneiform_ocr_data/classification/data/ebl")
    validate_imgs(imgs_path)
