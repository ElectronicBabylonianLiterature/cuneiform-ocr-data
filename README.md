# Cuneiform OCR Data Preprocessing


## Installation

* requirements.txt
* pip install -U openmim
* mim install "mmocr==1.0.0rc5"  it is important to be this exact version because prepare_data.py won't work in newer versions (DATA_PARSERS are not backward compatible)



## Data Preprocessing for Text Detection (Predict only Bounding Boxes)

1. Heidelberg Images (VAT Images from https://github.com/CompVis/cuneiform-sign-detection-dataset and the rest from CDLI (some ids needed manuell fixing)
   - all Heidelberg imgs at `data/raw-data/heidelberg/heidelberg-imgs`
2. The csv files from https://github.com/CompVis/cuneiform-sign-detection-dataset have to be converted to correct format with `create_annotations_txts.py`
   -  csv files at `data/raw-data/heidelberg/annotations_csv`
   - Converted Heidelberg annotations  `data/processed-data/heidelberg/annotations`
   - Heidelberg MZL is converted to Oracc Global Sign List via `mzl.txt`
   - P336663 and P397986 annotations are shifted (P336663 is shifted by 340, 1790 and P397986 is shifted by 370 and 60)
3. Heidelberg-xml is some more annotations added to original Heidelberg Annotations. They need to be converted to correct format and merged with Heidelberg annotations `parse_corrected_xml.py` and merged with `merge_corrected_xml.py`
   - gt_P314346-v3.txt replaced gt_P314346.txt and all others have to use the highest version so v3 for example if present `data/processed-data/heideberg-merged-2`
   - Once merged remove duplicate lines in ground_truth `remove_duplicates.py`
   - Files at `data/processed-data/heideberg-merged`
4. Extract Contours (Obverse, Reverse, ...)
   - Extract contours from Heidelberg Data (`data/processed-data/heideberg-merged-extracted`)
   - Extract contours using Struct/Obverse and Reverse BoundingBoxes from LMU Data (`data/processed-data/lmu-detection-extracted`)
5. Manuelly scroll through Heidelberg Data delete invalid imgs and fix the one which need manuell fixing
   - Use `display_bboxes.py` to manually display imgs + ground_truth
   - Delete all invalid imgs `data/processed-data/heideberg-merged-extracted-cleaned`
   - Some random wrong bounding boxes are deleted with `delete_bbox_within_rectangle.py` and P336009.jpg contours were extracted manually (`data/processed-data/heideberg-merged-extracted-cleaned-2`)
6. Merge LMU + Heidelberg data -> `data/processed-data/total`
   - This Dataset can be used for training only the Oracc Global Sign List has to be converted to ABZ Sign List with ebl.txt
   - The last step is optional Oracc Global Sign List is more fine grained than ABZ Sign List

  
### Dataformat
image: P3310-0.jp, with gt_P3310-0.txt.

Ground truth contains top left x, top left y, width, height and sign.

Sign followed by ? means it is partially broken. Unclear signs have value 'UnclearSign'.

Example: 0,0,10,10,KUR

## Data Preprocessing for Image (Sign) Classification
1. Images are cropped from LMU and Heidelberg using `crop_signs.py` and converted to ABZ Sign List via ebl.txt mapping from OraccGlobalSignList/ MZL to ABZ Number
   - Partially are broken are treated as "unbroken"
   - Unclear Sign is included to added ABZ Number
2. Images from CDP (urschrei-cdp) are renamed using the mapping from the urschrei-repo https://github.com/urschrei/CDP/csvs (look at cuneiform_ocr/preprocessing_cdp)
   - Images are renamed `rename_to_mzl.py`
   - Images are mapped via urschrei-cdp cirrected_instances_forimport.xlsx and custom mapping via `convert_cdp_and_jooch.py`
3. Cuneiform JOOCH images are not used due to bad quality currently
4. Labasi Project is scraped with `labasi/crawl_labasi_page.py` (can take very long multiple hours with interruptions) and renamed manually to fit ebl.txt mapping

## Preparing Classification Data
`classification/gather_all.py` will gather all data from the different directories and merge them. In case of using a specific directory as test set one can specify that as data_set in code
or make it `None` and specify the split variable so there will be a random split created. Categories "NoABZ" (just in labasi) and "NoABZ0" (= UnclearSign in ebl.txt) are not included.
You have to set a MINIMUM_SAMPLE_SIZE which determines how many instances of a category have to be present to be included in train/testing. 
The data will be in ./data folder ready for training in cuneiform_ocr repo. 
**Important** the classes will be printed as a list in the screen. This list has to be copied to the config files for classification. Their index will associate the output of the Classification which is a Number with the corresponding ABZ Number.
Finally run 'validate_imgs.py` to make sure there are no damaged images.

## Preparing Detection Data
`prepare_data.py` either pass a list of image names which are going to be the test set or a number which will be the percentage of the test set. The rest will be the training set.
The data will be in ./data/icdar2015 folder ready for training in cuneiform_ocr repo. **Important** the path has to be ./data/icdar2015 otherwise the json will be empty check the json file !.
Line 139-142 is run twice because we need the annotations & imgs twice if you later want to convert them using `convert_to_coco.py`. For training the detector only `data/icdar2015` is needed.

## Preparing Recognition Coco Dataset
Once you have run `prepare_data.py` you can run `convert_to_coco.py`. You have to give the list `classes` which has the mapping index to ABZ Number. Which was mentioned above.


## Acknowledgements/ Citation
- Deep learning of cuneiform sign detection with weak supervision using transliteration alignment [https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243039](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243039)
  - Annotated Tablets (75 Tablets) [https://compvis.github.io/cuneiform-sign-detection-dataset/](https://compvis.github.io/cuneiform-sign-detection-dataset/)
  - -> Heidelberg Data
- Synthetic Cuneiform Dataset (2000 Tablets) from [https://github.com/cdli-gh/Cuneiform-OCR](https://github.com/cdli-gh/Cuneiform-OCR) (not currently used for training)
- Towards Query-by-eXpression Retrieval of Cuneiform Signs [https://patrec.cs.tu-dortmund.de/pubs/papers/Rusakov2020-TQX]
  - -> JOOCH Dataset https://graphics-data.cs.tu-dortmund.de/docs/publications/cuneiform/
- Labasi Project https://labasi.acdh.oeaw.ac.at/
- CDP Project https://github.com/urschrei/CDP
- LMU https://www.ebl.lmu.de/

