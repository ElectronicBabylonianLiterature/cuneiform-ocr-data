data_root = "data/icdar2015"


data_converter = dict(
    type="TextDetDataConverter",
    splits=["train", "test"],
    data_root=data_root,
    gatherer=dict(
        type="pair_gather",
        suffixes=[".jpg", ".JPG"],
        rule=[r"([\a-zA-Z\,\.\d]+)\.([jJ][pP][gG])", r"gt_\1.txt"],
    ),
    parser=dict(type="ICDARTxtTextDetAnnParser"),
    dumper=dict(type="JsonDumper"),
    test_anns=[
        dict(ann_file='textrecog_test.json')
    ]
)
