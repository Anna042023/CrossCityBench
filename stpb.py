# stpb.py
# Build STPB prototypes for cross-city transfer (PeMS-BAY -> METR-LA)
# Using: source train (70%) + target train (70%) following label_end split rule.
#
# Author: ChatGPT
#
# Example:
#   python stpb.py \
#     --root_dir /home/zc/wanganna \
#     --source_name PEMS-BAY --target_name METR-LA \
#     --input_len 12 --output_len 12 \
#     --hidden_dim 64 --embed_dim 128 \
#     --K 16 \
#     --train_steps 2000 --batch_size 16 --mask_ratio 0.2 \
#     --windows_per_domain 60000 \
#     --out_dir /home/zc/wanganna/STPB_bay2la
#
# Outputs:
#   out_dir/stpb_prototypes.npy       (K, embed_dim), L2-normalized
#   out_dir/stpb_meta.json            metadata (split, shapes, params)
#   out_dir/stpb_training_log.txt     simple log

import os
import json
import math
import time
import random
import argparse
from typing import Dict, Tuple, Optional, List

import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

# Optional dependencies (will raise a friendly error if missing)
try:
    import pandas as pd
except Exception as e:
    pd = None

try:
    import h5py
except Exception as e:
    h5py = None

try:
    from sklearn.cluster import KMeans
except Exception as e:
    KMeans = None


# -----------------------------
# Reproducibility
# -----------------------------
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# -----------------------------
# H5 loader for METR-LA / PEMS-BAY
# -----------------------------
def _read_h5_as_numpy(h5_path: str) -> np.ndarray:
    """
    Tries to read .h5 in common traffic speed datasets (METR-LA / PEMS-BAY).
    Preferred format is pandas HDFStore key 'df' (DCRNN style), shape (T, N).
    Returns float32 numpy array with shape (T, N, 1).
    """
    if not os.path.exists(h5_path):
        raise FileNotFoundError(f"File not found: {h5_path}")

    # 1) pandas read_hdf (most common)
    if pd is not None:
        # Common keys: 'df', sometimes others
        for key in ["df", "data", "speed", "flows", "values"]:
            try:
                df = pd.read_hdf(h5_path, key=key)
                # df: (T, N)
                if hasattr(df, "values"):
                    arr = df.values.astype(np.float32)
                    if arr.ndim == 2:
                        return arr[:, :, None]
            except Exception:
                pass

        # If keys unknown, try listing keys
        try:
            with pd.HDFStore(h5_path, mode="r") as store:
                keys = store.keys()
            for k in keys:
                try:
                    df = pd.read_hdf(h5_path, key=k)
                    arr = df.values.astype(np.float32)
                    if arr.ndim == 2:
                        return arr[:, :, None]
                except Exception:
                    pass
        except Exception:
            pass

    # 2) fallback h5py
    if h5py is None:
        raise RuntimeError(
            "Failed to read h5 with pandas, and h5py is not installed. "
            "Please install pandas and h5py."
        )

    with h5py.File(h5_path, "r") as f:
        # Try common datasets
        candidates = []
        def _collect(name, obj):
            if isinstance(obj, h5py.Dataset):
                candidates.append(name)
        f.visititems(_collect)

        # Heuristic: choose dataset with 2D or 3D and largest first dim (T)
        best = None
        best_score = -1
        for name in candidates:
            dset = f[name]
            shape = dset.shape
            if shape is None:
                continue
            if len(shape) == 2:
                T, N = shape
                score = T * N
            elif len(shape) == 3:
                T, N, C = shape
                score = T * N * max(1, C)
            else:
                continue
            if score > best_score:
                best_score = score
                best = name

        if best is None:
            raise RuntimeError(f"Could not find a suitable dataset in {h5_path}. Found keys: {candidates}")

        arr = f[best][...].astype(np.float32)
        if arr.ndim == 2:
            arr = arr[:, :, None]
        elif arr.ndim == 3 and arr.shape[-1] != 1:
            # keep only first channel if multi-channel
            arr = arr[:, :, :1]
        return arr


# -----------------------------
# Window sampling with label_end split rule
# -----------------------------
def compute_split_b1(T: int, train_ratio: float = 0.7) -> int:
    return int(math.floor(train_ratio * T))

def valid_starts(T: int, input_len: int, output_len: int, b1: int) -> np.ndarray:
    """
    A window starting at s is train-eligible if label_end = s + input_len + output_len <= b1.
    Also require s >= 0 and s + input_len + output_len <= T.
    """
    max_s_by_T = T - (input_len + output_len)
    if max_s_by_T < 0:
        return np.array([], dtype=np.int64)
    max_s_by_b1 = b1 - (input_len + output_len)
    max_s = min(max_s_by_T, max_s_by_b1)
    if max_s < 0:
        return np.array([], dtype=np.int64)
    return np.arange(0, max_s + 1, dtype=np.int64)


def fit_train_scaler(data: np.ndarray, b1: int, eps: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
    """
    data: (T, N, 1)
    Fit mean/std on [0:b1) time range (train segment) for each node independently.
    Return mean/std with shape (N, 1).
    """
    x = data[:b1]  # (b1, N, 1)
    mean = x.mean(axis=0)  # (N, 1)
    std = x.std(axis=0)    # (N, 1)
    std = np.maximum(std, eps)
    return mean.astype(np.float32), std.astype(np.float32)


def normalize_window(window: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    """
    window: (N, T, 1)
    mean/std: (N, 1)
    """
    # broadcast mean/std to (N, T, 1)
    return (window - mean[:, None, :]) / std[:, None, :]


# -----------------------------
# Pattern Encoder + Masked Reconstruction
# -----------------------------
class NodeTemporalEncoder(nn.Module):
    """
    Encode each node's time-series window independently via 1D conv over time.
    Input:  x (B, N, T, 1)
    Output: node_emb (B, N, H)
            win_emb  (B, D)  [mean pooled over nodes + projection]
    Also provides a simple decoder to reconstruct masked values in (B, N, T, 1)
    from node_emb.
    """
    def __init__(self, input_len: int, hidden_dim: int = 64, embed_dim: int = 128):
        super().__init__()
        self.input_len = input_len
        self.hidden_dim = hidden_dim
        self.embed_dim = embed_dim

        # per-node temporal conv: (B*N, 1, T) -> (B*N, hidden_dim, T)
        self.conv1 = nn.Conv1d(1, hidden_dim, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(hidden_dim, hidden_dim, kernel_size=3, padding=1)
        self.norm1 = nn.BatchNorm1d(hidden_dim)
        self.norm2 = nn.BatchNorm1d(hidden_dim)

        # projection to window embedding
        self.proj = nn.Linear(hidden_dim, embed_dim)

        # decoder reconstruct time-series from node_emb: (B, N, H) -> (B, N, T, 1)
        self.dec = nn.Linear(hidden_dim, input_len)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: (B, N, T, 1)
        """
        B, N, T, C = x.shape
        assert T == self.input_len and C == 1

        xn = x.reshape(B * N, T, 1).transpose(1, 2)  # (B*N, 1, T)

        h = self.conv1(xn)
        h = self.norm1(h)
        h = F.relu(h)

        h = self.conv2(h)
        h = self.norm2(h)
        h = F.relu(h)

        # time pooling -> (B*N, hidden_dim)
        h_pool = h.mean(dim=-1)

        node_emb = h_pool.reshape(B, N, self.hidden_dim)  # (B, N, H)

        # window embedding: mean pool nodes -> (B, H) -> proj -> (B, D)
        win_h = node_emb.mean(dim=1)
        win_emb = self.proj(win_h)

        return node_emb, win_emb

    def reconstruct(self, node_emb: torch.Tensor) -> torch.Tensor:
        """
        node_emb: (B, N, H)
        return x_hat: (B, N, T, 1)
        """
        B, N, H = node_emb.shape
        out = self.dec(node_emb)  # (B, N, T)
        out = out.unsqueeze(-1)   # (B, N, T, 1)
        return out


def masked_recon_loss(x: torch.Tensor, x_hat: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """
    x, x_hat: (B, N, T, 1)
    mask: boolean or 0/1 tensor, same shape, True/1 means masked positions to reconstruct
    Loss only computed on masked positions.
    """
    diff = (x_hat - x)
    diff = diff * mask
    denom = mask.sum().clamp(min=1.0)
    return (diff.pow(2).sum() / denom)


# -----------------------------
# Random window batch sampler
# -----------------------------
class RandomWindowBatcher:
    """
    Draws random windows from a domain's train-eligible starts.
    Keeps data in memory as numpy, returns torch tensors on the chosen device.
    """
    def __init__(
        self,
        data: np.ndarray,                 # (T, N, 1)
        starts: np.ndarray,               # eligible starts
        mean: np.ndarray, std: np.ndarray,
        input_len: int,
        batch_size: int,
        device: torch.device,
    ):
        self.data = data
        self.starts = starts
        self.mean = mean
        self.std = std
        self.input_len = input_len
        self.batch_size = batch_size
        self.device = device

        if len(self.starts) == 0:
            raise ValueError("No eligible starts found for this domain. Check T, input_len, output_len, split b1.")

    def sample_batch(self) -> torch.Tensor:
        idx = np.random.randint(0, len(self.starts), size=self.batch_size)
        s_list = self.starts[idx]

        # build batch: (B, N, T, 1)
        windows = []
        for s in s_list:
            w = self.data[s:s + self.input_len]  # (T, N, 1)
            w = np.transpose(w, (1, 0, 2))       # (N, T, 1)
            w = normalize_window(w, self.mean, self.std)
            windows.append(w)

        x = np.stack(windows, axis=0).astype(np.float32)  # (B, N, T, 1)
        xt = torch.from_numpy(x).to(self.device)
        return xt


# -----------------------------
# Build embeddings + KMeans prototypes
# -----------------------------
@torch.no_grad()
def collect_embeddings(
    encoder: NodeTemporalEncoder,
    data: np.ndarray,
    starts: np.ndarray,
    mean: np.ndarray,
    std: np.ndarray,
    input_len: int,
    device: torch.device,
    num_windows: int,
    batch_size: int,
) -> np.ndarray:
    """
    Collect num_windows window embeddings from random starts.
    Returns np array (num_windows, embed_dim)
    """
    encoder.eval()
    emb_list = []
    n_collected = 0
    while n_collected < num_windows:
        cur_bs = min(batch_size, num_windows - n_collected)
        # sample starts
        idx = np.random.randint(0, len(starts), size=cur_bs)
        s_list = starts[idx]

        windows = []
        for s in s_list:
            w = data[s:s + input_len]     # (T, N, 1)
            w = np.transpose(w, (1, 0, 2))  # (N, T, 1)
            w = normalize_window(w, mean, std)
            windows.append(w)
        x = np.stack(windows, axis=0).astype(np.float32)  # (B, N, T, 1)

        xt = torch.from_numpy(x).to(device)
        _, win_emb = encoder(xt)  # (B, D)
        win_emb = F.normalize(win_emb, p=2, dim=-1)
        emb_list.append(win_emb.detach().cpu().numpy())
        n_collected += cur_bs

    return np.concatenate(emb_list, axis=0)


def run_kmeans(emb: np.ndarray, K: int, seed: int = 42) -> np.ndarray:
    if KMeans is None:
        raise RuntimeError("scikit-learn is required for KMeans. Please install scikit-learn.")
    km = KMeans(n_clusters=K, random_state=seed, n_init="auto")
    km.fit(emb)
    centers = km.cluster_centers_.astype(np.float32)  # (K, D)
    # L2 normalize prototypes
    centers /= (np.linalg.norm(centers, axis=1, keepdims=True) + 1e-12)
    return centers


# -----------------------------
# Main
# -----------------------------
def parse_args():
    ap = argparse.ArgumentParser("Build STPB prototypes (source + target train) for bay->la")
    ap.add_argument("--root_dir", type=str, default="/home/zc/wanganna")
    ap.add_argument("--source_name", type=str, default="PEMS-BAY")
    ap.add_argument("--target_name", type=str, default="METR-LA")

    ap.add_argument("--source_h5", type=str, default="pems-bay.h5")
    ap.add_argument("--target_h5", type=str, default="metr-la.h5")

    ap.add_argument("--input_len", type=int, default=12)
    ap.add_argument("--output_len", type=int, default=12)

    ap.add_argument("--train_ratio", type=float, default=0.7)

    ap.add_argument("--hidden_dim", type=int, default=64)
    ap.add_argument("--embed_dim", type=int, default=128)

    ap.add_argument("--mask_ratio", type=float, default=0.2)
    ap.add_argument("--train_steps", type=int, default=2000)
    ap.add_argument("--batch_size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight_decay", type=float, default=1e-4)

    ap.add_argument("--windows_per_domain", type=int, default=60000, help="Number of windows to embed per domain for KMeans (balanced).")
    ap.add_argument("--collect_batch_size", type=int, default=64)

    ap.add_argument("--K", type=int, default=16)
    ap.add_argument("--seed", type=int, default=42)

    ap.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")

    ap.add_argument("--out_dir", type=str, default="./STPB_bay2la")
    return ap.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)

    os.makedirs(args.out_dir, exist_ok=True)
    log_path = os.path.join(args.out_dir, "stpb_training_log.txt")

    def log(msg: str):
        print(msg)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    # Paths
    src_dir = os.path.join(args.root_dir, args.source_name)
    tgt_dir = os.path.join(args.root_dir, args.target_name)
    src_h5_path = os.path.join(src_dir, args.source_h5)
    tgt_h5_path = os.path.join(tgt_dir, args.target_h5)

    log(f"[INFO] Source h5: {src_h5_path}")
    log(f"[INFO] Target h5: {tgt_h5_path}")

    # Load data
    src_data = _read_h5_as_numpy(src_h5_path)  # (T, N, 1)
    tgt_data = _read_h5_as_numpy(tgt_h5_path)  # (T, N, 1)

    T_src, N_src, _ = src_data.shape
    T_tgt, N_tgt, _ = tgt_data.shape
    log(f"[DATA] Source shape: T={T_src}, N={N_src}, C=1")
    log(f"[DATA] Target shape: T={T_tgt}, N={N_tgt}, C=1")

    # Compute train boundary b1 per domain
    b1_src = compute_split_b1(T_src, args.train_ratio)
    b1_tgt = compute_split_b1(T_tgt, args.train_ratio)
    log(f"[SPLIT] b1_src=floor({args.train_ratio}*{T_src})={b1_src}")
    log(f"[SPLIT] b1_tgt=floor({args.train_ratio}*{T_tgt})={b1_tgt}")

    # Eligible window starts using label_end rule
    starts_src = valid_starts(T_src, args.input_len, args.output_len, b1_src)
    starts_tgt = valid_starts(T_tgt, args.input_len, args.output_len, b1_tgt)
    log(f"[SPLIT] Eligible starts source(train): {len(starts_src)}")
    log(f"[SPLIT] Eligible starts target(train): {len(starts_tgt)}")
    if len(starts_src) == 0 or len(starts_tgt) == 0:
        raise RuntimeError("No eligible windows found. Check input_len/output_len or dataset length.")

    # Fit per-domain scaler on train segment only
    mean_src, std_src = fit_train_scaler(src_data, b1_src)
    mean_tgt, std_tgt = fit_train_scaler(tgt_data, b1_tgt)
    log("[SCALER] Fitted mean/std on each domain's train segment only.")

    # Build encoder
    device = torch.device(args.device)
    encoder = NodeTemporalEncoder(
        input_len=args.input_len,
        hidden_dim=args.hidden_dim,
        embed_dim=args.embed_dim,
    ).to(device)

    opt = torch.optim.AdamW(encoder.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    # Create batchers for balanced training (each step uses half from source + half from target)
    bs_half = max(1, args.batch_size // 2)
    src_batcher = RandomWindowBatcher(
        data=src_data, starts=starts_src, mean=mean_src, std=std_src,
        input_len=args.input_len, batch_size=bs_half, device=device
    )
    tgt_batcher = RandomWindowBatcher(
        data=tgt_data, starts=starts_tgt, mean=mean_tgt, std=std_tgt,
        input_len=args.input_len, batch_size=args.batch_size - bs_half, device=device
    )

    log(f"[TRAIN] device={device}, steps={args.train_steps}, batch_size={args.batch_size} (src={bs_half}, tgt={args.batch_size - bs_half})")
    log(f"[TRAIN] mask_ratio={args.mask_ratio}, lr={args.lr}, wd={args.weight_decay}")

    # Training loop (masked reconstruction)
    encoder.train()
    t0 = time.time()
    for step in range(1, args.train_steps + 1):
        x_src = src_batcher.sample_batch()  # (Bs, Ns, T, 1)
        x_tgt = tgt_batcher.sample_batch()  # (Bt, Nt, T, 1)

        # We train using two domains separately to avoid forcing same N
        loss_total = 0.0

        for x in [x_src, x_tgt]:
            # mask positions
            mask = (torch.rand_like(x) < args.mask_ratio).float()
            x_masked = x * (1.0 - mask)

            node_emb, _ = encoder(x_masked)
            x_hat = encoder.reconstruct(node_emb)

            loss = masked_recon_loss(x, x_hat, mask)
            loss_total = loss_total + loss

        opt.zero_grad()
        loss_total.backward()
        nn.utils.clip_grad_norm_(encoder.parameters(), max_norm=5.0)
        opt.step()

        if step % 100 == 0 or step == 1:
            elapsed = time.time() - t0
            log(f"[TRAIN] step={step:5d}/{args.train_steps}, loss={loss_total.item():.6f}, elapsed={elapsed:.1f}s")

    # Collect embeddings (balanced)
    log("[EMB] Collecting embeddings for KMeans (balanced source/target)...")
    emb_src = collect_embeddings(
        encoder=encoder,
        data=src_data, starts=starts_src, mean=mean_src, std=std_src,
        input_len=args.input_len,
        device=device,
        num_windows=args.windows_per_domain,
        batch_size=args.collect_batch_size
    )
    emb_tgt = collect_embeddings(
        encoder=encoder,
        data=tgt_data, starts=starts_tgt, mean=mean_tgt, std=std_tgt,
        input_len=args.input_len,
        device=device,
        num_windows=args.windows_per_domain,
        batch_size=args.collect_batch_size
    )
    emb_all = np.concatenate([emb_src, emb_tgt], axis=0)
    log(f"[EMB] emb_src={emb_src.shape}, emb_tgt={emb_tgt.shape}, emb_all={emb_all.shape}")

    # KMeans prototypes
    log(f"[KMEANS] Running KMeans: K={args.K} ...")
    prototypes = run_kmeans(emb_all, K=args.K, seed=args.seed)
    log(f"[KMEANS] prototypes shape: {prototypes.shape}")

    # Save outputs
    proto_path = os.path.join(args.out_dir, "stpb_prototypes.npy")
    np.save(proto_path, prototypes)

    meta = {
        "task": "PEMS-BAY->METR-LA",
        "root_dir": args.root_dir,
        "source_name": args.source_name,
        "target_name": args.target_name,
        "source_h5": src_h5_path,
        "target_h5": tgt_h5_path,
        "T_src": int(T_src),
        "N_src": int(N_src),
        "T_tgt": int(T_tgt),
        "N_tgt": int(N_tgt),
        "train_ratio": float(args.train_ratio),
        "b1_src": int(b1_src),
        "b1_tgt": int(b1_tgt),
        "input_len": int(args.input_len),
        "output_len": int(args.output_len),
        "split_rule": "train windows satisfy label_end = s+input_len+output_len <= b1",
        "encoder": {
            "type": "NodeTemporalEncoder(Conv1D per-node + mean-pool nodes)",
            "hidden_dim": int(args.hidden_dim),
            "embed_dim": int(args.embed_dim),
            "mask_ratio": float(args.mask_ratio),
            "train_steps": int(args.train_steps),
            "batch_size": int(args.batch_size),
            "lr": float(args.lr),
            "weight_decay": float(args.weight_decay),
        },
        "kmeans": {
            "K": int(args.K),
            "windows_per_domain": int(args.windows_per_domain),
            "balanced": True,
            "seed": int(args.seed),
        },
        "outputs": {
            "prototypes_npy": proto_path
        }
    }
    meta_path = os.path.join(args.out_dir, "stpb_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    log(f"[DONE] Saved prototypes to: {proto_path}")
    log(f"[DONE] Saved metadata to:   {meta_path}")
    log("[DONE] You can now load stpb_prototypes.npy in your interpretability evaluation.")


if __name__ == "__main__":
    main()
