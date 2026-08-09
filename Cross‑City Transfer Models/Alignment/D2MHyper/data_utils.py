import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader


# ---------------------------
# Z-score scaler (for 4D arrays: (T,N,1) or (B,out,N,1))
# ---------------------------
class ZScoreScaler:
    """Z-score scaler supporting both global-scalar and per-node scaling.

    In most traffic forecasting codebases, normalization is done **per node** to
    avoid mixing statistics across sensors with very different ranges.

    Shapes supported:
      - X: (T, N, 1)
      - windows: (B, in/out, N, 1)
    """

    def __init__(self, mean, std):
        # mean/std can be scalars or broadcastable arrays, typically (1,N,1)
        self.mean = mean
        self.std = std

    @staticmethod
    def fit(X, per_node: bool = True):
        """Fit scaler on training split.

        Args:
            X: np.ndarray, shape (T,N,1) or (T,N)
            per_node: if True, compute mean/std over time for each node.
                      if False, compute global scalar mean/std.
        """
        if X.ndim == 2:
            X_ = X[..., None]
        else:
            X_ = X

        if per_node:
            mean = X_.mean(axis=0, keepdims=True)           # (1,N,1)
            std = X_.std(axis=0, keepdims=True)            # (1,N,1)
        else:
            mean = float(X_.mean())
            std = float(X_.std())

        std = np.maximum(std, 1e-6)
        return ZScoreScaler(mean, std)

    def transform(self, X):
        return (X - self.mean) / self.std

    def inverse_transform(self, X):
        return X * self.std + self.mean


# ---------------------------
# Data loading
# ---------------------------
def load_city_data(city_name, city_dir):
    """
    Return X: (T,N,1) float32
    - npz: try key 'data', else first array
           if shape is (T,N,C) and C!=1, will keep channel 0 to make (T,N,1)
    - h5: use pandas.read_hdf -> DataFrame (T,N)
    """
    for fn in os.listdir(city_dir):
        if fn.endswith(".npz"):
            path = os.path.join(city_dir, fn)
            npz = np.load(path, allow_pickle=True)
            if "data" in npz.files:
                arr = npz["data"]
            else:
                arr = npz[npz.files[0]]

            if arr.ndim == 2:
                arr = arr[..., None]
            elif arr.ndim == 3:
                if arr.shape[-1] != 1:
                    arr = arr[..., :1]
            else:
                raise ValueError(f"[Data] Unexpected npz array ndim={arr.ndim} at {path}, shape={arr.shape}")

            return arr.astype(np.float32)

    for fn in os.listdir(city_dir):
        if fn.endswith(".h5"):
            path = os.path.join(city_dir, fn)
            df = pd.read_hdf(path)
            arr = df.values.astype(np.float32)  # (T,N)
            arr = arr[..., None]                # (T,N,1)
            return arr

    raise FileNotFoundError(f"Cannot find .npz or .h5 in {city_dir}")


# ---------------------------
# Adjacency loading helpers
# ---------------------------
def read_edge_list_csv(path):
    """
    Supports:
    - header: from,to,distance
    - header: from,to,cost
    - whitespace/tab separated variants
    - no header (take first 3 columns)
    Returns DataFrame with columns: ['from','to','dist'].
    """
    df = pd.read_csv(path, sep=None, engine="python")
    df.columns = [str(c).strip().lower() for c in df.columns]

    def pick(keys):
        for k in keys:
            if k in df.columns:
                return k
        for c in df.columns:
            for k in keys:
                if k in c:
                    return c
        return None

    c_from = pick(["from", "src", "source", "u", "i"])
    c_to = pick(["to", "dst", "target", "v", "j"])
    c_dist = pick(["distance", "dist", "cost", "weight", "w", "len", "length"])

    if c_from is None or c_to is None or c_dist is None:
        df2 = pd.read_csv(path, sep=None, engine="python", header=None)
        if df2.shape[1] < 3:
            raise ValueError(f"[EdgeCSV] Cannot parse edge list (need >=3 cols), got shape={df2.shape}, path={path}")
        df2 = df2.iloc[:, :3].copy()
        df2.columns = ["from", "to", "dist"]
        return df2

    out = df[[c_from, c_to, c_dist]].copy()
    out.columns = ["from", "to", "dist"]
    return out


def _build_adj_from_edge_list(
    edge_df,
    num_nodes,
    epsilon_percentile=0.10,
    epsilon_value=None,
    force_sensor_id_mapping=False
):
    """
    Build binary adjacency A (N,N) from edge-list.
    - PEMS08 distance.csv uses 0..N-1 indices => NO mapping required
    - PEMS03 PEMS03.csv uses real sensor IDs => must map to 0..N-1
    """
    edge_df = edge_df.copy()
    edge_df.columns = [str(c).strip().lower() for c in edge_df.columns]

    if "from" not in edge_df.columns or "to" not in edge_df.columns:
        edge_df.rename(columns={edge_df.columns[0]: "from", edge_df.columns[1]: "to"}, inplace=True)
    if "dist" not in edge_df.columns:
        for cand in ["distance", "cost", "weight", "len", "length"]:
            if cand in edge_df.columns:
                edge_df.rename(columns={cand: "dist"}, inplace=True)
                break
    if "dist" not in edge_df.columns:
        edge_df.rename(columns={edge_df.columns[2]: "dist"}, inplace=True)

    frm_raw = edge_df["from"].to_numpy()
    to_raw = edge_df["to"].to_numpy()
    dist = edge_df["dist"].to_numpy().astype(np.float32)

    if epsilon_value is None:
        eps = float(np.quantile(dist, epsilon_percentile))
    else:
        eps = float(epsilon_value)

    mask = dist < eps
    frm_raw = frm_raw[mask]
    to_raw = to_raw[mask]

    need_map = bool(force_sensor_id_mapping)
    if not need_map:
        try:
            max_id = int(max(np.max(frm_raw), np.max(to_raw)))
            if max_id >= num_nodes:
                need_map = True
        except Exception:
            need_map = True

    if need_map:
        uniq = np.unique(np.concatenate([frm_raw, to_raw]))
        uniq_sorted = np.sort(uniq)

        if len(uniq_sorted) != num_nodes:
            print(
                f"[AdjWarn] unique node ids in edge list = {len(uniq_sorted)} != num_nodes(data)={num_nodes}. "
                f"Will align by taking first {num_nodes} sorted ids and dropping others."
            )

        keep = uniq_sorted[:num_nodes]
        keep_ids = set(keep.tolist())
        id_map = {sid: i for i, sid in enumerate(keep)}

        frm = []
        to = []
        for a, b in zip(frm_raw, to_raw):
            if a in keep_ids and b in keep_ids:
                frm.append(id_map[a])
                to.append(id_map[b])
        frm = np.asarray(frm, dtype=np.int64)
        to = np.asarray(to, dtype=np.int64)
    else:
        frm = frm_raw.astype(np.int64)
        to = to_raw.astype(np.int64)
        valid = (frm >= 0) & (frm < num_nodes) & (to >= 0) & (to < num_nodes)
        frm = frm[valid]
        to = to[valid]

    A = np.zeros((num_nodes, num_nodes), dtype=np.float32)
    A[frm, to] = 1.0
    A[to, frm] = 1.0

    print(
        f"[Adj] edge-list -> binary adj by epsilon={eps:.6f} "
        f"(percentile={epsilon_percentile}, override={epsilon_value is not None}), "
        f"mapped={need_map}, shape={A.shape}"
    )
    return A.astype(np.float32)


def _extract_adj_from_pkl(obj):
    """
    Robustly extract NxN adjacency from common traffic PKL formats.
    Supports:
    - (sensor_ids, sensor_id_to_ind, adj_mx)  as tuple OR list
    - dict with keys: adj_mx / adj / A / matrix / adjacency
    - directly stored numpy array or scipy sparse
    """
    # tuple/list: try to find a 2D square matrix inside
    if isinstance(obj, (tuple, list)):
        # common case length==3: (ids, map, adj)
        if len(obj) >= 3:
            cand = obj[2]
            adj = _extract_adj_from_pkl(cand)
            if adj is not None:
                return adj
        # otherwise scan all
        for it in obj:
            adj = _extract_adj_from_pkl(it)
            if adj is not None:
                return adj
        return None

    # dict
    if isinstance(obj, dict):
        for k in ["adj_mx", "adj", "A", "matrix", "adjacency"]:
            if k in obj:
                adj = _extract_adj_from_pkl(obj[k])
                if adj is not None:
                    return adj
        # sometimes dict itself is sparse/ndarray-like but stored as value
        return None

    # sparse
    try:
        import scipy.sparse as sp
        if sp.issparse(obj):
            return obj.toarray()
    except Exception:
        pass

    # ndarray
    if isinstance(obj, np.ndarray):
        if obj.ndim == 2 and obj.shape[0] == obj.shape[1]:
            return obj
        return None

    # torch tensor
    if isinstance(obj, torch.Tensor):
        arr = obj.detach().cpu().numpy()
        if arr.ndim == 2 and arr.shape[0] == arr.shape[1]:
            return arr
        return None

    return None


def load_adjacency_for_city(city_name, city_dir, epsilon_percentile=0.10, epsilon_value=None):
    """
    - PEMS03 / PEMS08: use CSV edge-list
    - PEMS-BAY / METR-LA: use PKL adjacency
    """
    city_upper = city_name.upper()

    prefer_csv = (city_upper in ["PEMS03", "PEMS08"])
    prefer_pkl = (city_upper in ["PEMS-BAY", "METR-LA", "PEMS_BAY", "METR_LA"])

    pkl_candidates = [os.path.join(city_dir, fn) for fn in os.listdir(city_dir) if fn.endswith(".pkl")]
    csv_candidates = [os.path.join(city_dir, fn) for fn in os.listdir(city_dir) if fn.endswith(".csv")]

    # ---- CSV (forced for PEMS03/08) ----
    if prefer_csv:
        if len(csv_candidates) == 0:
            raise FileNotFoundError(f"[Adj] {city_name} requires CSV edge-list, but no .csv found in {city_dir}")

        if city_upper == "PEMS03":
            preferred = ["PEMS03.csv", "PEMS03_data.csv", "pems03.csv", "pems03_data.csv"]
        else:
            preferred = ["distance.csv", "Distance.csv", "DISTANCE.csv"]

        path = None
        name2path = {os.path.basename(p): p for p in csv_candidates}
        name2path_lower = {os.path.basename(p).lower(): p for p in csv_candidates}

        for fn in preferred:
            if fn in name2path:
                path = name2path[fn]; break
            if fn.lower() in name2path_lower:
                path = name2path_lower[fn.lower()]; break

        if path is None:
            csv_candidates_sorted = sorted(
                csv_candidates,
                key=lambda p: (("dist" not in os.path.basename(p).lower()) and ("distance" not in os.path.basename(p).lower()))
            )
            path = csv_candidates_sorted[0]

        X = load_city_data(city_name, city_dir)
        N = int(X.shape[1])
        df = read_edge_list_csv(path)

        force_map = (city_upper == "PEMS03")

        A = _build_adj_from_edge_list(
            df, num_nodes=N,
            epsilon_percentile=epsilon_percentile,
            epsilon_value=epsilon_value,
            force_sensor_id_mapping=force_map
        )
        print(f"[Adj] {city_name}: edge-list CSV loaded from {os.path.basename(path)}")
        return A.astype(np.float32)

    # ---- PKL (preferred for BAY / LA) ----
    if prefer_pkl and len(pkl_candidates) > 0:
        import pickle

        def pkl_rank(p):
            bn = os.path.basename(p).lower()
            # prefer adjacency-like name
            return 0 if ("adj" in bn or "mx" in bn) else 1

        pkl_candidates = sorted(pkl_candidates, key=pkl_rank)
        path = pkl_candidates[0]

        with open(path, "rb") as f:
            obj = pickle.load(f, encoding="latin1")

        adj = _extract_adj_from_pkl(obj)
        if adj is None:
            raise ValueError(f"[Adj] Cannot extract NxN adjacency from {path}. Loaded type={type(obj)}")

        adj = np.asarray(adj, dtype=np.float32)
        if adj.ndim != 2 or adj.shape[0] != adj.shape[1]:
            raise ValueError(f"[Adj] adjacency from {path} is not NxN matrix, got shape={adj.shape}")

        adj = np.maximum(adj, adj.T)
        print(f"[Adj] {city_name}: loaded from PKL {os.path.basename(path)} with shape={adj.shape}")
        return adj.astype(np.float32)

    raise FileNotFoundError(f"[Adj] Cannot find proper adjacency for {city_name} in {city_dir}")


# ---------------------------
# window dataset
# ---------------------------
class WindowDataset(Dataset):
    def __init__(self, X, in_len=12, out_len=12):
        self.X = X
        self.in_len = in_len
        self.out_len = out_len
        self.T = X.shape[0]
        self.indices = []
        max_start = self.T - (in_len + out_len) + 1
        for s in range(max_start):
            self.indices.append(s)

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        s = self.indices[idx]
        x = self.X[s:s + self.in_len]
        y = self.X[s + self.in_len:s + self.in_len + self.out_len]
        return torch.from_numpy(x).float(), torch.from_numpy(y).float()


def make_dataloaders(Xs_tr, Xs_va, Xs_te, Xt_tr, Xt_va, Xt_te, in_len, out_len, batch_size):
    train_s = DataLoader(WindowDataset(Xs_tr, in_len, out_len), batch_size=batch_size, shuffle=True, drop_last=True)
    val_s   = DataLoader(WindowDataset(Xs_va, in_len, out_len), batch_size=batch_size, shuffle=False, drop_last=False)
    test_s  = DataLoader(WindowDataset(Xs_te, in_len, out_len), batch_size=batch_size, shuffle=False, drop_last=False)

    train_t = DataLoader(WindowDataset(Xt_tr, in_len, out_len), batch_size=batch_size, shuffle=True, drop_last=True)
    val_t   = DataLoader(WindowDataset(Xt_va, in_len, out_len), batch_size=batch_size, shuffle=False, drop_last=False)
    test_t  = DataLoader(WindowDataset(Xt_te, in_len, out_len), batch_size=batch_size, shuffle=False, drop_last=False)
    return train_s, val_s, test_s, train_t, val_t, test_t


def build_splits_with_target_7days(Xs, Xt, in_len, out_len, points_per_day=288, target_train_days=7):
    def split_712(X):
        T = X.shape[0]
        n_tr = int(T * 0.7)
        n_va = int(T * 0.1)
        X_tr = X[:n_tr]
        X_va = X[n_tr:n_tr + n_va]
        X_te = X[n_tr + n_va:]
        return X_tr, X_va, X_te

    Xs_tr, Xs_va, Xs_te = split_712(Xs)
    Xt_tr_full, Xt_va, Xt_te = split_712(Xt)

    max_points = target_train_days * points_per_day
    Xt_tr = Xt_tr_full[:max_points]

    min_len = in_len + out_len + 1
    if Xt_tr.shape[0] < min_len:
        raise ValueError(f"Target 7-day train too short for windows: got {Xt_tr.shape[0]}, need >= {min_len}")

    return Xs_tr, Xs_va, Xs_te, Xt_tr, Xt_va, Xt_te
