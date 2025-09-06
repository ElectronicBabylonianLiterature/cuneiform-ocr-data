# standard imports 
from pathlib import Path
import shutil

# package imports
from tqdm import tqdm

# local imports
#################

def move_sign_files(txt_file):
    root_name = 'data_40k_crops'
    new_root = Path(root_name)
    new_root.mkdir(parents=True, exist_ok=True) 

    with open(txt_file, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            file_path = Path(line.strip())
            abz_folder = file_path.parent.name
            abz_folder_path = Path(f"{root_name}/{abz_folder}") 
            abz_folder_path.mkdir(parents=True, exist_ok=True) 
            dest = new_root / abz_folder / file_path.name
            shutil.copy(str(file_path), str(dest))

if __name__ == '__main__':
    txt_file = "utils/images_to_delete/no_partial_order_x1.txt"
    move_sign_files(txt_file)




