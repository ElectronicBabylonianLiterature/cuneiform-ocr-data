
<p>**heidelberg** Python Package</p>
Dataset from the paper: <br/>
Dencker, T., Klinkisch, P., Maul, S. M., and Ommer, B. (2020): Deep Learning of Cuneiform Sign Detection with Weak Supervision using Transliteration Alignment, PLOS ONE, 15:12, pp. 1–21 <a href="https://doi.org/10.1371/journal.pone.0243039">https://doi.org/10.1371/journal.pone.0243039</a>

Dataset Link <a href="https://github.com/CompVis/cuneiform-sign-detection-dataset">https://github.com/CompVis/cuneiform-sign-detection-dataset</a>  

Dataset was collected using the following annotation tool: <a href="https://github.com/CompVis/cuneiform-sign-detection-webapp">https://github.com/CompVis/cuneiform-sign-detection-webapp</a> 

We have also added some annotations around 1000 using the tool from above these are in `data/raw-data/heidelberg/heidelberg-xml` 
There are multiple versions for some annotations like <code>gt_P3143346.txt</code> and <code>gt_P3143346-v3.txt</code>. These have to merged manually.</p>

<code>gt_P314346.txt</code> is broken <code>gt_P314346-v3.txt</code> is fine. 
<code>gt_P335575-v3.txt</code> is a subset of  <code>gt_P335575.txt</code>. 
<code>gt_P336158.txt</code> is a superset of <code>gt_P336158-v3.txt</code> and <code>gt_P336158-v4.txt</code>
All duplicates are fixed in `data/raw-data/heidelberg/heidelberg-xml-manuel-fixed/heidelberg-xml` 


Pipeline
<ol>  
<li>Download `data/raw-data/heidelberg` </li>  
<li>Run <code>create_annotations_txts.py</code></li>  
<li>Run <code>parse_corrected_heidelberg_xml.py</code></li>  
<li>Run <code>merge_corrected_xml.py</code></li>  
<li>Run   <code>manuel_fixing/shift_bboxes.py</code></li>
<li>Run <code>manuel_fixing/delete_bbox_within_rectangle.py</code>
<li>Run <code> extract_contours.py </code> with `EXTRACT_AUTOMATICALLY=True` </li>
<li> Following Images have to be deleted ['P334357-2', 'P335976-2', 'P335980-3', 'P334042-3', 'P334828-0', 'P337153-2', 'P334828-2', 'P337163-1', 'P334932-2', 'P336663-0', 'P335561-2', 'P334311-2', 'P335946-2', 'P336643-2', 'P334311-3', 'P336663-1', 'P334357-4', 'P334042-2', 'P336614-2', 'P393668-2', 'P334357-3']
<li> P336009.jpg has to replaced with P336009_fixed.jpg
<li>Run `display_bboxes.py` to verify Images
</ol>
<code>create_annotations_txts.py</code> will convert to .csv format to txts and download missing images from CDLI.
Some images are downloaded from CDLI website (<a href="https://cdli.ucla.edu/">https://cdli.ucla.edu/</a>) and for some image ids the download fails. We have added those images manually so instead of downloading the images one can download our dataset (`data/raw-data/heidelberg`). We have fixed the missing ids and downloaded manually. Passing <code>download=False</code> will only convert the ground truth to txt format and using the correct sign classes.
The Annotations have line segmentation and structural information like obverse, reverse but these annotations are not used.

<code>parse_corrected_heidelberg_xml.py</code> convert data from heidelberg-xml to txt annotations.

<code>merge_corrected_xml.py</code> will merge the corrections with the existing annotations.

<code>prepare_images_for_php_annotation_tool.py</code> is a legacy script which was used once for porting the data to add unfinished annotations to it using the <a href="https://github.com/CompVis/cuneiform-sign-detection-webapp">https://github.com/CompVis/cuneiform-sign-detection-webapp</a> tool.

