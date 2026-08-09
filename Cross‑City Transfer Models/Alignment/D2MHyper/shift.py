
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shift.py for D2MHyper (Scheme A)

Goal:
  Compute robustness metric under cross-city shifts:

      ΔM_shift = (MAE_hetero - MAE_homo) / MAE_homo * 100%

  where MAE is evaluated at horizon=average ("avg" over all out_len steps).

Scheme A (same as your previous methods):
  - HETERO:  PEMS03 -> PEMS08   (cross-city / heterogeneous)
  - HOMO(A): PEMS03 -> PEMS03   (within-city temporal split)
            source-domain = first homo_src_ratio of time
            target-domain = remaining time

Constraints:
  - Do NOT modify existing files.
  - This script reuses your existing modules:
      data_utils.py / model_d2mhyper.py / metrics.py / profiler_utils.py / utils.py

How it works:
  - For each scenario, we run the same training procedure as train_one_task.py:
      * build_splits_with_target_7days()  (target train limited to 7 days)
      * per-node ZScoreScaler for source/target
      * D2MHyper training with adversarial warmup
      * evaluate on target test set, take MAE_avg
  - Then compute ΔM_shift.

Run examples:
  # Use physical GPU2 (recommended if GPU0 is full)
  CUDA_VISIBLE_DEVICES=2 python shift.py --data_root /home/zc/wanganna --gpu 0

  # Or, without CUDA_VISIBLE_DEVICES, choose GPU index directly:
  python shift.py --data_root /home/zc/wanganna --gpu 2

Outputs:
  - Prints MAE_homo_avg / MAE_hetero_avg / ΔM_shift
  - Appends one row to --out_csv (default: outputs/d2mhyper_shift.csv)
"""

import os
import time
import csv
import argparse
from typing import Optional
import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW

from data_utils import (
    load_city_data, load_adjacency_for_city,
    build_splits_with_target_7days, make_dataloaders,
    ZScoreScaler
)
from model_d2mhyper import D2MHyper
from metrics import compute_metrics_horizons
from utils import set_seed, ensure_dir, count_trainable_params


# -------------------------
# Helpers
# -------------------------
def append_to_csv(path, row_dict):
    ensure_dir(os.path.dirname(path) if os.path.dirname(path) else ".")
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row_dict.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row_dict)


def train_one_epoch(model, loader_s, loader_t, optimizer, device, lambda_adv, adv_alpha=1.0):
    model.train()
    mse = nn.MSELoss()

    it_s = iter(loader_s)
    it_t = iter(loader_t)
    steps = max(len(loader_s), len(loader_t))

    loss_sum = 0.0
    for _ in range(steps):
        try:
            xs, ys = next(it_s)
        except StopIteration:
            it_s = iter(loader_s)
            xs, ys = next(it_s)

        try:
            xt, yt = next(it_t)
        except StopIteration:
            it_t = iter(loader_t)
            xt, yt = next(it_t)

        xs, ys = xs.to(device), ys.to(device)
        xt, yt = xt.to(device), yt.to(device)

        optimizer.zero_grad(set_to_none=True)
        ysp, ytp, adv_loss = model(xs, xt)

        loss_s = mse(ysp, ys)
        loss_t = mse(ytp, yt)
        loss = loss_s + loss_t + (lambda_adv * float(adv_alpha)) * adv_loss

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        optimizer.step()

        loss_sum += loss.item()

    return float(loss_sum / max(steps, 1))


@torch.no_grad()
def eval_target_mae_avg(model, loader_t, device, scaler_t, out_len=12, mape_min_denom=5.0):
    """
    Returns:
      mae_avg (float), metrics dict
    """
    model.eval()
    preds = []
    trues = []
    for xt, yt in loader_t:
        xt = xt.to(device)
        yt = yt.to(device)
        _, ytp, _ = model(None, xt, only_target=True)
        preds.append(ytp.detach().cpu().numpy())
        trues.append(yt.detach().cpu().numpy())

    pred = np.concatenate(preds, axis=0)
    true = np.concatenate(trues, axis=0)

    pred_inv = scaler_t.inverse_transform(pred)
    true_inv = scaler_t.inverse_transform(true)

    metrics = compute_metrics_horizons(pred_inv, true_inv, out_len=out_len, mape_min_denom=mape_min_denom)
    return float(metrics["avg"]["MAE"]), metrics


def run_task_get_mae_avg(
    *,
    data_root: str,
    source_city: str,
    target_city: str,
    task_type: str,
    device: torch.device,
    in_len: int,
    out_len: int,
    batch_size: int,
    hidden_dim: int,
    heads: int,
    hyperedges: str,
    lr: float,
    epochs: int,
    patience: int,
    lambda_adv: float,
    adv_warmup_epochs: int,
    epsilon_percentile: float,
    epsilon_value: 'Optional[float]',
    target_train_days: int,
):
    src_dir = os.path.join(data_root, source_city)
    tgt_dir = os.path.join(data_root, target_city)

    Xs = load_city_data(source_city, src_dir)
    Xt = load_city_data(target_city, tgt_dir)

    As = load_adjacency_for_city(source_city, src_dir, epsilon_percentile=epsilon_percentile, epsilon_value=epsilon_value)
    At = load_adjacency_for_city(target_city, tgt_dir, epsilon_percentile=epsilon_percentile, epsilon_value=epsilon_value)

    splits = build_splits_with_target_7days(
        Xs, Xt,
        in_len=in_len, out_len=out_len,
        points_per_day=288,
        target_train_days=target_train_days
    )
    (Xs_tr, Xs_va, Xs_te, Xt_tr, Xt_va, Xt_te) = splits

    scaler_s = ZScoreScaler.fit(Xs_tr, per_node=True)
    scaler_t = ZScoreScaler.fit(Xt_tr, per_node=True)

    Xs_trn = scaler_s.transform(Xs_tr); Xs_van = scaler_s.transform(Xs_va); Xs_ten = scaler_s.transform(Xs_te)
    Xt_trn = scaler_t.transform(Xt_tr); Xt_van = scaler_t.transform(Xt_va); Xt_ten = scaler_t.transform(Xt_te)

    train_s, val_s, test_s, train_t, val_t, test_t = make_dataloaders(
        Xs_trn, Xs_van, Xs_ten,
        Xt_trn, Xt_van, Xt_ten,
        in_len=in_len, out_len=out_len,
        batch_size=batch_size
    )

    hyperedges_list = [int(x) for x in hyperedges.split(",") if str(x).strip() != ""]
    model = D2MHyper(
        Ns=Xs.shape[1], Nt=Xt.shape[1],
        A_s=As, A_t=At,
        in_dim=1, hidden_dim=hidden_dim,
        hyperedges=hyperedges_list,
        heads=heads,
        out_len=out_len
    ).to(device)

    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    best_val = float("inf")
    wait = 0
    mse = nn.MSELoss()

    # mape denom heuristic (only affects MAPE, MAE unaffected)
    mape_min_denom = 5.0 if task_type.lower() == "flow" else 1.0

    for ep in range(1, epochs + 1):
        p = min(1.0, ep / max(1, adv_warmup_epochs))
        _ = train_one_epoch(model, train_s, train_t, optimizer, device, lambda_adv, adv_alpha=p)

        # val on target
        model.eval()
        val_losses = []
        with torch.no_grad():
            for xt, yt in val_t:
                xt, yt = xt.to(device), yt.to(device)
                _, ytp, _ = model(None, xt, only_target=True)
                val_losses.append(mse(ytp, yt).item())
        val_loss = float(np.mean(val_losses)) if len(val_losses) > 0 else 1e9

        print(f"Epoch {ep:03d} | target_val_mse={val_loss:.6f} | p={p:.2f}")

        if val_loss < best_val - 1e-6:
            best_val = val_loss
            wait = 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                print(f"[EarlyStop] best target_val_mse={best_val:.6f}")
                break

    if 'best_state' in locals():
        model.load_state_dict(best_state, strict=True)

    mae_avg, metrics = eval_target_mae_avg(model, test_t, device, scaler_t, out_len=out_len, mape_min_denom=mape_min_denom)
    return mae_avg, metrics, count_trainable_params(model)


def run_homo_temporal_split_get_mae_avg(
    *,
    data_root: str,
    city: str,
    task_type: str,
    device: torch.device,
    homo_src_ratio: float,
    **train_kwargs,
):
    """
    HOMO(A): within-city temporal split:
      source = first ratio of time, target = remaining.
    Uses same pipeline as hetero by treating (Xs, Xt) as two "domains".
    """
    city_dir = os.path.join(data_root, city)
    X = load_city_data(city, city_dir)  # (T,N,1)
    T = X.shape[0]
    cut = int(T * homo_src_ratio)

    min_need = int(train_kwargs["in_len"] + train_kwargs["out_len"] + 10)
    cut = max(cut, min_need)
    cut = min(cut, T - min_need)

    Xs = X[:cut]
    Xt = X[cut:]

    # Use the same city's adjacency for both domains
    A = load_adjacency_for_city(city, city_dir,
                               epsilon_percentile=train_kwargs["epsilon_percentile"],
                               epsilon_value=train_kwargs["epsilon_value"])

    # build splits (same helper) but we need to bypass load_adjacency_for_city inside run_task_get_mae_avg.
    # So we inline the core pipeline here, reusing the same functions/classes.
    splits = build_splits_with_target_7days(
        Xs, Xt,
        in_len=train_kwargs["in_len"], out_len=train_kwargs["out_len"],
        points_per_day=288,
        target_train_days=train_kwargs["target_train_days"]
    )
    (Xs_tr, Xs_va, Xs_te, Xt_tr, Xt_va, Xt_te) = splits

    scaler_s = ZScoreScaler.fit(Xs_tr, per_node=True)
    scaler_t = ZScoreScaler.fit(Xt_tr, per_node=True)

    Xs_trn = scaler_s.transform(Xs_tr); Xs_van = scaler_s.transform(Xs_va); Xs_ten = scaler_s.transform(Xs_te)
    Xt_trn = scaler_t.transform(Xt_tr); Xt_van = scaler_t.transform(Xt_va); Xt_ten = scaler_t.transform(Xt_te)

    train_s, val_s, test_s, train_t, val_t, test_t = make_dataloaders(
        Xs_trn, Xs_van, Xs_ten,
        Xt_trn, Xt_van, Xt_ten,
        in_len=train_kwargs["in_len"], out_len=train_kwargs["out_len"],
        batch_size=train_kwargs["batch_size"]
    )

    hyperedges_list = [int(x) for x in train_kwargs["hyperedges"].split(",") if str(x).strip() != ""]
    model = D2MHyper(
        Ns=Xs.shape[1], Nt=Xt.shape[1],
        A_s=A, A_t=A,
        in_dim=1, hidden_dim=train_kwargs["hidden_dim"],
        hyperedges=hyperedges_list,
        heads=train_kwargs["heads"],
        out_len=train_kwargs["out_len"]
    ).to(device)

    optimizer = AdamW(model.parameters(), lr=train_kwargs["lr"], weight_decay=1e-4)

    best_val = float("inf")
    wait = 0
    mse = nn.MSELoss()

    mape_min_denom = 5.0 if task_type.lower() == "flow" else 1.0

    for ep in range(1, train_kwargs["epochs"] + 1):
        p = min(1.0, ep / max(1, train_kwargs["adv_warmup_epochs"]))
        _ = train_one_epoch(model, train_s, train_t, optimizer, device, train_kwargs["lambda_adv"], adv_alpha=p)

        model.eval()
        val_losses = []
        with torch.no_grad():
            for xt, yt in val_t:
                xt, yt = xt.to(device), yt.to(device)
                _, ytp, _ = model(None, xt, only_target=True)
                val_losses.append(mse(ytp, yt).item())
        val_loss = float(np.mean(val_losses)) if len(val_losses) > 0 else 1e9

        print(f"Epoch {ep:03d} | target_val_mse={val_loss:.6f} | p={p:.2f}")

        if val_loss < best_val - 1e-6:
            best_val = val_loss
            wait = 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= train_kwargs["patience"]:
                print(f"[EarlyStop] best target_val_mse={best_val:.6f}")
                break

    if 'best_state' in locals():
        model.load_state_dict(best_state, strict=True)

    mae_avg, metrics = eval_target_mae_avg(model, test_t, device, scaler_t,
                                           out_len=train_kwargs["out_len"],
                                           mape_min_denom=mape_min_denom)
    return mae_avg, metrics, count_trainable_params(model)


# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()

    # data
    parser.add_argument("--data_root", type=str, default="/home/zc/wanganna/")
    parser.add_argument("--task_type", type=str, choices=["flow", "speed"], default="flow")

    # hetero
    parser.add_argument("--hetero_source", type=str, default="PEMS03")
    parser.add_argument("--hetero_target", type=str, default="PEMS08")

    # homo(A)
    parser.add_argument("--homo_city", type=str, default="PEMS03")
    parser.add_argument("--homo_src_ratio", type=float, default=0.6)

    # training hyperparams (match train_one_task.py defaults as much as possible)
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--in_len", type=int, default=12)
    parser.add_argument("--out_len", type=int, default=12)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--hidden_dim", type=int, default=64)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--hyperedges", type=str, default="20,80,200")
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--lambda_adv", type=float, default=0.1)
    parser.add_argument("--adv_warmup_epochs", type=int, default=10)

    parser.add_argument("--epsilon_percentile", type=float, default=0.10)
    parser.add_argument("--epsilon_value", type=float, default=None)

    # to match train_one_task target limited train data
    parser.add_argument("--target_train_days", type=int, default=7)

    # output
    parser.add_argument("--out_csv", type=str, default="outputs/d2mhyper_shift.csv")

    args = parser.parse_args()
    ensure_dir(os.path.dirname(args.out_csv) if os.path.dirname(args.out_csv) else ".")
    set_seed(args.seed)

    device = torch.device(f"cuda:{args.gpu}" if torch.cuda.is_available() else "cpu")
    print(f"[Device] {device}")

    train_kwargs = dict(
        in_len=args.in_len,
        out_len=args.out_len,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        heads=args.heads,
        hyperedges=args.hyperedges,
        lr=args.lr,
        epochs=args.epochs,
        patience=args.patience,
        lambda_adv=args.lambda_adv,
        adv_warmup_epochs=args.adv_warmup_epochs,
        epsilon_percentile=args.epsilon_percentile,
        epsilon_value=args.epsilon_value,
        target_train_days=args.target_train_days,
    )

    # -------------------------
    # 1) HETERO
    # -------------------------
    print("\n==================== [HETERO] ====================")
    print(f"[HETERO TASK] {args.hetero_source} -> {args.hetero_target}")
    mae_hetero_avg, metrics_hetero, params_hetero = run_task_get_mae_avg(
        data_root=args.data_root,
        source_city=args.hetero_source,
        target_city=args.hetero_target,
        task_type=args.task_type,
        device=device,
        **train_kwargs
    )
    print(f"[HETERO] MAE_avg = {mae_hetero_avg:.6f}")

    # -------------------------
    # 2) HOMO(A): temporal split within same city
    # -------------------------
    print("\n===================== [HOMO] =====================")
    print(f"[HOMO TASK] {args.homo_city} -> {args.homo_city} (temporal split, src_ratio={args.homo_src_ratio})")
    mae_homo_avg, metrics_homo, params_homo = run_homo_temporal_split_get_mae_avg(
        data_root=args.data_root,
        city=args.homo_city,
        task_type=args.task_type,
        device=device,
        homo_src_ratio=args.homo_src_ratio,
        **train_kwargs
    )
    print(f"[HOMO] MAE_avg = {mae_homo_avg:.6f}")

    # -------------------------
    # 3) ΔM_shift
    # -------------------------
    delta_m_shift = (mae_hetero_avg - mae_homo_avg) / max(mae_homo_avg, 1e-12) * 100.0
    print("\n================== [ΔM_shift] ==================")
    print(f"MAE_homo (avg)   = {mae_homo_avg:.6f}")
    print(f"MAE_hetero (avg) = {mae_hetero_avg:.6f}")
    print(f"ΔM_shift (%)     = {delta_m_shift:.4f}%")
    print("================================================\n")

    # save
    row = {
        "model": "D2MHyper",
        "task_type": args.task_type,
        "hetero_source": args.hetero_source,
        "hetero_target": args.hetero_target,
        "homo_city": args.homo_city,
        "homo_src_ratio": float(args.homo_src_ratio),
        "MAE_homo_avg": float(mae_homo_avg),
        "MAE_hetero_avg": float(mae_hetero_avg),
        "Delta_M_shift(%)": float(delta_m_shift),
        "epochs": int(args.epochs),
        "patience": int(args.patience),
        "batch_size": int(args.batch_size),
        "lr": float(args.lr),
        "hidden_dim": int(args.hidden_dim),
        "heads": int(args.heads),
        "hyperedges": args.hyperedges,
        "target_train_days": int(args.target_train_days),
        "seed": int(args.seed),
        "params_hetero": int(params_hetero),
        "params_homo": int(params_homo),
    }
    append_to_csv(args.out_csv, row)
    print(f"[OK] Saved shift results to: {args.out_csv}")


if __name__ == "__main__":
    main()
