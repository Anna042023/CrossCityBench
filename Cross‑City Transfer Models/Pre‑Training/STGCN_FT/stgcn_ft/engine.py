from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

from .metrics import horizon_report


@dataclass
class TrainConfig:
    epochs: int = 100
    patience: int = 10
    lr: float = 1e-3
    weight_decay: float = 0.0
    optimizer: str = "adamw"
    lr_decay_every: int = 5
    lr_decay_rate: float = 0.7
    grad_clip: float = 5.0


def make_optimizer(model: nn.Module, cfg: TrainConfig):
    name = cfg.optimizer.lower()
    if name == "adamw":
        return torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    if name == "adam":
        return torch.optim.Adam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    if name == "rmsprop":
        return torch.optim.RMSprop(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    raise ValueError(f"Unknown optimizer: {cfg.optimizer}")


def train_one_step_epoch(model, loader, optimizer, device, grad_clip=5.0):
    model.train()
    losses = []
    for x, y in loader:
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        pred = model(x)
        loss = torch.mean((pred - y) ** 2)
        loss.backward()
        if grad_clip and grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()
        losses.append(loss.detach().item())
    return float(np.mean(losses)) if losses else float("nan")


@torch.no_grad()
def eval_one_step_mse(model, loader, device):
    model.eval()
    losses = []
    for x, y in loader:
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)
        pred = model(x)
        losses.append(torch.mean((pred - y) ** 2).item())
    return float(np.mean(losses)) if losses else float("inf")


@torch.no_grad()
def predict_multistep(model, loader, device, scaler):
    model.eval()
    ys, ps = [], []
    for x, y in loader:
        x = x.to(device, non_blocking=True)
        pred = model.autoregressive_forecast(x, y.shape[1])
        ys.append(y.numpy())
        ps.append(pred.cpu().numpy())
    y = np.concatenate(ys, axis=0)
    p = np.concatenate(ps, axis=0)
    return scaler.inverse_transform(y), scaler.inverse_transform(p)


@torch.no_grad()
def eval_multistep_mae(model, loader, device, scaler):
    y, p = predict_multistep(model, loader, device, scaler)
    return float(np.mean(np.abs(y - p)))


def fit_model(
    model,
    train_loader,
    val_loader,
    device,
    cfg: TrainConfig,
    checkpoint_path: str | Path,
    val_mode: str = "one_step",
    scaler=None,
    verbose_prefix: str = "",
):
    checkpoint_path = Path(checkpoint_path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    optimizer = make_optimizer(model, cfg)
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=max(1, cfg.lr_decay_every),
        gamma=cfg.lr_decay_rate,
    )

    best = float("inf")
    best_epoch = -1
    wait = 0
    history = []

    for epoch in range(1, cfg.epochs + 1):
        t0 = time.time()
        tr = train_one_step_epoch(model, train_loader, optimizer, device, cfg.grad_clip)
        if val_mode == "one_step":
            va = eval_one_step_mse(model, val_loader, device)
            val_name = "val_mse"
        elif val_mode == "multistep_mae":
            if scaler is None:
                raise ValueError("scaler required for multistep validation")
            va = eval_multistep_mae(model, val_loader, device, scaler)
            val_name = "val_avg_mae"
        else:
            raise ValueError(val_mode)

        lr = optimizer.param_groups[0]["lr"]
        elapsed = time.time() - t0
        row = {"epoch": epoch, "train_mse": tr, val_name: va, "lr": lr, "seconds": elapsed}
        history.append(row)
        print(
            f"{verbose_prefix}Epoch {epoch:03d} | train_mse={tr:.6f} | "
            f"{val_name}={va:.6f} | lr={lr:.3e} | {elapsed:.1f}s"
        )

        if va < best - 1e-10:
            best = va
            best_epoch = epoch
            wait = 0
            torch.save({"model": model.state_dict(), "epoch": epoch, "val": va}, checkpoint_path)
        else:
            wait += 1
            if wait >= cfg.patience:
                print(f"{verbose_prefix}Early stop at epoch {epoch}; best epoch={best_epoch}, best={best:.6f}")
                break
        scheduler.step()

    ckpt = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(ckpt["model"])
    return history, best_epoch, best


def evaluate_and_report(model, loader, device, scaler, horizon_steps=(3, 6, 12), mape_threshold=1e-5, mape_mode="mask"):
    y, p = predict_multistep(model, loader, device, scaler)
    report = horizon_report(y, p, horizon_steps, mape_threshold, mape_mode)
    return report, y, p
