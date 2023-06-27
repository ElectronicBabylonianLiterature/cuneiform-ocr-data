data_root = "data/icdar2015"
cache_path = "data/cache"


data_converter = dict(
    type="TextDetDataConverter",
    splits=["train", "test"],
    data_root=data_root,
    gatherer=dict(
        type="pair_gather",
        suffixes=[".jpg", ".JPG"],
        rule=[r"(.*)\.([jJ][pP][gG])", r"gt_\1.txt"],
    ),
    parser=dict(type="EblTxtTextDetAnnParser"),
    dumper=dict(type="JsonDumper"),
)
