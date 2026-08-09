#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from dagn.data import prepare_transfer_data, build_dataloaders, canonical_name, INTERVAL_MINUTES
from dagn.model import DAGN
from dagn.trainer import fit, evaluate, print_metrics
from dagn.utils import count_parameters, device_from_arg, ensure_dir, save_json, set_seed


PAPER_TASKS = {
    "pems03_to_pems04": ("PEMS03", "PEMS04", "flow"),
    "pems03_to_pems08": ("PEMS03", "PEMS08", "flow"),
    "metrla_to_pemsbay": ("METR-LA", "PEMS-BAY", "speed"),
    "pemsbay_to_metrla": ("PEMS-BAY", "METR-LA", "speed"),
    "pemsbay_to_sztaxi": ("PEMS-BAY", "SZ-TAXI", "speed"),
}

PAPER_DAGN_PARAMS = {
    # Table 5 in the paper, target-task parameter counts.
    "PEMS04": 115267,
    "PEMS08": 110883,
    "METR-LA": 87923,
    "PEMS-BAY": 87923,
    "SZ-TAXI": 29762,
}


def infer_task_type(source, target):
    flow = {"PEMS03", "PEMS04", "PEMS08"}
    return "flow" if source in flow and target in flow else "speed"


def build_parser():
    p = argparse.ArgumentParser(
        description="Reproduction of DAGN: Domain adversarial graph neural network with cross-city graph structure learning"
    )
    p.add_argument("--data_root", type=str, default="./datasets")
    p.add_argument("--task", choices=list(PAPER_TASKS.keys()), default=None)
    p.add_argument("--source", type=str, default="PEMS03")
    p.add_argument("--target", type=str, default="PEMS08")
    p.add_argument("--source_data", type=str, default=None)
    p.add_argument("--target_data", type=str, default=None)
    p.add_argument("--source_adj", type=str, default=None)
    p.add_argument("--target_adj", type=str, default=None)
    p.add_argument("--source_sensor_ids", type=str, default=None)
    p.add_argument("--target_sensor_ids", type=str, default=None)
    p.add_argument("--allow_identity_adj", action="store_true")
    p.add_argument("--feature_idx", type=int, default=0)
    p.add_argument("--source_interval", type=int, default=None)
    p.add_argument("--target_interval", type=int, default=None)

    # Paper: historical one hour -> next one hour.
    p.add_argument("--history", type=int, default=None)
    p.add_argument("--horizon", type=int, default=None)
    p.add_argument("--target_train_days", type=int, default=10)

    # Paper disclosed settings.
    p.add_argument("--batch_size", type=int, default=16)
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight_decay", type=float, default=1e-4)
    p.add_argument("--emb_dim", type=int, default=32)
    p.add_argument("--alpha", type=float, default=None)
    p.add_argument("--beta", type=float, default=None)

    # Not explicitly disclosed in the paper; kept configurable.
    p.add_argument("--temporal_dim", type=int, default=64)
    p.add_argument("--spatial_dim", type=int, default=32)
    p.add_argument("--disc_hidden", type=int, default=32)
    p.add_argument("--predictor_hidden", type=int, default=32)
    p.add_argument("--tau", type=float, default=0.5)
    p.add_argument("--grl_lambda", type=float, default=1.0)
    p.add_argument("--no_normalize_adj", action="store_true")
    p.add_argument("--soft_graph_eval", action="store_true")

    p.add_argument("--variant", choices=["full", "M1", "M2", "M3a", "M3b", "M4a", "M4b"], default="full")
    p.add_argument("--seed", type=int, default=2023)
    p.add_argument("--device", type=str, default="cuda:0")
    p.add_argument("--num_workers", type=int, default=0)
    p.add_argument("--grad_clip", type=float, default=5.0)
    p.add_argument("--min_delta", type=float, default=1e-4)
    p.add_argument("--mape_threshold", type=float, default=1e-5)
    p.add_argument("--max_steps_per_epoch", type=int, default=0,
                   help="0 = full epoch. Positive value is useful only for smoke tests/debugging.")
    p.add_argument("--save_dir", type=str, default="./runs")
    p.add_argument("--eval_only", action="store_true")
    p.add_argument("--checkpoint", type=str, default=None)
    return p


def resolve_args(args):
    if args.task:
        args.source, args.target, task_type = PAPER_TASKS[args.task]
    else:
        args.source = canonical_name(args.source)
        args.target = canonical_name(args.target)
        task_type = infer_task_type(args.source, args.target)

    args.source = canonical_name(args.source)
    args.target = canonical_name(args.target)

    target_interval = args.target_interval or INTERVAL_MINUTES.get(args.target, 5)
    source_interval = args.source_interval or INTERVAL_MINUTES.get(args.source, 5)
    args.target_interval = target_interval
    args.source_interval = source_interval

    if args.history is None:
        args.history = int(60 // target_interval)
    if args.horizon is None:
        args.horizon = int(60 // target_interval)
    if args.history != args.horizon:
        raise ValueError(
            "This reproduction follows the paper's one-hour-history -> one-hour-future setting, "
            "where Ph=Pf. Please use equal --history and --horizon."
        )

    if args.alpha is None:
        args.alpha = 0.5 if task_type == "flow" else 1.0
    if args.beta is None:
        args.beta = 3.0 if task_type == "flow" else 1.0
    args.task_type = task_type
    return args


def main():
    args = resolve_args(build_parser().parse_args())
    set_seed(args.seed)
    device = device_from_arg(args.device)

    run_name = f"{args.source}_to_{args.target}_{args.variant}_seed{args.seed}"
    save_dir = ensure_dir(Path(args.save_dir) / run_name)
    save_json(vars(args), save_dir / "args.json")

    print("=" * 88)
    print("DAGN reproduction")
    print(f"Task       : {args.source} -> {args.target} ({args.task_type})")
    print(f"Variant    : {args.variant}")
    print(f"Device     : {device}")
    print(f"History/Pf : {args.history}/{args.horizon}")
    print(f"Target days: {args.target_train_days}")
    print(f"alpha/beta : {args.alpha}/{args.beta}")
    print("=" * 88)

    prepared = prepare_transfer_data(args)
    datasets, loaders = build_dataloaders(prepared, args.batch_size, args.num_workers)

    model = DAGN(
        n_source=prepared.source.data_norm.shape[1],
        n_target=prepared.target.data_norm.shape[1],
        seq_len=args.history,
        in_dim=1,
        out_dim=1,
        emb_dim=args.emb_dim,
        temporal_dim=args.temporal_dim,
        spatial_dim=args.spatial_dim,
        discriminator_hidden=args.disc_hidden,
        predictor_hidden=args.predictor_hidden,
        tau=args.tau,
        variant=args.variant,
        normalize_adj=not args.no_normalize_adj,
        hard_graph_eval=not args.soft_graph_eval,
    ).to(device)

    n_params = count_parameters(model)
    print(f"[Model] Trainable parameters: {n_params:,}")
    paper_count = PAPER_DAGN_PARAMS.get(args.target) if args.variant == "full" else None
    if paper_count:
        print(
            f"[Paper] Table-5 DAGN parameter count for this target/task: {paper_count:,}. "
            f"Gap={n_params - paper_count:+,}. The paper does not disclose d_td/d_sd/discriminator widths, "
            "so exact parameter matching is not guaranteed."
        )

    if args.eval_only:
        if not args.checkpoint:
            raise ValueError("--eval_only requires --checkpoint")
        state = torch.load(args.checkpoint, map_location=device)
        model.load_state_dict(state["model"] if "model" in state else state)
        prior_s = torch.as_tensor(prepared.source.adj, dtype=torch.float32, device=device)
        prior_t = torch.as_tensor(prepared.target.adj, dtype=torch.float32, device=device)
    else:
        model, prior_s, prior_t = fit(model, loaders, prepared, args, save_dir, device)

    metrics = evaluate(
        model, loaders, "test", prepared, prior_s, prior_t, device,
        mape_threshold=args.mape_threshold,
        save_predictions_path=save_dir / "predictions.npz",
        save_aux_path=save_dir / "learned_structures.npz",
    )
    print_metrics(metrics, "TEST")
    save_json(metrics, save_dir / "metrics.json")

    final = {
        "task": f"{args.source}->{args.target}",
        "variant": args.variant,
        "seed": args.seed,
        "parameters": n_params,
        "metrics": metrics,
    }
    save_json(final, save_dir / "summary.json")
    print(f"[Saved] {save_dir}")


if __name__ == "__main__":
    main()
