# GaitSet CASIA-B Project

This repository is a cleaned training setup for gait recognition based on the GaitSet paper and codebase, adapted for local CASIA-B experiments.

It keeps the core training, testing, and pretreatment pipeline, while removing local-only checkpoints, caches, and machine-specific paths so the project is easier to understand and reuse.

## Included

- `train.py`: train the GaitSet model
- `test.py`: evaluate a saved checkpoint
- `pretreatment.py`: align and crop raw silhouette sequences into 64x64 inputs
- `batch_unzip.py`: batch archive extraction helper for dataset preparation
- `config.py`: project configuration with relative-path-friendly defaults
- `model/`: network, loss, data loading, and evaluation code
- `work/OUMVLP_network/`: alternate OUMVLP network files preserved from the original project
- `figures/`: screenshots/results from earlier runs

## Not Included

The original local project contained artifacts that are not stored in this GitHub copy:

- training checkpoints in `work/checkpoint/`
- generated partition files in `work/partition/`
- cached Python files
- local pretreatment logs
- raw or processed gait datasets

## Project Background

This project is based on GaitSet:

- Paper: [GaitSet: Cross-view Gait Recognition through Utilizing Gait as a Deep Set](https://ieeexplore.ieee.org/document/9351667)
- Original implementation concepts and directory structure are preserved where practical

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Data Preparation

Prepare the raw dataset in this structure:

```text
your_dataset_path/subject_ids/walking_conditions/views
```

Example:

```text
CASIA-B/001/nm-01/000/
```

Run pretreatment:

```bash
python pretreatment.py --input_path "path/to/raw_dataset" --output_path "path/to/output"
```

The processed silhouettes should be 64x64.

## Configuration

Default paths in `config.py` are relative to the repository:

- `WORK_PATH`: `./work`
- `dataset_path`: `./data/output`

You can also override them with environment variables:

- `GAITSET_WORK_PATH`
- `GAITSET_DATASET_PATH`
- `CUDA_VISIBLE_DEVICES`

## Train

```bash
python train.py --cache=True
```

## Test

```bash
python test.py --iter=80000 --batch_size=1 --cache=False
```

## Notes

- This repository is intended as a cleaned project snapshot rather than the full original experiment folder.
- If you want to reproduce training, you must prepare the dataset yourself and generate new checkpoints locally.
- The original upstream-style README content has been condensed here to better match this cleaned project layout.
