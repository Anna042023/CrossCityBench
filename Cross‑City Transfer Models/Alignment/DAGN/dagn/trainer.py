from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from .metrics import horizon_metrics
from .utils import cycle_next, save_json


def domain_loss(logit_pair, device):
    if logit_pair is None:
        return torch.tensor(0.0, device=device)
    src_logits, tgt_logits = logit_pair
    src_labels = torch.zeros(src_logits.shape[0], dtype=torch.long, device=device)
    tgt_labels = torch.ones(tgt_logits.shape[0], dtype=torch.long, device=device)
    return F.cross_entropy(src_logits, src_labels) + F.cross_entropy(tgt_logits, tgt_labels)


def train_epoch(model, loaders, optimizer, prior_s, prior_t, device, alpha, beta, variant,
                grl_lambda=1.0, grad_clip=5.0, max_steps=0):
    model.train()
    src_loader = loaders["src_train"]
    tgt_loader = loaders["tgt_train"]
    steps = max(len(src_loader), len(tgt_loader))
    if max_steps and max_steps > 0:
        steps = min(steps, max_steps)

    src_iter = iter(src_loader)
    tgt_iter = iter(tgt_loader)
    totals = {"loss": 0.0, "pred": 0.0, "rg": 0.0, "td": 0.0, "sd": 0.0}

    for _ in range(steps):
        (xs, ys), src_iter = cycle_next(src_iter, src_loader)
        (xt, yt), tgt_iter = cycle_next(tgt_iter, tgt_loader)
        xs, ys = xs.to(device), ys.to(device)
        xt, yt = xt.to(device), yt.to(device)

        optimizer.zero_grad(set_to_none=True)
        out = model(xs, xt, prior_s, prior_t, grl_lambda=grl_lambda)

        lpred = F.mse_loss(out["pred_source"], ys) + F.mse_loss(out["pred_target"], yt)
        lrg = model.graph_reconstruction_loss(prior_s, prior_t)
        ltd = domain_loss(out["temporal_logits"], device)
        lsd = domain_loss(out["spatial_logits"], device)

        # Paper Eq. (25): L = Lpred + alpha*Lrg + beta*(Ltd+Lsd)
        # Ablation variants selectively turn terms off.
        rg_weight = 0.0 if variant in {"M1", "M2"} else alpha
        td_weight = 0.0 if variant in {"M1", "M3a"} else beta
        sd_weight = 0.0 if variant in {"M1", "M3b"} else beta
        loss = lpred + rg_weight * lrg + td_weight * ltd + sd_weight * lsd

        loss.backward()
        if grad_clip and grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()

        totals["loss"] += float(loss.detach().cpu())
        totals["pred"] += float(lpred.detach().cpu())
        totals["rg"] += float(lrg.detach().cpu())
        totals["td"] += float(ltd.detach().cpu())
        totals["sd"] += float(lsd.detach().cpu())

    for k in totals:
        totals[k] /= max(steps, 1)
    return totals


def _paired_source_batch(src_iter, src_loader, target_batch_size):
    batch, src_iter = cycle_next(src_iter, src_loader)
    xs, ys = batch
    # Evaluation loaders do not drop_last. Make source context batch match target batch.
    if xs.shape[0] < target_batch_size:
        pieces_x = [xs]
        pieces_y = [ys]
        have = xs.shape[0]
        while have < target_batch_size:
            (x2, y2), src_iter = cycle_next(src_iter, src_loader)
            need = target_batch_size - have
            pieces_x.append(x2[:need])
            pieces_y.append(y2[:need])
            have += min(need, x2.shape[0])
        xs = torch.cat(pieces_x, dim=0)[:target_batch_size]
        ys = torch.cat(pieces_y, dim=0)[:target_batch_size]
    elif xs.shape[0] > target_batch_size:
        xs, ys = xs[:target_batch_size], ys[:target_batch_size]
    return (xs, ys), src_iter


@torch.no_grad()
def evaluate(model, loaders, split, prepared, prior_s, prior_t, device, mape_threshold=1e-5,
             save_predictions_path=None, save_aux_path=None):
    model.eval()
    tgt_loader = loaders[f"tgt_{split}"]
    src_loader = loaders[f"src_{split}"]
    src_iter = iter(src_loader)

    y_true_all, y_pred_all = [], []
    aux_saved = False

    for xt, yt in tgt_loader:
        (xs, _), src_iter = _paired_source_batch(src_iter, src_loader, xt.shape[0])
        xs = xs.to(device)
        xt = xt.to(device)
        out = model(xs, xt, prior_s, prior_t, grl_lambda=0.0, return_aux=(save_aux_path is not None and not aux_saved))
        pred = out["pred_target"].cpu().numpy()
        true = yt.numpy()
        y_true_all.append(true)
        y_pred_all.append(pred)

        if save_aux_path is not None and not aux_saved:
            payload = {}
            if out.get("theta") is not None:
                ts, tt, tcc = out["theta"]
                payload["theta_source"] = ts.detach().cpu().numpy()
                payload["theta_target"] = tt.detach().cpu().numpy()
                payload["theta_cross_city"] = tcc.detach().cpu().numpy()
            if out.get("attention") is not None:
                a_s, a_t = out["attention"]
                payload["attention_source"] = a_s.detach().cpu().numpy()
                payload["attention_target"] = a_t.detach().cpu().numpy()
            if out.get("adjacency") is not None:
                payload["learned_adjacency"] = out["adjacency"].detach().cpu().numpy()
            if payload:
                np.savez_compressed(save_aux_path, **payload)
            aux_saved = True

    y_true = np.concatenate(y_true_all, axis=0)
    y_pred = np.concatenate(y_pred_all, axis=0)
    scaler = prepared.target.scaler
    y_true_raw = scaler.inverse_transform(y_true)
    y_pred_raw = scaler.inverse_transform(y_pred)

    metrics = horizon_metrics(
        y_true_raw,
        y_pred_raw,
        interval_minutes=prepared.target.interval_minutes,
        mape_threshold=mape_threshold,
    )
    if save_predictions_path is not None:
        np.savez_compressed(
            save_predictions_path,
            y_true=y_true_raw.astype(np.float32),
            y_pred=y_pred_raw.astype(np.float32),
        )
    return metrics


def print_metrics(metrics, prefix="TEST"):
    print(f"[{prefix}]")
    for name in ["15min", "30min", "60min", "Average"]:
        if name not in metrics:
            continue
        m = metrics[name]
        print(
            f"  {name:<8} | MAE {m['MAE']:.4f} | RMSE {m['RMSE']:.4f} | MAPE {m['MAPE']:.4f}%"
        )


def fit(model, loaders, prepared, args, save_dir, device):
    save_dir = Path(save_dir)
    prior_s = torch.as_tensor(prepared.source.adj, dtype=torch.float32, device=device)
    prior_t = torch.as_tensor(prepared.target.adj, dtype=torch.float32, device=device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    best_score = float("inf")
    bad_epochs = 0
    history = []
    ckpt_path = save_dir / "best.pt"

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_stat = train_epoch(
            model, loaders, optimizer, prior_s, prior_t, device,
            alpha=args.alpha, beta=args.beta, variant=args.variant,
            grl_lambda=args.grl_lambda, grad_clip=args.grad_clip,
            max_steps=args.max_steps_per_epoch,
        )
        val_metrics = evaluate(
            model, loaders, "val", prepared, prior_s, prior_t, device,
            mape_threshold=args.mape_threshold,
        )
        val_mae = val_metrics["Average"]["MAE"]
        dt = time.time() - t0
        print(
            f"Epoch {epoch:03d} | {dt:7.1f}s | loss={train_stat['loss']:.5f} "
            f"pred={train_stat['pred']:.5f} rg={train_stat['rg']:.5f} "
            f"td={train_stat['td']:.5f} sd={train_stat['sd']:.5f} | "
            f"val_avg_MAE={val_mae:.4f}"
        )
        history.append({"epoch": epoch, "seconds": dt, **train_stat, "val": val_metrics})

        if val_mae < best_score - args.min_delta:
            best_score = val_mae
            bad_epochs = 0
            torch.save({
                "model": model.state_dict(),
                "epoch": epoch,
                "val_mae": val_mae,
                "args": vars(args),
            }, ckpt_path)
            print(f"  -> saved best checkpoint: {ckpt_path}")
        else:
            bad_epochs += 1
            if bad_epochs >= args.patience:
                print(f"Early stopping at epoch {epoch} (patience={args.patience}).")
                break

    save_json(history, save_dir / "history.json")
    state = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(state["model"])
    return model, prior_s, prior_t
