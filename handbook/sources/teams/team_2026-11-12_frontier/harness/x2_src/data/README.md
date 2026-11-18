# Data Directory

Populate with symlinks (nothing is copied):

```bash
python scripts/link_data.py --dataset_dir /path/to/BenchmarkELimages/dataset_20211104
```

## Layout

```
data/
├── labeled/
│   ├── images/        # symlinks -> dataset_20211104/images_{train_original,val,test}
│   └── masks_coded/   # symlinks -> dataset_20211104/masks_coded_{train_original,val,test}
└── splits/            # committed; see scripts/make_splits.py
```

## Mask encoding

Masks are the dataset's single-channel index PNGs: pixel value == class id
0–23 (`src/data/class_info.py`). They are read directly; any value outside
0–23, or a non single-channel PNG, is an error.

Split files are required. A missing or empty split file is an error; the code
never falls back to "every image in the directory".
