data_root = "cuneiform_ocr_data/data/icdar2015"

data_converter = dict(
    type="TextSpottingDataConverter",
    splits=["train", "test"],
    data_root=data_root,
    gatherer=dict(
        type="pair_gather",
        suffixes=[".jpg", ".JPG"],
        rule=[r"([\a-zA-Z\,\.\d]+)\.([jJ][pP][gG])", r"gt_\1.txt"],
    ),
    parser=dict(type="EblTxtTextDetAnnParser", encoding="utf-8-sig"),
    dumper=dict(type="JsonDumper"),
)
