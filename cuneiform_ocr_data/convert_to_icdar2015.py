# Copyright (c) OpenMMLab. All rights reserved.
import os
import os.path as osp
import shutil
import warnings
from pathlib import Path
from typing import Optional, List, Tuple, Sequence

from mmocr.datasets.preparers import DatasetPreparer
from mmocr.datasets.preparers.data_preparer import DATA_PARSERS
from mmocr.datasets.preparers.parsers.base import BaseParser
from mmocr.utils import register_all_modules, bbox2poly

from cuneiform_ocr_data.utils import is_valid_data

dataset = "ebl"
nproc = 4
task = "textdet"
dataset_zoo_path = "cuneiform_ocr_data/dataset_zoo"


@DATA_PARSERS.register_module()
class EblTxtTextDetAnnParser(BaseParser):
    """ICDAR Txt Format Text Detection Annotation Parser.
    The original annotation format of this dataset is stored in txt files,
    which is formed as the following format:
        x1, y1, x2, y2, x3, y3, x4, y4, transcription
    Args:
        separator (str): The separator between each element in a line. Defaults
            to ','.
        ignore (str): The text to be ignored. Defaults to '###'.
        format (str): The format of the annotation. Defaults to
            'x1,y1,x2,y2,x3,y3,x4,trans'.
        encoding (str): The encoding of the annotation file. Defaults to
            'utf-8-sig'.
        nproc (int): The number of processes to parse the annotation. Defaults
            to 1.
        remove_strs (List[str], Optional): Used to remove redundant strings in
            the transcription. Defaults to None.
        mode (str, optional): The mode of the box converter. Supported modes
            are 'xywh' and 'xyxy'. Defaults to None.
    """

    def __init__(
        self,
        separator: str = ",",
        ignore: str = "###",
        format: str = "x1,y1,x2,y2,x3,y3,x4,y4,trans",
        encoding: str = "utf-8",
        nproc: int = 1,
        remove_strs: Optional[List[str]] = None,
        mode: str = None,
    ) -> None:
        self.sep = separator
        self.format = format
        self.encoding = encoding
        self.ignore = ignore
        self.mode = mode
        self.remove_strs = remove_strs
        super().__init__(nproc=nproc)

    def parse_file(self, file: Tuple, split: str) -> Tuple:
        """Parse single annotation."""
        img_file, txt_file = file
        instances = list()
        for anno in self.loader(txt_file, self.sep, self.format, self.encoding):
            anno = list(anno.values())
            if self.remove_strs is not None:
                for strs in self.remove_strs:
                    for i in range(len(anno)):
                        if strs in anno[i]:
                            anno[i] = anno[i].replace(strs, "")
            poly = list(map(float, anno[0:4]))
            poly = bbox2poly(poly, "xywh")
            poly = poly.tolist()
            #text = anno[4:5][0] including abz sign class eventually
            instances.append(dict(poly=poly, text="Hello", ignore=False))
        return img_file, instances


def main():
    register_all_modules()
    if not osp.isdir(osp.join(dataset_zoo_path, dataset)):
        warnings.warn(
            f"{dataset} is not supported yet. Please check "
            "dataset zoo for supported datasets."
        )

    preparer = DatasetPreparer(
        cfg_path=dataset_zoo_path, dataset_name=dataset, task=task, nproc=nproc
    )
    preparer()


def copy_image_and_corresponding_annotation(
    images_path: Sequence[Path],
    output_folder_annotations: Path,
    output_folder_imgs: Path,
    annotations_path_copy_from: Path,
):
    for file in images_path:
        shutil.copyfile(file, output_folder_imgs / file.name)
        annotation_path = next(annotations_path_copy_from.glob(f"gt_{file.stem}.txt"))
        shutil.copyfile(
            annotation_path, output_folder_annotations / annotation_path.name
        )


def prepare_data(data_path, output_path, test_set):
    images_path = data_path / "imgs"
    annotations_path = data_path / "annotations"

    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    def create_folders(anno, imgs, data):
        anns = output_path / anno
        imgs = output_path / imgs
        anns.mkdir(parents=True)
        imgs.mkdir(parents=True)
        copy_image_and_corresponding_annotation(data, anns, imgs, annotations_path)

    annotations = Path("annotations")
    imgs = Path("textdet_imgs")

    val_imgs = []

    for elem in test_set:
        # find all images in images_path where elem is in name
        val_imgs.extend(list(images_path.glob(f"*{elem}*")))

    train_imgs = list(set(list(images_path.iterdir())) - set(val_imgs))

    create_folders(annotations / "train", imgs / "train", train_imgs)

    create_folders(annotations / "test", imgs / "test", val_imgs)


if __name__ == "__main__":
    data_path = Path("../data/processed-data/data/processed-data/detection/total+deebscribe")
    test_set_path = Path("../data/processed-data/data/processed-data/detection/test/test_imgs.txt")
    # read newline seperated txt file and save to list
    with open(test_set_path, "r") as f:
        test_set = f.read().splitlines()
    is_valid_data(data_path)

    output_path = Path("cuneiform_ocr_data/data") / "icdar2015"
    prepare_data(data_path, output_path, test_set)
    main()
