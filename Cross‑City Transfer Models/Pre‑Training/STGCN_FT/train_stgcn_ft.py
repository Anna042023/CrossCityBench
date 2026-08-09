#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch

from stgcn_ft.data import prepare_domain, make_loader, autodiscover_dataset_files
from stgcn_ft.engine import TrainConfig, fit_model, evaluate_and_report
from stgcn_ft.graph import load_adjacency, build_cheb_tensor
from stgcn_ft.model import STGCN, STGCNConfig
from stgcn_ft.transfer import transfer_shape_compatible_parameters


TASKS = {
    "pems03_to_pems04": ("PEMS03", "PEMS04", "flow"),
    "pems03_to_pems08": ("PEMS03", "PEMS08", "flow"),
    "pemsbay_to_metrla": ("PEMS-BAY", "METR-LA", "speed"),
    "metrla_to_pemsbay": ("METR-LA", "PEMS-BAY", "speed"),
    "pemsbay_to_sztaxi": ("PEMS-BAY", "SZ-Taxi", "speed"),
}


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def resolve_device(device: str):
    if device.startswith("cuda") and not torch.cuda.is_available():
        print("[WARN] CUDA requested but unavailable; using CPU.")
        return torch.device("cpu")
    return torch.device(device)


def resolve_files(args, source_name: str, target_name: str):
    if args.source_data and args.source_adj:
        src_data, src_adj = Path(args.source_data), Path(args.source_adj)
    else:
        src_data, src_adj = autodiscover_dataset_files(args.data_root, source_name)
    if args.target_data and args.target_adj:
        tgt_data, tgt_adj = Path(args.target_data), Path(args.target_adj)
    else:
        tgt_data, tgt_adj = autodiscover_dataset_files(args.data_root, target_name)
    return src_data, src_adj, tgt_data, tgt_adj


def print_report(report: Dict, steps_per_day: int):
    print("\n" + "=" * 92)
    print("STGCN-FT FINAL TARGET TEST RESULTS")
    print("=" * 92)
    for h in (3, 6, 12):
        key = str(h)
        if key not in report:
            continue
        minutes = int(round(h * 1440 / steps_per_day)) if steps_per_day > 0 else h
        r = report[key]
        print(f"{minutes:>3d} min | MAE {r['MAE']:.4f} | RMSE {r['RMSE']:.4f} | MAPE {r['MAPE']:.4f}%")
    r = report["Average"]
    print("-" * 92)
    print(f"Average | MAE {r['MAE']:.4f} | RMSE {r['RMSE']:.4f} | MAPE {r['MAPE']:.4f}%")
    print("=" * 92)


def aggregate_reports(reports):
    keys = list(reports[0].keys())
    out = {}
    for k in keys:
        out[k] = {}
        for m in ("MAE", "RMSE", "MAPE"):
            vals = np.array([r[k][m] for r in reports], dtype=float)
            out[k][m] = {"mean": float(vals.mean()), "std": float(vals.std(ddof=0))}
    return out


def run_once(args, run_idx: int, seed: int):
    set_seed(seed)
    device = resolve_device(args.device)
    source_name, target_name, task_type = TASKS[args.task]
    src_data, src_adj, tgt_data, tgt_adj = resolve_files(args, source_name, target_name)

    run_dir = Path(args.save_dir) / args.task / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "#" * 92)
    print(f"Run {run_idx + 1}/{args.repeat} | seed={seed} | task={source_name} -> {target_name}")
    print("#" * 92)
    print(f"Source data: {src_data}")
    print(f"Source adj : {src_adj}")
    print(f"Target data: {tgt_data}")
    print(f"Target adj : {tgt_adj}")
    print(f"Device     : {device}")

    # DAGN uses 5-min datasets except SZ-Taxi (15-min). This script is mainly for the four 5-min tasks.
    horizon = args.horizon
    source = prepare_domain(
        src_data,
        history=args.history,
        horizon=horizon,
        feature_idx=args.source_feature_idx,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        train_days=None,
        steps_per_day=args.steps_per_day,
        train_stride=args.train_stride,
        eval_stride=args.eval_stride,
    )
    target = prepare_domain(
        tgt_data,
        history=args.history,
        horizon=horizon,
        feature_idx=args.target_feature_idx,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        train_days=args.target_train_days,
        steps_per_day=args.steps_per_day,
        train_stride=args.train_stride,
        eval_stride=args.eval_stride,
    )

    print(
        f"Source shape={source['raw_shape']}, train/val/test steps="
        f"{source['train_steps']}/{source['val_steps']}/{source['test_steps']}"
    )
    print(
        f"Target shape={target['raw_shape']}, FT train steps={target['train_steps']} "
        f"({args.target_train_days} days), val/test={target['val_steps']}/{target['test_steps']}"
    )
    print(f"Source scaler mean/std={source['scaler'].mean:.4f}/{source['scaler'].std:.4f}")
    print(f"Target scaler mean/std={target['scaler'].mean:.4f}/{target['scaler'].std:.4f}")

    W_s = load_adjacency(src_adj, source["n_nodes"])
    W_t = load_adjacency(tgt_adj, target["n_nodes"])
    cheb_s = build_cheb_tensor(W_s, args.ks, device=device)
    cheb_t = build_cheb_tensor(W_t, args.ks, device=device)

    model_cfg = STGCNConfig(
        n_his=args.history,
        ks=args.ks,
        kt=args.kt,
        blocks=((1, 32, 64), (64, 32, 128)),
        dropout=args.dropout,
    )

    # ---------------- Source pre-training ----------------
    source_model = STGCN(source["n_nodes"], cheb_s, model_cfg).to(device)
    src_train_loader = make_loader(source["train_ds"], args.batch_size, True, args.num_workers)
    src_val_loader = make_loader(source["val_one_ds"], args.eval_batch_size, False, args.num_workers)

    pre_cfg = TrainConfig(
        epochs=args.pretrain_epochs,
        patience=args.patience,
        lr=args.lr,
        weight_decay=args.weight_decay,
        optimizer=args.optimizer,
        lr_decay_every=args.lr_decay_every,
        lr_decay_rate=args.lr_decay_rate,
        grad_clip=args.grad_clip,
    )
    print("\n[Stage 1] Source-city pre-training")
    src_hist, src_best_epoch, src_best = fit_model(
        source_model,
        src_train_loader,
        src_val_loader,
        device,
        pre_cfg,
        run_dir / "source_best.pt",
        val_mode="one_step",
        verbose_prefix="[PRE] ",
    )

    # ---------------- Target model + compatible transfer ----------------
    target_model = STGCN(target["n_nodes"], cheb_t, model_cfg).to(device)
    copied, skipped = transfer_shape_compatible_parameters(source_model, target_model)
    print("\n[Transfer] source -> target")
    print(f"Transferred trainable tensors: {len(copied)}")
    print(f"Reinitialized target-specific tensors: {len(skipped)}")
    for name, reason in skipped:
        print(f"  SKIP {name}: {reason}")

    transfer_info = {
        "copied": copied,
        "skipped": [{"name": n, "reason": r} for n, r in skipped],
    }
    with open(run_dir / "transfer_info.json", "w", encoding="utf-8") as f:
        json.dump(transfer_info, f, indent=2)

    # ---------------- Target fine-tuning ----------------
    tgt_train_loader = make_loader(target["train_ds"], args.batch_size, True, args.num_workers)
    if args.ft_val_mode == "multistep_mae":
        tgt_val_loader = make_loader(target["val_multi_ds"], args.eval_batch_size, False, args.num_workers)
    else:
        tgt_val_loader = make_loader(target["val_one_ds"], args.eval_batch_size, False, args.num_workers)

    ft_cfg = TrainConfig(
        epochs=args.finetune_epochs,
        patience=args.patience,
        lr=args.ft_lr,
        weight_decay=args.weight_decay,
        optimizer=args.optimizer,
        lr_decay_every=args.lr_decay_every,
        lr_decay_rate=args.lr_decay_rate,
        grad_clip=args.grad_clip,
    )
    print("\n[Stage 2] Target-city fine-tuning")
    ft_hist, ft_best_epoch, ft_best = fit_model(
        target_model,
        tgt_train_loader,
        tgt_val_loader,
        device,
        ft_cfg,
        run_dir / "target_ft_best.pt",
        val_mode=args.ft_val_mode,
        scaler=target["scaler"],
        verbose_prefix="[FT ] ",
    )

    # ---------------- Target test ----------------
    test_loader = make_loader(target["test_multi_ds"], args.eval_batch_size, False, args.num_workers)
    horizon_steps = (3, 6, 12) if args.steps_per_day == 288 else tuple(args.report_steps)
    report, y_true, y_pred = evaluate_and_report(
        target_model,
        test_loader,
        device,
        target["scaler"],
        horizon_steps=horizon_steps,
        mape_threshold=args.mape_threshold,
        mape_mode=args.mape_mode,
    )
    print_report(report, args.steps_per_day)

    np.savez_compressed(run_dir / "predictions.npz", y_true=y_true.astype(np.float32), y_pred=y_pred.astype(np.float32))
    payload = {
        "task": args.task,
        "source": source_name,
        "target": target_name,
        "seed": seed,
        "source_data": str(src_data),
        "source_adj": str(src_adj),
        "target_data": str(tgt_data),
        "target_adj": str(tgt_adj),
        "source_best_epoch": src_best_epoch,
        "target_best_epoch": ft_best_epoch,
        "metrics": report,
        "settings": vars(args),
    }
    with open(run_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return report


def parse_args():
    p = argparse.ArgumentParser(
        description="STGCN-FT: pre-train STGCN on source city, then fine-tune on 10-day target-city data."
    )
    p.add_argument("--task", choices=TASKS.keys(), required=True)
    p.add_argument("--data_root", type=str, default="./datasets")
    p.add_argument("--source_data", type=str, default=None)
    p.add_argument("--source_adj", type=str, default=None)
    p.add_argument("--target_data", type=str, default=None)
    p.add_argument("--target_adj", type=str, default=None)
    p.add_argument("--source_feature_idx", type=int, default=0)
    p.add_argument("--target_feature_idx", type=int, default=0)

    p.add_argument("--history", type=int, default=12)
    p.add_argument("--horizon", type=int, default=12)
    p.add_argument("--steps_per_day", type=int, default=288)
    p.add_argument("--report_steps", type=int, nargs="+", default=[3, 6, 12])
    p.add_argument("--target_train_days", type=int, default=10)
    p.add_argument("--train_ratio", type=float, default=0.7)
    p.add_argument("--val_ratio", type=float, default=0.1)
    p.add_argument("--train_stride", type=int, default=1)
    p.add_argument("--eval_stride", type=int, default=1)

    p.add_argument("--ks", type=int, default=3)
    p.add_argument("--kt", type=int, default=3)
    p.add_argument("--dropout", type=float, default=0.0)

    # DAGN-paper-oriented preset defaults: batch 16, lr 1e-3, 100 epochs, patience 10.
    # Architecture remains the supplied STGCN (two ST-Conv blocks, Cheb graph conv, gated temporal conv).
    p.add_argument("--batch_size", type=int, default=16)
    p.add_argument("--eval_batch_size", type=int, default=64)
    p.add_argument("--pretrain_epochs", type=int, default=100)
    p.add_argument("--finetune_epochs", type=int, default=100)
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--ft_lr", type=float, default=1e-4)
    p.add_argument("--optimizer", choices=["adamw", "adam", "rmsprop"], default="adamw")
    p.add_argument("--weight_decay", type=float, default=0.0)
    p.add_argument("--lr_decay_every", type=int, default=5)
    p.add_argument("--lr_decay_rate", type=float, default=0.7)
    p.add_argument("--grad_clip", type=float, default=5.0)
    p.add_argument("--ft_val_mode", choices=["one_step", "multistep_mae"], default="one_step")

    p.add_argument("--mape_mode", choices=["mask", "legacy"], default="mask")
    p.add_argument("--mape_threshold", type=float, default=1e-5)
    p.add_argument("--num_workers", type=int, default=0)
    p.add_argument("--device", type=str, default="cuda:0")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--save_dir", type=str, default="./runs/stgcn_ft")
    return p.parse_args()


def main():
    args = parse_args()
    reports = []
    for i in range(args.repeat):
        reports.append(run_once(args, i, args.seed + i))

    if len(reports) > 1:
        agg = aggregate_reports(reports)
        out_dir = Path(args.save_dir) / args.task
        with open(out_dir / "repeat_summary.json", "w", encoding="utf-8") as f:
            json.dump(agg, f, indent=2)
        print("\n" + "=" * 92)
        print(f"REPEAT SUMMARY ({len(reports)} runs): mean ± std")
        print("=" * 92)
        for k in ["3", "6", "12", "Average"]:
            if k not in agg:
                continue
            r = agg[k]
            print(
                f"{k:>7s} | MAE {r['MAE']['mean']:.4f}±{r['MAE']['std']:.4f} | "
                f"RMSE {r['RMSE']['mean']:.4f}±{r['RMSE']['std']:.4f} | "
                f"MAPE {r['MAPE']['mean']:.4f}±{r['MAPE']['std']:.4f}%"
            )
        print("=" * 92)


if __name__ == "__main__":
    main()
