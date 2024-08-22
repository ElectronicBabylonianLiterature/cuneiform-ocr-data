# Cuneiform OCR Data Preprocessing for Ebl Project (https://www.ebl.lmu.de/, https://github.com/ElectronicBabylonianLiterature
Data+Code is part of Paper [Sign Detection for Cuneiform Tablets from Yunus Cobanoglu, Luis Sáenz, Ilya Khait, Enrique Jiménez](https://www.degruyter.com/document/doi/10.1515/itit-2024-0028/html). <br/>
Data on Zenodoo [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10693601.svg)](https://doi.org/10.5281/zenodo.10693601).

See [https://github.com/ElectronicBabylonianLiterature/cuneiform-ocr/blob/main/README.md](https://github.com/ElectronicBabylonianLiterature/cuneiform-ocr/blob/main/README.md) for overview and general information of all repositories associated with the paper from above.


## Installation
* requirements.txt (optionally: includes opencv-python)
* `pip3 install torch=="2.0.1" torchvision  --index-url https://download.pytorch.org/whl/cpu`
* `pip install -U openmim`
* `mim install "mmocr==1.0.0rc5"`  it is important to use this exact version because prepare_data.py won't work in newer versions (DATA_PARSERS are not backward compatible)
* `mim install "mmcv==2.0.0"`

Make sure PYTHONPATH is root of repository

See the explanatory video [here](https://syncandshare.lrz.de/getlink/fiTPERQRzdTAxNKPLSRNYb/CuneiformOCR_part1_data.mp4).

## Data
The data was fetched from our api `https://github.com/ElectronicBabylonianLiterature/ebl-api/blob/master/ebl/fragmentarium/retrieve_annotations.py`. 

To update the dataset use previous function to get new fragments, after that run [filter](https://github.com/ElectronicBabylonianLiterature/cuneiform-ocr-data/blob/601b7125d43318a019f45412f8604bbdbac09b7c/cuneiform_ocr_data/filter_annotations.py) to get fragments appliable for the training.

download [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10693601.svg)](https://doi.org/10.5281/zenodo.10693601)  raw-data and processed-data according to instructions below. This code will use raw-data and processed-data and output the data as in ready-for-training (i.e. icdar2015 and coco2017 format) (see in zenodoo ready-for-training.tar.gz). 
Directory Structure
```
data
  processed-data
    data-coco
    data-icdar2015
    detection
    ...
    classification
      data (after gather_all.py
      ...
  raw-data
    ebl
    heidelberg
    jooch
    urschrei-CDP
```
 		

## Data Preprocessing for Text Detection (Predict only Bounding Boxes)
1. Preprocessing Heidelberg Data, all Details in `cuneiform_ocr_data/heidelberg/README.md`

2. Ebl (our) data in `data/raw-data/ebl` (generally better to create test set from ebl data because quality is better) 

    2.1. Run `extract_contours.py` with `EXTRACT_AUTMOATICALLY=False` on `data/raw-data/ebl/detection`

    2.2. Run `display_bboxes.py` and use keys to delete all which are not good quality 

3. Run `select_test_set.py` which will select 50 randomly images from `data/processed-data/ebl/ebl-detection-extracted-deleted` (currently no option to create val set because of small size of dataset) 

4. `data/processed-data/ebl/ebl-detection-extracted-test` has .txt file will names of all images in test set (this will be necessary to create train,test for classification later)  

5. Now merge `data/processed-data/heidelberg/heidelberg-extracted-deleted` and `ebl-detection-extracted-train` which will be your train set (see `data/processed-data/detection`, around 295 train and 50 test instances). 

6. Optionally. Create Icdar2015 Style dataset using `convert_to_icdar2015.py` 

7. Optionally: Create Coco Style Dataset  `convert_to_coco.py` will create only a test set coco style


### Dataformat
image: P3310-0.jp, with gt_P3310-0.txt.

Ground truth contains top left x, top left y, width, height and sign.

Sign followed by ? means it is partially broken. Unclear signs have value 'UnclearSign'.

Example: 0,0,10,10,KUR


## Data Preprocessing for Image Classification

1. Fetch Sign Images from https://labasi.acdh.oeaw.ac.at/ using their api in `cuneiform_ocr_data/labasi`
2. Run `classification/cdp/main.py` will map data using our ABZ Sign Mapping some signs can't be mapped (should be checked by an assyiriologist for correctness)
3. Run `classification/jooch/main.py` will map data using our ABZ Sign Mapping some signs can't be mapped (should be checked by an assyiriologist for correctness)
4. Merge `data/processed-data/heidelberg/heidelberg` and `data/raw-data/ebl/ebl-classification` to `data/processed-data/ebl+heidelberg-classification`
5. Split `data/processed-data/ebl+heidelberg-classification` to `data/processed-data/ebl+heidelberg-classification-train` and `data/processed-data/ebl+heidelberg-classification-test` by copying all files which are part of the detection test set using the script `move_test_set_for_classification.py`
6. Run `crop_sign.py` on `data/processed-data/ebl+heidelberg-classification-train` and `data/processed-data/ebl+heidelberg-classification-test` you can modify `crop_signs.py` to include/exclude partially broken or UnclearSigns.
7. `data/processed-data/classification` should contain Cuneiform Dataset JOOCH, ebl+heidelberg/ebl+heidelberg-train, ebl+heidelberg/ebl+heidelberg-test, labasi and urschrei-CDP-processed
8. `gather_all.py` will gather and finalize the format for training/testing of all the folders from 7. (gather_all.py will create "cuneiform_ocr_data/classification/data" directory with classes.txt which has all classes used for training/testing)


## Data Preprocessing for Image (Sign) Classification (Details)
0. Use `move_test_set_for_classification.py` to extract all images belonging to detection test set for classification
1. Images are cropped from LMU and Heidelberg using `crop_signs.py` and converted to ABZ Sign List via ebl.txt mapping from OraccGlobalSignList/ MZL to ABZ Number
   - Partially Broken and Unclear Signs can be dealt included/excluded on parameter in script
2. Images from CDP (urschrei-cdp) are renamed using the mapping from the urschrei-repo https://github.com/urschrei/CDP/csvs (look at cuneiform_ocr/preprocessing_cdp)
   - Images are renamed `rename_to_mzl.py`
   - Images are mapped via urschrei-cdp corrected_instances_forimport.xlsx and custom mapping via `convert_cdp_and_jooch.py`
3. Cuneiform JOOCH images are not used due to bad quality currently
4. Labasi Project is scraped with `labasi/crawl_labasi_page.py` (can take very long multiple hours with interruptions) and renamed manually to fit ebl.txt mapping


## Acknowledgements/ Citation
- Deep learning of cuneiform sign detection with weak supervision using transliteration alignment [https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243039](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243039)
  - Annotated Tablets (75 Tablets) [https://compvis.github.io/cuneiform-sign-detection-dataset/](https://compvis.github.io/cuneiform-sign-detection-dataset/)
  - -> Heidelberg Data
- Towards Query-by-eXpression Retrieval of Cuneiform Signs [https://patrec.cs.tu-dortmund.de/pubs/papers/Rusakov2020-TQX]
  - -> JOOCH Dataset https://graphics-data.cs.tu-dortmund.de/docs/publications/cuneiform/
- Labasi Project https://labasi.acdh.oeaw.ac.at/
- CDP Project https://github.com/urschrei/CDP
- LMU https://www.ebl.lmu.de/

## Cite this paper
```
@article{CobanogluSáenzKhaitJiménez+2024,
url = {https://doi.org/10.1515/itit-2024-0028},
title = {Sign detection for cuneiform tablets},
title = {},
author = {Yunus Cobanoglu and Luis Sáenz and Ilya Khait and Enrique Jiménez},
journal = {it - Information Technology},
doi = {doi:10.1515/itit-2024-0028},
year = {2024},
lastchecked = {2024-06-01}
}
```

