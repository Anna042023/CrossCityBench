from __future__ import annotations

import csv
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch


def _as_matrix_from_pickle(obj: Any) -> np.ndarray:
    if isinstance(obj, np.ndarray):
        return obj
    if isinstance(obj, (list, tuple)):
        # Common DCRNN format: (sensor_ids, sensor_id_to_ind, adj_mx)
        for item in reversed(obj):
            if isinstance(item, np.ndarray) and item.ndim == 2 and item.shape[0] == item.shape[1]:
                return item
    if isinstance(obj, dict):
        for key in ("adj_mx", "adj", "A", "matrix", "weight", "weights"):
            if key in obj:
                arr = np.asarray(obj[key])
                if arr.ndim == 2:
                    return arr
    raise ValueError("Could not find a square adjacency matrix in pickle object")


def _edge_list_to_matrix(df: pd.DataFrame, n_nodes: int, sigma2: float = 0.1, epsilon: float = 0.5) -> np.ndarray:
    if df.shape[1] < 2:
        raise ValueError("Edge list needs at least two columns")
    cols = list(df.columns)
    src = pd.to_numeric(df[cols[0]], errors="coerce").to_numpy()
    dst = pd.to_numeric(df[cols[1]], errors="coerce").to_numpy()
    if df.shape[1] >= 3:
        val = pd.to_numeric(df[cols[2]], errors="coerce").to_numpy()
    else:
        val = np.ones(len(df), dtype=np.float64)

    good = np.isfinite(src) & np.isfinite(dst) & np.isfinite(val)
    src, dst, val = src[good].astype(int), dst[good].astype(int), val[good].astype(float)

    # If node ids are not compact 0..N-1, map unique ids by sorted order.
    unique_ids = np.unique(np.concatenate([src, dst]))
    if src.min(initial=0) < 0 or dst.min(initial=0) < 0 or unique_ids.max(initial=0) >= n_nodes:
        if len(unique_ids) != n_nodes:
            raise ValueError(
                f"Edge list node ids cannot be mapped to n_nodes={n_nodes}; found {len(unique_ids)} unique ids"
            )
        mapping = {v: i for i, v in enumerate(unique_ids.tolist())}
        src = np.array([mapping[v] for v in src], dtype=int)
        dst = np.array([mapping[v] for v in dst], dtype=int)

    W = np.zeros((n_nodes, n_nodes), dtype=np.float64)
    finite_val = val[np.isfinite(val)]
    if finite_val.size and np.nanmax(np.abs(finite_val)) > 1.0:
        # Treat as physical distance and apply the same Gaussian idea as supplied STGCN.
        scale = np.nanmax(np.abs(finite_val))
        d = val / (scale + 1e-12)
        w = np.exp(-(d * d) / sigma2)
        w[w < epsilon] = 0.0
    else:
        w = val

    W[src, dst] = w
    W[dst, src] = np.maximum(W[dst, src], w)
    np.fill_diagonal(W, 0.0)
    return W


def load_adjacency(path: str | Path, n_nodes: int, symmetrize: bool = True) -> np.ndarray:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Adjacency file not found: {path}")
    suffix = path.suffix.lower()

    if suffix == ".npy":
        W = np.load(path, allow_pickle=True)
    elif suffix == ".npz":
        z = np.load(path, allow_pickle=True)
        key = next((k for k in ("adj_mx", "adj", "A", "matrix", "data") if k in z.files), z.files[0])
        W = z[key]
    elif suffix in (".pkl", ".pickle"):
        with open(path, "rb") as f:
            W = _as_matrix_from_pickle(pickle.load(f, encoding="latin1"))
    elif suffix in (".csv", ".txt"):
        # First try square matrix without header.
        raw = pd.read_csv(path, header=None)
        arr = raw.apply(pd.to_numeric, errors="coerce").to_numpy()
        if arr.ndim == 2 and arr.shape[0] == arr.shape[1] == n_nodes and np.isfinite(arr).mean() > 0.95:
            W = arr
        else:
            raw2 = pd.read_csv(path)
            W = _edge_list_to_matrix(raw2, n_nodes)
    else:
        raise ValueError(f"Unsupported adjacency format: {suffix}")

    W = np.asarray(W, dtype=np.float64)
    if W.shape != (n_nodes, n_nodes):
        raise ValueError(f"Adjacency shape {W.shape} does not match n_nodes={n_nodes}")
    W[~np.isfinite(W)] = 0.0

    # Supplied STGCN converts distance matrices using W/10000 and a Gaussian threshold.
    # Apply that only when matrix magnitude clearly looks like physical distance.
    unique = np.unique(W)
    is_binary = set(unique.tolist()).issubset({0.0, 1.0})
    if not is_binary and np.nanmax(np.abs(W)) > 1.5:
        d = W / 10000.0
        W2 = d * d
        sim = np.exp(-W2 / 0.1)
        W = sim * (sim >= 0.5)
        np.fill_diagonal(W, 0.0)

    if symmetrize:
        W = np.maximum(W, W.T)
    np.fill_diagonal(W, 0.0)
    return W.astype(np.float32)


def scaled_laplacian(W: np.ndarray) -> np.ndarray:
    W = np.asarray(W, dtype=np.float64)
    d = W.sum(axis=1)
    d_inv_sqrt = np.zeros_like(d)
    nz = d > 1e-12
    d_inv_sqrt[nz] = 1.0 / np.sqrt(d[nz])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L = np.eye(W.shape[0], dtype=np.float64) - D_inv_sqrt @ W @ D_inv_sqrt
    eigvals = np.linalg.eigvals(L)
    lambda_max = float(np.max(np.real(eigvals))) if eigvals.size else 2.0
    if not np.isfinite(lambda_max) or lambda_max < 1e-12:
        lambda_max = 2.0
    return (2.0 * L / lambda_max - np.eye(W.shape[0], dtype=np.float64)).astype(np.float32)


def cheb_polynomials(L_tilde: np.ndarray, ks: int) -> np.ndarray:
    n = L_tilde.shape[0]
    t0 = np.eye(n, dtype=np.float32)
    if ks == 1:
        return t0[None, ...]
    t1 = L_tilde.astype(np.float32)
    polys = [t0, t1]
    for _ in range(2, ks):
        polys.append(2.0 * L_tilde @ polys[-1] - polys[-2])
    return np.stack(polys[:ks], axis=0).astype(np.float32)


def build_cheb_tensor(W: np.ndarray, ks: int, device: torch.device | str = "cpu") -> torch.Tensor:
    L = scaled_laplacian(W)
    T = cheb_polynomials(L, ks)
    return torch.from_numpy(T).to(device)
