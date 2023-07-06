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
from cuneiform_ocr_data.select_test_set import test_set

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



if __name__ == "__main__":
    data_path = Path(
        "/home/yunus/PycharmProjects/cuneiform-ocr-data/data/processed-data/lmu+heidel"
    )
    path = Path("data")
    output_path = path
    prepare_data(data_path, output_path, test_set, 1)
    output_path = path / "icdar2015"
    prepare_data(data_path, output_path, test_set, 1)
    main()
