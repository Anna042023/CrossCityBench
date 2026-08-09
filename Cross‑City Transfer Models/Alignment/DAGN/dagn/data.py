from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader


EXPECTED_NODES = {
    "PEMS03": 358,
    "PEMS04": 307,
    "PEMS08": 170,
    "METR-LA": 207,
    "PEMS-BAY": 325,
    "SZ-TAXI": 156,
}

INTERVAL_MINUTES = {
    "PEMS03": 5,
    "PEMS04": 5,
    "PEMS08": 5,
    "METR-LA": 5,
    "PEMS-BAY": 5,
    "SZ-TAXI": 15,
}


def canonical_name(name: str) -> str:
    n = name.upper().replace("_", "-")
    aliases = {
        "METRLA": "METR-LA",
        "PEMSBAY": "PEMS-BAY",
        "SZTAXI": "SZ-TAXI",
        "PEMS-03": "PEMS03",
        "PEMS-04": "PEMS04",
        "PEMS-08": "PEMS08",
    }
    return aliases.get(n, n)


def _candidate_dirs(root: Path, name: str):
    variants = [name, name.lower(), name.replace("-", "_"), name.replace("-", "")]
    dirs = [root]
    for v in variants:
        dirs.append(root / v)
    # preserve order, remove duplicates
    out = []
    seen = set()
    for d in dirs:
        s = str(d)
        if s not in seen:
            out.append(d)
            seen.add(s)
    return out


def resolve_data_path(root: str | Path, name: str, explicit: Optional[str] = None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            raise FileNotFoundError(f"Data file not found: {p}")
        return p

    root = Path(root)
    name = canonical_name(name)
    variants = [name, name.lower(), name.replace("-", "_"), name.replace("-", "")]
    filenames = []
    for v in variants:
        filenames += [f"{v}.npz", f"{v}.npy", f"{v}.h5", f"{v}.hdf5", f"{v}.csv"]
    filenames += ["data.npz", "data.npy", "data.h5", "data.hdf5", "traffic.npz", "traffic.npy"]

    for d in _candidate_dirs(root, name):
        for fn in filenames:
            p = d / fn
            if p.exists() and p.is_file():
                return p

    raise FileNotFoundError(
        f"Cannot auto-find data for {name} under {root}. "
        f"Pass --source_data/--target_data explicitly."
    )


def resolve_sensor_ids_path(root: str | Path, name: str, explicit: Optional[str] = None) -> Optional[Path]:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            raise FileNotFoundError(f"Sensor-id file not found: {p}")
        return p
    root = Path(root)
    name = canonical_name(name)
    candidates = [
        "sensor_ids.txt", "graph_sensor_ids.txt", f"{name}.txt", f"{name.lower()}.txt",
        f"{name.replace('-', '_')}.txt",
    ]
    for d in _candidate_dirs(root, name):
        for fn in candidates:
            p = d / fn
            if p.exists() and p.is_file():
                return p
    return None


def resolve_adj_path(root: str | Path, name: str, explicit: Optional[str] = None) -> Optional[Path]:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            raise FileNotFoundError(f"Adjacency file not found: {p}")
        return p

    root = Path(root)
    name = canonical_name(name)
    variants = [name, name.lower(), name.replace("-", "_"), name.replace("-", "")]
    common = [
        "adj_mx.pkl", "adj.pkl", "adjacency.pkl", "adj.npy", "adj.npz",
        "adjacency.npy", "adjacency.npz", "distance.csv", "distances.csv",
        "edges.csv", "edge.csv", "graph.csv",
    ]
    for v in variants:
        common += [
            f"{v}_adj.npy", f"{v}_adj.npz", f"{v}_adj.pkl",
            f"adj_{v}.npy", f"adj_{v}.npz", f"adj_{v}.pkl",
            f"{v}.csv",
        ]
    for d in _candidate_dirs(root, name):
        for fn in common:
            p = d / fn
            if p.exists() and p.is_file():
                return p
    return None


def _extract_npz_array(obj):
    preferred = ["data", "x", "flow", "speed", "values"]
    for k in preferred:
        if k in obj.files:
            return obj[k], k
    if len(obj.files) == 1:
        k = obj.files[0]
        return obj[k], k
    # choose the largest numeric array with >=2 dimensions
    ranked = []
    for k in obj.files:
        a = np.asarray(obj[k])
        if np.issubdtype(a.dtype, np.number) and a.ndim >= 2:
            ranked.append((a.size, k, a))
    if not ranked:
        raise ValueError(f"No suitable numeric data array in NPZ keys: {obj.files}")
    _, k, a = max(ranked, key=lambda x: x[0])
    return a, k


def load_traffic_array(path: str | Path, name: str, feature_idx: int = 0) -> np.ndarray:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".npz":
        obj = np.load(path, allow_pickle=True)
        arr, key = _extract_npz_array(obj)
        print(f"[Data] {name}: NPZ key='{key}', raw shape={np.asarray(arr).shape}")
    elif suffix == ".npy":
        arr = np.load(path, allow_pickle=True)
    elif suffix in {".h5", ".hdf5"}:
        try:
            df = pd.read_hdf(path)
        except Exception:
            # Try common key names if the HDF has multiple objects.
            with pd.HDFStore(path, mode="r") as store:
                keys = store.keys()
                if not keys:
                    raise ValueError(f"No datasets in HDF5 file: {path}")
                df = store[keys[0]]
        arr = df.values if hasattr(df, "values") else np.asarray(df)
    elif suffix == ".csv":
        df = pd.read_csv(path)
        numeric = df.select_dtypes(include=[np.number])
        if numeric.shape[1] == 0:
            raise ValueError(f"No numeric columns found in {path}")
        arr = numeric.values
    else:
        raise ValueError(f"Unsupported data format: {path.suffix}")

    arr = np.asarray(arr)
    expected = EXPECTED_NODES.get(canonical_name(name))

    if arr.ndim == 1:
        arr = arr[:, None, None]
    elif arr.ndim == 2:
        # Expected [T,N]. If [N,T], transpose using known sensor count.
        if expected is not None and arr.shape[0] == expected and arr.shape[1] != expected:
            arr = arr.T
        arr = arr[:, :, None]
    elif arr.ndim == 3:
        # Expected [T,N,C]. Detect [N,T,C].
        if expected is not None and arr.shape[0] == expected and arr.shape[1] != expected:
            arr = np.transpose(arr, (1, 0, 2))
        if feature_idx < 0 or feature_idx >= arr.shape[-1]:
            raise ValueError(
                f"feature_idx={feature_idx} is invalid for {name} data shape {arr.shape}"
            )
        arr = arr[..., feature_idx : feature_idx + 1]
    else:
        raise ValueError(f"Expected [T,N] or [T,N,C], got shape={arr.shape}")

    arr = arr.astype(np.float32)
    arr[~np.isfinite(arr)] = np.nan
    # Fill missing values per node using the node median, then 0 as final fallback.
    for n in range(arr.shape[1]):
        col = arr[:, n, 0]
        med = np.nanmedian(col) if np.isfinite(col).any() else 0.0
        col[~np.isfinite(col)] = med
        arr[:, n, 0] = col

    if expected is not None and arr.shape[1] != expected:
        print(
            f"[Warn] {name}: expected {expected} sensors from the paper, "
            f"but loaded {arr.shape[1]}. Continuing with loaded data."
        )
    print(f"[Data] {name}: final shape={arr.shape} [T,N,C]")
    return arr


def load_sensor_ids(path: Optional[str | Path]):
    if path is None:
        return None
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="ignore")
    # Common formats: comma-separated IDs on one line or one ID per line.
    tokens = [x.strip() for x in text.replace("\n", ",").split(",") if x.strip()]
    return tokens or None


def _edge_list_to_adj(df: pd.DataFrame, n_nodes: int, sensor_ids=None) -> np.ndarray:
    if df.shape[1] < 2:
        raise ValueError("Edge-list CSV must have at least two columns")
    src = df.iloc[:, 0].astype(str).tolist()
    dst = df.iloc[:, 1].astype(str).tolist()

    if sensor_ids is not None:
        mapping = {str(s): i for i, s in enumerate(sensor_ids)}
        pairs = [(mapping[s], mapping[d]) for s, d in zip(src, dst) if s in mapping and d in mapping]
    else:
        pairs = []
        for s, d in zip(src, dst):
            try:
                si, di = int(float(s)), int(float(d))
            except Exception:
                continue
            if 0 <= si < n_nodes and 0 <= di < n_nodes:
                pairs.append((si, di))

    if not pairs:
        raise ValueError(
            "Could not map edge-list node IDs to data columns. Provide --source_sensor_ids/"
            "--target_sensor_ids when the CSV uses external sensor IDs."
        )
    A = np.zeros((n_nodes, n_nodes), dtype=np.float32)
    for i, j in pairs:
        A[i, j] = 1.0
        A[j, i] = 1.0
    return A


def load_adjacency(path: Optional[str | Path], n_nodes: int, sensor_ids=None, allow_identity=False) -> np.ndarray:
    if path is None:
        if allow_identity:
            print("[Warn] Adjacency not found; using identity graph. This is NOT paper-faithful.")
            return np.eye(n_nodes, dtype=np.float32)
        raise FileNotFoundError(
            "Adjacency file was not found. Pass --source_adj/--target_adj, or use "
            "--allow_identity_adj only for a smoke test."
        )

    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".npy":
        obj = np.load(p, allow_pickle=True)
        A = np.asarray(obj)
    elif suffix == ".npz":
        obj = np.load(p, allow_pickle=True)
        preferred = ["adj", "adj_mx", "A", "data"]
        key = next((k for k in preferred if k in obj.files), obj.files[0])
        A = np.asarray(obj[key])
    elif suffix in {".pkl", ".pickle"}:
        with p.open("rb") as f:
            obj = pickle.load(f, encoding="latin1")
        if isinstance(obj, (tuple, list)) and len(obj) >= 3:
            # DCRNN-style: (sensor_ids, sensor_id_to_ind, adj_mx)
            A = np.asarray(obj[-1])
        elif isinstance(obj, dict):
            for k in ["adj_mx", "adj", "A"]:
                if k in obj:
                    A = np.asarray(obj[k])
                    break
            else:
                raise ValueError(f"Cannot identify adjacency in pickle keys={list(obj.keys())[:10]}")
        else:
            A = np.asarray(obj)
    elif suffix in {".csv", ".txt"}:
        # First try as a numeric square matrix.
        try:
            raw = pd.read_csv(p, header=None)
            num = raw.apply(pd.to_numeric, errors="coerce")
            if num.shape[0] == n_nodes and num.shape[1] == n_nodes and num.notna().all().all():
                A = num.values
            else:
                # Re-read with header inference; common PeMS distance files have headers.
                df = pd.read_csv(p)
                A = _edge_list_to_adj(df, n_nodes, sensor_ids)
        except Exception:
            df = pd.read_csv(p)
            A = _edge_list_to_adj(df, n_nodes, sensor_ids)
    else:
        raise ValueError(f"Unsupported adjacency format: {p.suffix}")

    A = np.asarray(A, dtype=np.float32)
    if A.shape != (n_nodes, n_nodes):
        raise ValueError(f"Adjacency shape {A.shape} does not match n_nodes={n_nodes}")
    A = (A > 0).astype(np.float32)
    np.fill_diagonal(A, 0.0)
    return A


@dataclass
class StandardScaler:
    mean: float
    std: float

    def transform(self, x):
        return (x - self.mean) / self.std

    def inverse_transform(self, x):
        return x * self.std + self.mean


def fit_scaler(data: np.ndarray, end_idx: int) -> StandardScaler:
    train = data[:end_idx]
    mean = float(np.mean(train))
    std = float(np.std(train))
    if std < 1e-6:
        std = 1.0
    return StandardScaler(mean, std)


class WindowDataset(Dataset):
    def __init__(self, data: np.ndarray, history: int, horizon: int, target_start: int, target_end: int):
        self.data = data
        self.history = int(history)
        self.horizon = int(horizon)
        self.indices = []
        first = max(int(target_start), self.history)
        last = int(target_end) - self.horizon
        for target_t in range(first, last + 1):
            input_t = target_t - self.history
            if input_t >= 0:
                self.indices.append(target_t)
        if not self.indices:
            raise ValueError(
                f"No windows can be built: history={history}, horizon={horizon}, "
                f"target range=[{target_start},{target_end})"
            )

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        t = self.indices[idx]
        x = self.data[t - self.history : t]          # [H,N,C]
        y = self.data[t : t + self.horizon]          # [P,N,C]
        x = np.transpose(x, (1, 0, 2))               # [N,H,C]
        y = np.transpose(y, (1, 0, 2))               # [N,P,C]
        return torch.from_numpy(x.copy()), torch.from_numpy(y.copy())


@dataclass
class DomainPrepared:
    name: str
    data_raw: np.ndarray
    data_norm: np.ndarray
    adj: np.ndarray
    scaler: StandardScaler
    train_end: int
    val_end: int
    target_train_end: int
    interval_minutes: int


@dataclass
class TransferPrepared:
    source: DomainPrepared
    target: DomainPrepared
    history: int
    horizon: int


def prepare_transfer_data(args) -> TransferPrepared:
    src_name = canonical_name(args.source)
    tgt_name = canonical_name(args.target)

    src_data_path = resolve_data_path(args.data_root, src_name, args.source_data)
    tgt_data_path = resolve_data_path(args.data_root, tgt_name, args.target_data)
    src_ids_path = resolve_sensor_ids_path(args.data_root, src_name, args.source_sensor_ids)
    tgt_ids_path = resolve_sensor_ids_path(args.data_root, tgt_name, args.target_sensor_ids)
    src_adj_path = resolve_adj_path(args.data_root, src_name, args.source_adj)
    tgt_adj_path = resolve_adj_path(args.data_root, tgt_name, args.target_adj)

    # Avoid silently treating a traffic CSV as an adjacency CSV when auto-discovery
    # returns the same file for both roles. Explicit adjacency paths still take priority.
    if args.source_adj is None and src_adj_path is not None and src_adj_path.resolve() == src_data_path.resolve():
        src_adj_path = None
    if args.target_adj is None and tgt_adj_path is not None and tgt_adj_path.resolve() == tgt_data_path.resolve():
        tgt_adj_path = None

    print(f"[Path] source data: {src_data_path}")
    print(f"[Path] target data: {tgt_data_path}")
    print(f"[Path] source adj : {src_adj_path}")
    print(f"[Path] target adj : {tgt_adj_path}")

    src_raw = load_traffic_array(src_data_path, src_name, args.feature_idx)
    tgt_raw = load_traffic_array(tgt_data_path, tgt_name, args.feature_idx)

    src_ids = load_sensor_ids(src_ids_path)
    tgt_ids = load_sensor_ids(tgt_ids_path)
    src_adj = load_adjacency(src_adj_path, src_raw.shape[1], src_ids, args.allow_identity_adj)
    tgt_adj = load_adjacency(tgt_adj_path, tgt_raw.shape[1], tgt_ids, args.allow_identity_adj)

    src_interval = args.source_interval or INTERVAL_MINUTES.get(src_name, 5)
    tgt_interval = args.target_interval or INTERVAL_MINUTES.get(tgt_name, 5)
    if src_interval != tgt_interval:
        # The paper evaluates PEMS-BAY (5-min) -> SZ-Taxi (15-min) but does not
        # describe the exact temporal alignment. To make the joint node-wise
        # model well-defined, align the source sequence to the target interval.
        if tgt_interval > src_interval and tgt_interval % src_interval == 0:
            factor = tgt_interval // src_interval
            usable = (len(src_raw) // factor) * factor
            src_raw = src_raw[:usable].reshape(usable // factor, factor, src_raw.shape[1], src_raw.shape[2]).mean(axis=1)
            print(f"[Data] Aligned source interval {src_interval}min -> {tgt_interval}min by block mean (factor={factor}).")
            src_interval = tgt_interval
        else:
            raise ValueError(
                f"Source interval={src_interval} min and target interval={tgt_interval} min cannot be aligned automatically. "
                "Provide pre-aligned data or matching --source_interval/--target_interval."
            )

    def split_indices(T):
        tr = int(T * 0.7)
        va = int(T * 0.8)
        return tr, va

    src_train_end, src_val_end = split_indices(len(src_raw))
    tgt_train_end_full, tgt_val_end = split_indices(len(tgt_raw))

    tgt_steps_per_day = int(round(24 * 60 / tgt_interval))
    tgt_10day_end = min(tgt_train_end_full, args.target_train_days * tgt_steps_per_day)

    # The paper uses all available source training data and only 10 days of target training data.
    src_scaler = fit_scaler(src_raw, src_train_end)
    tgt_scaler = fit_scaler(tgt_raw, tgt_10day_end)
    src_norm = src_scaler.transform(src_raw).astype(np.float32)
    tgt_norm = tgt_scaler.transform(tgt_raw).astype(np.float32)

    source = DomainPrepared(
        name=src_name,
        data_raw=src_raw,
        data_norm=src_norm,
        adj=src_adj,
        scaler=src_scaler,
        train_end=src_train_end,
        val_end=src_val_end,
        target_train_end=src_train_end,
        interval_minutes=src_interval,
    )
    target = DomainPrepared(
        name=tgt_name,
        data_raw=tgt_raw,
        data_norm=tgt_norm,
        adj=tgt_adj,
        scaler=tgt_scaler,
        train_end=tgt_train_end_full,
        val_end=tgt_val_end,
        target_train_end=tgt_10day_end,
        interval_minutes=tgt_interval,
    )
    return TransferPrepared(source, target, args.history, args.horizon)


def build_dataloaders(prepared: TransferPrepared, batch_size=16, num_workers=0):
    s = prepared.source
    t = prepared.target
    H, P = prepared.history, prepared.horizon

    datasets = {
        "src_train": WindowDataset(s.data_norm, H, P, 0, s.train_end),
        "src_val": WindowDataset(s.data_norm, H, P, s.train_end, s.val_end),
        "src_test": WindowDataset(s.data_norm, H, P, s.val_end, len(s.data_norm)),
        "tgt_train": WindowDataset(t.data_norm, H, P, 0, t.target_train_end),
        "tgt_val": WindowDataset(t.data_norm, H, P, t.train_end, t.val_end),
        "tgt_test": WindowDataset(t.data_norm, H, P, t.val_end, len(t.data_norm)),
    }

    loaders = {}
    for k, ds in datasets.items():
        is_train = k.endswith("train")
        loaders[k] = DataLoader(
            ds,
            batch_size=batch_size,
            shuffle=is_train,
            drop_last=is_train,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
        )
        print(f"[Loader] {k}: {len(ds)} windows, {len(loaders[k])} batches")
    return datasets, loaders
