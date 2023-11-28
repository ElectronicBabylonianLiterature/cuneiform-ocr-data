icdar2015_textspotting_data_root = 'data/icdar2015'

icdar2015_textspotting_train = dict(
    type='OCRDataset',
    data_root=icdar2015_textspotting_data_root,
    ann_file='textspotting_train.json',
    filter_cfg=dict(filter_empty_gt=True, min_size=32),
    pipeline=None)

icdar2015_textspotting_test = dict(
    type='OCRDataset',
    data_root=icdar2015_textspotting_data_root,
    ann_file='textspotting_test.json',
    test_mode=True,
    pipeline=None)
