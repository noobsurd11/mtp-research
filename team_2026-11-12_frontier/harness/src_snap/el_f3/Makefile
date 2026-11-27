.PHONY: help data splits stats train-sup train-ssl eval test

PYTHON      := .venv/bin/python
DATASET_DIR ?= ../datasets/BenchmarkELimages/dataset_20211104
FRAC        ?= 0.2
SEED        ?= 0
RUN         ?=

help:
	@echo "  make data        Symlink dataset_20211104 into data/labeled/"
	@echo "  make splits      Regenerate committed split files + split stats"
	@echo "  make stats       Per-split class pixel counts -> reports/"
	@echo "  make train-sup   Supervised run   (FRAC=$(FRAC) SEED=$(SEED))"
	@echo "  make train-ssl   Mean Teacher run (FRAC=$(FRAC) SEED=$(SEED))"
	@echo "  make eval RUN=<run_name>   Evaluate experiments/<run>/checkpoints/best.pth on test"
	@echo "  make test        Run unit tests"

data:
	$(PYTHON) scripts/link_data.py --dataset_dir $(DATASET_DIR)

splits:
	$(PYTHON) scripts/make_splits.py --dataset_dir $(DATASET_DIR)
	$(PYTHON) scripts/split_class_stats.py

stats:
	$(PYTHON) scripts/split_class_stats.py

train-sup:
	$(PYTHON) scripts/train.py --config configs/supervised.yaml --opts data.labeled_fraction=$(FRAC) seed=$(SEED)

train-ssl:
	$(PYTHON) scripts/train.py --config configs/ssl_mean_teacher.yaml --opts data.labeled_fraction=$(FRAC) seed=$(SEED)

eval:
	$(PYTHON) scripts/evaluate.py --run experiments/$(RUN) --weights best --split test

test:
	$(PYTHON) -m pytest tests -v
