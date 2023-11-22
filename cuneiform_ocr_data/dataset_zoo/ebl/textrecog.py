data_root = "cuneiform_ocr_data/data/icdar2015"
cache_path = "data/cache"



data_converter = dict(
    type="TextRecogDataConverter",
    splits=["train", "test"],
    data_root=data_root,
    gatherer=dict(
        type="pair_gather",
        suffixes=[".jpg", ".JPG"],
        rule=[r"(.*)\.([jJ][pP][gG])", r"gt_\1.txt"],
    ),
    parser=dict(type="EblTxtTextRecogAnnParser"),
    dumper=dict(type="JsonDumper"),
)