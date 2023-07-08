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
        "../../../cuneiform-ocr/cuneiform_ocr/classification/data/ebl", overwrite=True
    )
    random.seed(42)
    data_lmu = prepare_data(
        Path("../../data/processed-data/all_lmu+heidel/all_lmu_extracted_train_cropped")
    )
    data_cdp = prepare_data(
        Path("../../data/processed-data/classification/urschrei-CDP-processed")
    )
    data_jooch = prepare_data(
        Path(
            "../../data/processed-data/classification/Cuneiform Dataset JOOCH processed"
        )
    )
    data_labasi = prepare_labasi_data(
        Path("../../data/processed-data/classification/labasi")
    )

    data = merge_value_list_multiple_dicts(
        data_lmu, data_cdp, data_jooch, data_labasi
    )
    data_test = prepare_data(
        Path("../../data/processed-data/all_lmu+heidel/all_lmu_extracted_test_cropped")
    )
    SPLIT = 0.

    NOT_TO_INCLUDE = ["NoABZ", "NoABZ0"]

    """
    #Cluster = ['ABZ481', 'ABZ556', 'NoABZ2336', 'ABZ108', 'NoABZ2375', 'ABZ560', 'ABZ209', 'ABZ233', 'ABZ171', 'ABZ345', 'NoABZ829', 'ABZ191', 'ABZ63', 'ABZ192', 'ABZ439', 'ABZ129a', 'ABZ149', 'ABZ362', 'ABZ555', 'NoABZ1181', 'ABZ337', 'NoABZ658', 'ABZ8', 'NoABZ2105', 'ABZ129', 'ABZ122b', 'ABZ377', 'ABZ53', 'ABZ88', 'NoABZ2333', 'ABZ528', 'ABZ123', 'ABZ169', 'ABZ591', 'ABZ310', 'ABZ593', 'ABZ451', 'ABZ146', 'ABZ444', 'ABZ168', 'ABZ35', 'ABZ544', 'NoABZ2313', 'ABZ3', 'ABZ355', 'ABZ57', 'ABZ130', 'ABZ598a', 'ABZ309', 'NoABZ2127', 'NoABZ1195', 'ABZ573', 'ABZ76', 'ABZ574', 'ABZ425', 'ABZ435', 'NoABZ1501', 'NoABZ1350', 'ABZ114', 'ABZ200', 'ABZ406v2', 'ABZ546', 'NoABZ901', 'ABZ237', 'ABZ344', 'NoABZ2174', 'ABZ350', 'ABZ347', 'ABZ106', 'ABZ598', 'ABZ83', 'ABZ295m', 'NoABZ2179', 'ABZ592', 'NoABZ2368', 'ABZ87a', 'ABZ77', 'ABZ320', 'ABZ131', 'ABZ598n1', 'NoABZ1244', 'ABZ278', 'ABZ420', 'ABZ375', 'ABZ166', 'ABZ297', 'ABZ390', 'ABZ93', 'ABZ280', 'ABZ170a', 'ABZ215', 'ABZ9', 'ABZ454', 'ABZ433', 'ABZ446', 'ABZ325', 'ABZ541', 'ABZ374', 'ABZ402', 'ABZ456', 'ABZ557', 'ABZ540', 'ABZ323', 'ABZ459', 'ABZ336', 'ABZ78a', 'ABZ98', 'ABZ469', 'ABZ133', 'ABZ71', 'ABZ569', 'ABZ539', 'ABZ279', 'ABZ105', 'ABZ132', 'ABZ170', 'ABZ210', 'ABZ563', 'ABZ356', 'ABZ141', 'NoABZ2370', 'ABZ467', 'ABZ19', 'ABZ113', 'ABZ49', 'ABZ491', 'ABZ452v1', 'ABZ252', 'ABZ373', 'ABZ166b', 'ABZ400', 'ABZ36', 'ABZ515', 'ABZ470', 'ABZ81', 'NoABZ580', 'ABZ10', 'ABZ333', 'NoABZ557', 'ABZ332', 'ABZ346', 'ABZ321', 'ABZ17', 'NoABZ1491', 'ABZ229', 'ABZ550']
    cluster_value = []
    for k, v in data.items():
        if k in Cluster:
            cluster_value.extend(v)
    """
    for elem in NOT_TO_INCLUDE:
        data.pop(elem, None)
        data_test.pop(elem, None)



    print("Signs: ", len(data.keys()))
    print("Total Data:", len_values(data))
    MINIMUM_SAMPLE_SIZE = 75
    data = {k: v for k, v in data.items() if len(v) >= MINIMUM_SAMPLE_SIZE}
    # sort by length of list which is value in dict
    data = {k: v for k, v in sorted(data.items(), key=lambda item: len(item[1]), reverse=True)}

    classes = [f"{k} {len(v)}" for k, v in data.items()]
    print([f"{k} {len(v)}" for k, v in data.items()])
    # write classes as list to txt file


    class_to_int = {k: i for i, k in enumerate(data.keys())}
    print("ABZ Signs: ", data.keys())
    print("Number of imgs: ", len_values(data))
    print("Number of signs: ", len(data))

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


    if SPLIT != 0.0 and data_test is None:
        test_data = {}
        train_data = {}
        for k, v in data.items():
            if len(v) >= MINIMUM_SAMPLE_SIZE:
                split = int(SPLIT * len(v))
                test_data[k] = v[:split]
                train_data[k] = v[split:]
    else:
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
        for k,v in train_data.items():
            if k not in test_data.keys():
                test_data[k] = [] # need empty directory even if train data is not present in test set
                print(f"Train data contains sign {k} which is not in test data")
                train_category_not_in_test[k] = train_data[k]
        print("Test instances not in train: ", len_values(test_category_not_in_train))
        print("Train instances not in test: ", len_values(train_category_not_in_test))
        print()
    print("Test Category not in train: ", list(set(list(test_category_not_in_train.keys()))))
    train_data.pop("NoABZ", None)
    test_data.pop("NoABZ", None)
    print("Number of train signs:", len(train_data.keys()))
    print("Number of train imgs: ", len_values(train_data))
    print("Number of test signs:", len(test_data.keys()))
    print("Number of test imgs: ", len_values(test_data))






    # copy each file of value of train_data dict to directory
    create_directory(
        "data/ebl/test_set/test_set",
        overwrite=True,
    )
    create_directory(
        "data/ebl/train_set/train_set",
        overwrite=True,
    )
    _prep_data(
        test_data,
        Path(
            "data/ebl/test_set/test_set"
        ),
        class_to_int,
        "test.txt",
    )

    _prep_data(
        train_data,
        Path(
            "data/ebl/train_set/train_set"
        ),
        class_to_int,
        "train.txt",
    )

    with open("data/ebl/classes.txt", "w") as f:
        f.write(str(data.keys()))


