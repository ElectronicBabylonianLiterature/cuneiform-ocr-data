import random
import shutil
from pathlib import Path

from cuneiform_ocr_data.path import create_directory

random.seed(0)

lmu_extracted = ['1879,0708.86-0.jpg', 'BM.33337-0.jpg', 'BM.38076-0.jpg', 'BM.39030-1.jpg', 'BM.40403-0.jpg', 'BM.41747-1.jpg', 'K.10211-0.jpg', 'K.1283-0.jpg', 'K.18767.jpg', 'K.20256.jpg', 'K.3810-1.jpg', 'K.6400-0.jpg', 'K.9905-1.jpg', 'Rm-II.229-0.jpg', '1879,0708.86-1.jpg', 'BM.33337-1.jpg', 'BM.38272-0.jpg', 'BM.39119-0.jpg', 'BM.40406.jpg', 'BM.42273-0.jpg', 'K.10545-0.jpg', 'K.12984.jpg', 'K.18874-0.jpg', 'K.2025.jpg', 'K.4003-0.jpg', 'K.6400-1.jpg', 'MGT.3-0.jpg', 'Sm.986-0.jpg', '1880,0719.100-0.jpg', 'BM.33491-0.jpg', 'BM.38272-1.jpg', 'BM.39319-0.jpg', 'BM.40416-0.jpg', 'BM.42273-1.jpg', 'K.10545-1.jpg', 'K.12999.jpg', 'K.18875.jpg', 'K.20493.jpg', 'K.4003-1.jpg', 'K.7114-0.jpg', 'MLC.1874-0.jpg', 'Sm.986-1.jpg', '1880,0719.100-1.jpg', 'BM.33491-1.jpg', 'BM.38422-0.jpg', 'BM.39319-1.jpg', 'BM.40416-1.jpg', 'BM.42276-0.jpg', 'K.11309-0.jpg', 'K.13355.jpg', 'K.19000.jpg', 'K.2-0.jpg', 'K.4030-0.jpg', 'K.7114-1.jpg', 'MLC.1874-1.jpg', 'YBC.1317-0.jpg', '1882,0323.102-0.jpg', 'BM.33541-0.jpg', 'BM.38422-1.jpg', 'BM.39562-0.jpg', 'BM.40416-2.jpg', 'BM.42283-0.jpg', 'K.11373-0.jpg', 'K.13731.jpg', 'K.19001.jpg', 'K.21803.jpg', 'K.4063-0.jpg', 'K.7853-0.jpg', 'MLC.1874-2.jpg', 'YBC.1317-1.jpg', '1882,0323.17-0.jpg', 'BM.33541-1.jpg', 'BM.38432-0.jpg', 'BM.39788.jpg', 'BM.40431.jpg', 'BM.42283-1.jpg', 'K.11403-0.jpg', 'K.13887.jpg', 'K.19006.jpg', 'K.2189-0.jpg', 'K.4063-1.jpg', 'K.7853-1.jpg', 'MLC.1879-0.jpg', 'YBC.4046-0.jpg', '1882,0323.17-1.jpg', 'BM.33558-0.jpg', 'BM.38432-1.jpg', 'BM.40012-0.jpg', 'BM.40518-0.jpg', 'BM.42325-0.jpg', 'K.11700-0.jpg', 'K.14481.jpg', 'K.19010.jpg', 'K.2-1.jpg', 'K.4426-0.jpg', 'K.7917-0.jpg', 'MLC.1881-0.jpg', 'YBC.4046-1.jpg', '1882,0522.552-0.jpg', 'BM.33558-1.jpg', 'BM.38537-0.jpg', 'BM.40193-0.jpg', 'BM.40696-0.jpg', 'BM.42333-0.jpg', 'K.11947-0.jpg', 'K.14854.jpg', 'K.19105.jpg', 'K.2210-0.jpg', 'K.4426-1.jpg', 'K.8678-0.jpg', 'NBC.1120-0.jpg', 'YBC.4046-2.jpg', '1891,0509.236.jpg', 'BM.33983-0.jpg', 'BM.38537-1.jpg', 'BM.40196-0.jpg', 'BM.40696-1.jpg', 'DT.42-0.jpg', 'K.11947-1.jpg', 'K.15827.jpg', 'K.19118.jpg', 'K.2712-0.jpg', 'K.4782.jpg', 'K.8678-1.jpg', 'NBC.1120-1.jpg', 'BM.114741.jpg', 'BM.34218-0.jpg', 'BM.38544-0.jpg', 'BM.40196-1.jpg', 'BM.40818-0.jpg', 'GCBC.284-0.jpg', 'K.12000-0.jpg', 'K.16002-0.jpg', 'K.19210-0.jpg', 'K.2826-0.jpg', 'K.5807-0.jpg', 'K.9048-0.jpg', 'NBC.1120-2.jpg', 'BM.121131.A-0.jpg', 'BM.34314-0.jpg', 'BM.38544-1.jpg', 'BM.40216-0.jpg', 'BM.41000-0.jpg', 'GCBC.284-1.jpg', 'K.12000-1.jpg', 'K.16446.jpg', 'K.19403.jpg', 'K.3118-0.jpg', 'K.5807-1.jpg', 'K.9048-1.jpg', 'ND.5437-0.jpg', 'BM.32254-0.jpg', 'BM.35293-0.jpg', 'BM.38770-0.jpg', 'BM.40216-1.jpg', 'BM.41000-1.jpg', 'IM.67559-0.jpg', 'K.12000.Q-0.jpg', 'K.17666.jpg', 'K.19604-0.jpg', 'K.3118-1.jpg', 'K.6201-0.jpg', 'K.9499.jpg', 'ND.6200-0.jpg', 'BM.32254-1.jpg', 'BM.36041-0.jpg', 'BM.38770-1.jpg', 'BM.40295-0.jpg', 'BM.41291-0.jpg', 'IM.67571-0.jpg', 'K.12687.jpg', 'K.17674-0.jpg', 'K.19888.jpg', 'K.3285-0.jpg', 'K.6201-1.jpg', 'K.9654-0.jpg', 'ND.6201.jpg', 'BM.33014-0.jpg', 'BM.36041-1.jpg', 'BM.38770-2.jpg', 'BM.40295-1.jpg', 'BM.41291-1.jpg', 'K.10084.jpg', 'K.128-0.jpg', 'K.17677.jpg', 'K.20-0.jpg', 'K.3499-0.jpg', 'K.6393-0.jpg', 'K.9654-1.jpg', 'Rm.618-0.jpg', 'BM.33014-1.jpg', 'BM.36456-0.jpg', 'BM.39030-0.jpg', 'BM.40357-0.jpg', 'BM.41747-0.jpg', 'K.10208.jpg', 'K.128-1.jpg', 'K.1808-0.jpg', 'K.20-1.jpg', 'K.3810-0.jpg', 'K.6393-1.jpg', 'K.9905-0.jpg', 'Rm.618-1.jpg']
path = Path("../data/processed-data/all_lmu+heidel/all_lmu_extracted_train")
test_path = Path("../data/processed-data/all_lmu+heidel/all_lmu_extracted_test")
create_directory(test_path / "imgs", overwrite=True)
create_directory(test_path / "annotations", overwrite=True)
# select 50 elements without replacement at random from lmu_extracted list

test_set = random.sample(lmu_extracted, 50)
#print(test_set)
extracted = []
# iter through path and move all files from test_set to test folder
if __name__ == "__main__":
    for file in (path / "imgs").iterdir():
        if file.name in test_set:
            extracted.append(file.name)
            shutil.move(file, test_path / "imgs")

    for file in (path / "annotations").iterdir():
        if file.stem.split("gt_")[1] in list(map(lambda x: x.split(".jpg")[0],test_set)):
            shutil.move(file, test_path / "annotations")

    print(len(extracted))