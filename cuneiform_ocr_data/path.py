import os
import shutil
from pathlib import Path
from typing import Union


def create_directory(path: Union[str, Path], overwrite: bool = False) -> None:
    if overwrite:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
    else:
        if os.path.exists(path):
            raise FileExistsError(f"Directory {path} already exists")
        else:
            os.makedirs(path)
