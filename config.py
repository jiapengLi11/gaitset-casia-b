import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_WORK_PATH = PROJECT_ROOT / "work"
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "output"


conf = {
    "WORK_PATH": str(Path(os.getenv("GAITSET_WORK_PATH", DEFAULT_WORK_PATH)).resolve()),
    "CUDA_VISIBLE_DEVICES": os.getenv("CUDA_VISIBLE_DEVICES", "0"),
    "data": {
        "dataset_path": str(Path(os.getenv("GAITSET_DATASET_PATH", DEFAULT_DATASET_PATH)).resolve()),
        "resolution": "64",
        "dataset": "CASIA-B",
        # In CASIA-B, subject #5 is incomplete and is ignored in training.
        "pid_num": 73,
        "pid_shuffle": False,
    },
    "model": {
        "hidden_dim": 256,
        "lr": 5e-4,
        "hard_or_full_trip": "full",
        "batch_size": (8, 16),
        "restore_iter": 0,
        "total_iter": 80000,
        "margin": 0.2,
        "num_workers": 0,
        "frame_num": 30,
        "model_name": "GaitSet",
    },
}
