# data_loader.py
import os
import numpy as np
import torch
import h5py
import pandas as pd
from torch.utils.data import Dataset, DataLoader

class TrafficDataset(Dataset):
    def __init__(self, data_path, input_len=12, output_len=12, normalize=True):
        if data_path.endswith('.npz'):
            data = np.load(data_path)['data']  # [T, N, D]
        elif 'pems-bay' in data_path:
            with h5py.File(data_path, 'r') as f:
                data = f['speed/block0_values'][:]  # [T, N]
        elif 'metr-la' in data_path:
            df = pd.read_hdf(data_path, key='df')
            data = df.values.astype(np.float32)  # [T, N]
        else:
            raise ValueError(f"Unsupported dataset: {data_path}")

        # Ensure float32 and correct shape
        data = np.asarray(data, dtype=np.float32)
        if data.ndim == 2:
            data = data[..., np.newaxis]  # [T, N] -> [T, N, 1]
        elif data.ndim != 3:
            raise ValueError(f"Unexpected data shape: {data.shape}")

        self.original_data = data.copy()
        self.mean_val = np.mean(data, axis=0, keepdims=True)  # [1, N, D]
        self.std_val = np.std(data, axis=0, keepdims=True)   # [1, N, D]
        self.std_val = np.where(self.std_val < 1e-6, 1.0, self.std_val)

        if normalize:
            data = (data - self.mean_val) / self.std_val

        self.data = torch.tensor(data, dtype=torch.float32)
        self.input_len = input_len
        self.output_len = output_len
        self.T = self.data.shape[0]
        self.N = self.data.shape[1]
        self.D = self.data.shape[2]

    def __len__(self):
        return max(0, self.T - self.input_len - self.output_len + 1)

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.input_len]  # [L_in, N, D]
        y = self.data[idx + self.input_len:idx + self.input_len + self.output_len]  # [L_out, N, D]
        return x, y

    def get_original_stats(self):
        return self.mean_val, self.std_val


def get_dataloaders(source_name, target_name, data_root="/home/zc/wanganna/", input_len=12, batch_size=32):
    name_to_path = {
        'pems03': '/home/zc/wanganna/PEMS03/PEMS03.npz',
        'pems08': '/home/zc/wanganna/PEMS08/pems08.npz',
        'pems-bay': '/home/zc/wanganna/PEMS-BAY/pems-bay.h5',
        'metr-la': '/home/zc/wanganna/METR-LA/metr-la.h5'
    }

    src_path = name_to_path[source_name]
    tgt_path = name_to_path[target_name]

    # Load source data
    if src_path.endswith('.npz'):
        data_src = np.load(src_path)['data']
    elif 'pems-bay' in src_path:
        with h5py.File(src_path, 'r') as f:
            data_src = f['speed/block0_values'][:]
    elif 'metr-la' in src_path:
        df = pd.read_hdf(src_path, key='df')
        data_src = df.values.astype(np.float32)
    else:
        raise ValueError("Unsupported source dataset")

    data_src = np.asarray(data_src, dtype=np.float32)
    if data_src.ndim == 2:
        data_src = data_src[..., np.newaxis]
    print(f"Source data shape: {data_src.shape}")
    src_dim = data_src.shape[2]
    src_nodes = data_src.shape[1]

    # Load target data
    if tgt_path.endswith('.npz'):
        data_tgt = np.load(tgt_path)['data']
    elif 'pems-bay' in tgt_path:
        with h5py.File(tgt_path, 'r') as f:
            data_tgt = f['speed/block0_values'][:]
    elif 'metr-la' in tgt_path:
        df = pd.read_hdf(tgt_path, key='df')
        data_tgt = df.values.astype(np.float32)
    else:
        raise ValueError("Unsupported target dataset")

    data_tgt = np.asarray(data_tgt, dtype=np.float32)
    if data_tgt.ndim == 2:
        data_tgt = data_tgt[..., np.newaxis]
    print(f"Target data shape: {data_tgt.shape}")
    tgt_dim = data_tgt.shape[2]
    tgt_nodes = data_tgt.shape[1]

    # Create datasets
    src_dataset = TrafficDataset(src_path, input_len=input_len, output_len=12, normalize=True)
    tgt_dataset = TrafficDataset(tgt_path, input_len=input_len, output_len=12, normalize=True)

    src_loader = DataLoader(src_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    tgt_loader = DataLoader(tgt_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    test_loader = DataLoader(tgt_dataset, batch_size=batch_size, shuffle=False)

    print(f"Source Input Dim: {src_dim}, Target Input Dim: {tgt_dim}, Source Nodes: {src_nodes}, Target Nodes: {tgt_nodes}")
    return src_loader, tgt_loader, test_loader, src_nodes, tgt_nodes, src_dim, tgt_dim