from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader


DATA_EXTS = {".npz", ".npy", ".csv", ".txt", ".h5", ".hdf", ".hdf5"}
ADJ_HINTS = ("adj", "adjacency", "distance", "dist", "weight", "graph", "w_")
DATA_HINTS = ("data", "flow", "speed", "metr", "pems", "values", "traffic")


@dataclass
class StandardScaler:
    mean: float
    std: float

    def transform(self, x):
        return (x - self.mean) / self.std

    def inverse_transform(self, x):
        return x * self.std + self.mean


class OneStepWindowDataset(Dataset):
    def __init__(self, series: np.ndarray, history: int, stride: int = 1):
        self.series = np.asarray(series, dtype=np.float32)
        self.history = int(history)
        self.starts = np.arange(0, len(self.series) - self.history, stride, dtype=np.int64)
        if len(self.starts) == 0:
            raise ValueError("Not enough data to construct one-step training windows")

    def __len__(self):
        return len(self.starts)

    def __getitem__(self, i):
        s = int(self.starts[i])
        x = self.series[s:s + self.history]
        y = self.series[s + self.history]
        return torch.from_numpy(x), torch.from_numpy(y)


class MultiStepWindowDataset(Dataset):
    def __init__(self, series: np.ndarray, history: int, horizon: int, stride: int = 1):
        self.series = np.asarray(series, dtype=np.float32)
        self.history = int(history)
        self.horizon = int(horizon)
        self.starts = np.arange(0, len(self.series) - history - horizon + 1, stride, dtype=np.int64)
        if len(self.starts) == 0:
            raise ValueError("Not enough data to construct multi-step evaluation windows")

    def __len__(self):
        return len(self.starts)

    def __getitem__(self, i):
        s = int(self.starts[i])
        x = self.series[s:s + self.history]
        y = self.series[s + self.history:s + self.history + self.horizon]
        return torch.from_numpy(x), torch.from_numpy(y)


def _extract_npz(z, feature_idx: int = 0):
    preferred = ["data", "x", "flow", "speed", "values", "traffic"]
    key = next((k for k in preferred if k in z.files), None)
    if key is None:
        # Prefer arrays that look like time x node x feature.
        candidates = []
        for k in z.files:
            try:
                arr = np.asarray(z[k])
                if arr.ndim in (2, 3):
                    candidates.append((arr.size, k))
            except Exception:
                pass
        if not candidates:
            raise ValueError(f"No usable 2D/3D array found in NPZ keys: {z.files}")
        key = max(candidates)[1]
    return np.asarray(z[key])


def load_series(path: str | Path, feature_idx: int = 0) -> np.ndarray:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Traffic data file not found: {path}")
    suffix = path.suffix.lower()

    if suffix == ".npz":
        z = np.load(path, allow_pickle=True)
        arr = _extract_npz(z, feature_idx)
    elif suffix == ".npy":
        arr = np.load(path, allow_pickle=True)
    elif suffix in (".h5", ".hdf", ".hdf5"):
        try:
            obj = pd.read_hdf(path)
        except Exception as e:
            raise RuntimeError(f"Failed to read HDF5 {path}: {e}") from e
        arr = obj.values if hasattr(obj, "values") else np.asarray(obj)
    elif suffix in (".csv", ".txt"):
        # Most traffic matrices are headerless; if that yields an object column, retry with header.
        df = pd.read_csv(path, header=None)
        numeric = df.apply(pd.to_numeric, errors="coerce")
        if numeric.notna().mean().mean() < 0.9:
            df = pd.read_csv(path)
            numeric = df.select_dtypes(include=[np.number])
        arr = numeric.to_numpy()
    else:
        raise ValueError(f"Unsupported data format: {suffix}")

    arr = np.asarray(arr)
    if arr.ndim == 3:
        if feature_idx < 0 or feature_idx >= arr.shape[-1]:
            raise ValueError(f"feature_idx={feature_idx} invalid for shape={arr.shape}")
        arr = arr[..., feature_idx]
    elif arr.ndim == 1:
        arr = arr[:, None]
    elif arr.ndim != 2:
        raise ValueError(f"Expected [T,N] or [T,N,C], got shape={arr.shape} from {path}")

    arr = arr.astype(np.float32)
    arr[~np.isfinite(arr)] = np.nan
    # Per-node interpolation, then median fallback.
    df = pd.DataFrame(arr)
    df = df.interpolate(limit_direction="both", axis=0)
    med = df.median(axis=0)
    df = df.fillna(med).fillna(0.0)
    arr = df.to_numpy(dtype=np.float32)
    return arr


def split_indices(T: int, train_ratio=0.7, val_ratio=0.1):
    train_end = int(T * train_ratio)
    val_end = int(T * (train_ratio + val_ratio))
    if not (0 < train_end < val_end < T):
        raise ValueError("Invalid train/val split")
    return train_end, val_end


def prepare_domain(
    data_path: str | Path,
    history: int,
    horizon: int,
    feature_idx: int = 0,
    train_ratio: float = 0.7,
    val_ratio: float = 0.1,
    train_days: Optional[int] = None,
    steps_per_day: int = 288,
    train_stride: int = 1,
    eval_stride: int = 1,
):
    raw = load_series(data_path, feature_idx=feature_idx)
    T, N = raw.shape
    train_end, val_end = split_indices(T, train_ratio, val_ratio)

    if train_days is None:
        train_raw = raw[:train_end]
    else:
        usable = min(train_end, int(train_days) * int(steps_per_day))
        train_raw = raw[:usable]
        if usable < history + 1:
            raise ValueError(f"train_days={train_days} gives only {usable} steps")

    scaler = StandardScaler(float(np.mean(train_raw)), float(np.std(train_raw) + 1e-8))
    train = scaler.transform(train_raw).astype(np.float32)
    val = scaler.transform(raw[train_end:val_end]).astype(np.float32)
    test = scaler.transform(raw[val_end:]).astype(np.float32)

    train_ds = OneStepWindowDataset(train, history, stride=train_stride)
    val_one_ds = OneStepWindowDataset(val, history, stride=eval_stride)
    val_multi_ds = MultiStepWindowDataset(val, history, horizon, stride=eval_stride)
    test_multi_ds = MultiStepWindowDataset(test, history, horizon, stride=eval_stride)

    return {
        "raw_shape": raw.shape,
        "n_nodes": N,
        "train_steps": len(train),
        "val_steps": len(val),
        "test_steps": len(test),
        "scaler": scaler,
        "train_ds": train_ds,
        "val_one_ds": val_one_ds,
        "val_multi_ds": val_multi_ds,
        "test_multi_ds": test_multi_ds,
    }


def make_loader(ds: Dataset, batch_size: int, shuffle: bool, num_workers: int = 0):
    return DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=False,
    )


def _score_data_candidate(path: Path, dataset_name: str) -> float:
    s = path.name.lower()
    score = 0.0
    d = dataset_name.lower().replace("-", "").replace("_", "")
    norm = s.replace("-", "").replace("_", "")
    if d in norm:
        score += 5
    if any(h in s for h in DATA_HINTS):
        score += 2
    if any(h in s for h in ADJ_HINTS):
        score -= 8
    if path.suffix.lower() in (".npz", ".h5", ".hdf5"):
        score += 1
    return score


def _score_adj_candidate(path: Path, dataset_name: str) -> float:
    s = path.name.lower()
    score = 0.0
    d = dataset_name.lower().replace("-", "").replace("_", "")
    norm = s.replace("-", "").replace("_", "")
    if d in norm:
        score += 3
    if any(h in s for h in ADJ_HINTS):
        score += 6
    if path.suffix.lower() in (".pkl", ".pickle"):
        score += 2
    return score


def autodiscover_dataset_files(data_root: str | Path, dataset_name: str) -> Tuple[Path, Path]:
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root not found: {root}")

    aliases = {
        "PEMS03": ["pems03", "pemsd3", "pems3"],
        "PEMS04": ["pems04", "pemsd4", "pems4"],
        "PEMS08": ["pems08", "pemsd8", "pems8"],
        "METR-LA": ["metr-la", "metr_la", "metrla"],
        "PEMS-BAY": ["pems-bay", "pems_bay", "pemsbay"],
        "SZ-Taxi": ["sz-taxi", "sz_taxi", "sztaxi", "sz"],
    }
    names = aliases.get(dataset_name, [dataset_name.lower()])

    dirs = []
    for p in root.rglob("*"):
        if p.is_dir():
            q = p.name.lower()
            if any(a in q for a in names):
                dirs.append(p)
    search_roots = dirs if dirs else [root]

    candidates = []
    for sr in search_roots:
        for p in sr.rglob("*"):
            if p.is_file() and p.suffix.lower() in DATA_EXTS.union({".pkl", ".pickle"}):
                candidates.append(p)

    data_cands = [p for p in candidates if p.suffix.lower() in DATA_EXTS]
    adj_cands = [p for p in candidates if p.suffix.lower() in DATA_EXTS.union({".pkl", ".pickle"})]
    if not data_cands:
        raise FileNotFoundError(f"No data candidate found for {dataset_name} under {root}")

    data_path = max(data_cands, key=lambda p: _score_data_candidate(p, dataset_name))
    adj_scored = [(p, _score_adj_candidate(p, dataset_name)) for p in adj_cands if p != data_path]
    adj_scored = [x for x in adj_scored if x[1] > 0]
    if not adj_scored:
        raise FileNotFoundError(
            f"No adjacency candidate found for {dataset_name}. Pass --source_adj/--target_adj explicitly."
        )
    adj_path = max(adj_scored, key=lambda x: x[1])[0]
    return data_path, adj_path
