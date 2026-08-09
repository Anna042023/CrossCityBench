import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch
from torch.utils.data import DataLoader

from stgcn_ft.data import OneStepWindowDataset, MultiStepWindowDataset, StandardScaler
from stgcn_ft.graph import build_cheb_tensor
from stgcn_ft.model import STGCN, STGCNConfig
from stgcn_ft.transfer import transfer_shape_compatible_parameters


def make_graph(n):
    W = np.zeros((n, n), dtype=np.float32)
    for i in range(n - 1):
        W[i, i + 1] = W[i + 1, i] = 1.0
    return W


def make_series(T, N, phase=0.0):
    t = np.arange(T, dtype=np.float32)[:, None]
    node = np.arange(N, dtype=np.float32)[None, :]
    x = 10 + 2 * np.sin(t / 8 + phase + node / 9) + 0.2 * np.cos(t / 3 + node / 5)
    return x.astype(np.float32)


def one_train_step(model, series, device):
    ds = OneStepWindowDataset(series, 12, stride=4)
    dl = DataLoader(ds, batch_size=8, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    x, y = next(iter(dl))
    x, y = x.to(device), y.to(device)
    opt.zero_grad()
    loss = ((model(x) - y) ** 2).mean()
    loss.backward()
    opt.step()
    return float(loss.item())


def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    Ns, Nt = 11, 7
    src = make_series(120, Ns, 0.0)
    tgt = make_series(120, Nt, 0.5)
    src = (src - src.mean()) / src.std()
    tgt = (tgt - tgt.mean()) / tgt.std()

    cfg = STGCNConfig(n_his=12, ks=3, kt=3, dropout=0.0)
    ms = STGCN(Ns, build_cheb_tensor(make_graph(Ns), 3, device), cfg).to(device)
    mt = STGCN(Nt, build_cheb_tensor(make_graph(Nt), 3, device), cfg).to(device)

    l1 = one_train_step(ms, src, device)
    copied, skipped = transfer_shape_compatible_parameters(ms, mt)
    assert copied, "No parameters were transferred"
    assert skipped, "Different node counts should produce some skipped node-specific parameters"
    l2 = one_train_step(mt, tgt, device)

    hist = torch.from_numpy(tgt[:2*12].reshape(2, 12, Nt)).to(device)
    with torch.no_grad():
        pred = mt.autoregressive_forecast(hist, 12)
    assert pred.shape == (2, 12, Nt), pred.shape
    assert torch.isfinite(pred).all()

    print("Smoke test OK")
    print(f"source one-step loss: {l1:.6f}")
    print(f"target one-step loss: {l2:.6f}")
    print(f"transferred tensors: {len(copied)}")
    print(f"reinitialized tensors: {len(skipped)}")
    print(f"forecast shape: {tuple(pred.shape)}")


if __name__ == "__main__":
    main()
