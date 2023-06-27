# Copyright (c) OpenMMLab. All rights reserved.
import os.path as osp
import warnings
from pathlib import Path
from typing import Optional, List, Tuple

from mmocr.datasets.preparers import DatasetPreparer
from mmocr.datasets.preparers.data_preparer import DATA_PARSERS
from mmocr.datasets.preparers.parsers.base import BaseParser
from mmocr.utils import register_all_modules, bbox2poly

from cuneiform_ocr_data.prepare_and_split_data import prepare_data

dataset = "ebl"
nproc = 4
task = "textdet"
dataset_zoo_path = "dataset_zoo"


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
            text = anno[4:5][0]
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


HEIDELBERG_VAL_SET = [
    "P336128",
    "P336003",
    "P336637",
    "P335959",
    "P336188",
    "P335940",
    "P335960",
    "P335646",
    "P335652",
    "P335958",
    "P335980",
    "P335575",
    "P335976",
    "BM099070",
    "P335650",
    "P335957",
    "P335949",
    "P335593",
    "ND02486",
    "P334926",
    "P336158",
    "P335653",
    "P335651",
    "P335561",
    "K08396",
    "P335937",
    "K09237Vs",
    "P336150",
    "P336009",
    "P334932",
    "P335597",
    "P336198",
    "P335946",
    "P335941",
]


HEIDELBERG_VAL_SET = [
    "P336150",
    "P336009",
    "P334932",
    "P335597",
    "P336198",
    "P335946",
    "P335941"
]
#HEIDELBERG_VAL_SET_1 = HEIDELBERG_VAL_SET[: len(HEIDELBERG_VAL_SET) // 5]
#HEIDELBERG_VAL_SET_2 = HEIDELBERG_VAL_SET[len(HEIDELBERG_VAL_SET) // 5 : 2 * len(HEIDELBERG_VAL_SET) // 3]
#HEIDELBERG_VAL_SET_3 = HEIDELBERG_VAL_SET[2 * len(HEIDELBERG_VAL_SET) // 3 :]


if __name__ == "__main__":
    data_path = Path(
        "/home/yunus/PycharmProjects/cuneiform-ocr-data/data/processed-data/total-backup"
    )
    path = Path("data")
    output_path = path
    prepare_data(data_path, output_path, HEIDELBERG_VAL_SET, 1)
    output_path = path / "icdar2015"
    prepare_data(data_path, output_path, HEIDELBERG_VAL_SET, 1)

    main()
