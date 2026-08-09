import os
import time
import csv
import argparse
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
from profiler_utils import measure_inference_and_memory
from utils import set_seed, ensure_dir, count_trainable_params


def train_one_epoch(model, loader_s, loader_t, optimizer, device, lambda_adv, adv_alpha=1.0):
    model.train()
    mse = nn.MSELoss()

    it_s = iter(loader_s)
    it_t = iter(loader_t)
    steps = max(len(loader_s), len(loader_t))
    loss_sum = 0.0
    loss_s_sum = 0.0
    loss_t_sum = 0.0
    adv_sum = 0.0

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
        lambda_eff = lambda_adv * float(adv_alpha)
        loss = loss_s + loss_t + lambda_eff * adv_loss

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        optimizer.step()
        loss_sum += loss.item()
        loss_s_sum += loss_s.item()
        loss_t_sum += loss_t.item()
        adv_sum += adv_loss.item()

    return (loss_sum / steps), (loss_s_sum / steps), (loss_t_sum / steps), (adv_sum / steps)


@torch.no_grad()
def eval_target(model, loader_t, device, scaler_t, out_len=12, mape_min_denom=1.0):
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
    return metrics


def append_to_csv(path, row_dict):
    exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row_dict.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row_dict)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", type=str, required=True)
    parser.add_argument("--source", type=str, required=True)
    parser.add_argument("--target", type=str, required=True)
    parser.add_argument("--task_type", type=str, choices=["flow", "speed"], required=True)

    parser.add_argument("--out_dir", type=str, default="./outputs")
    parser.add_argument("--results_csv", type=str, default="./outputs/d2mhyper_results.csv")
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)

    parser.add_argument("--in_len", type=int, default=12)
    parser.add_argument("--out_len", type=int, default=12)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--hidden_dim", type=int, default=64)
    parser.add_argument("--heads", type=int, default=3)  # 即使是 3，模型内部也会自动修复
    parser.add_argument("--hyperedges", type=str, default="20,80,200")
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--lambda_adv", type=float, default=0.1)
    parser.add_argument("--adv_warmup_epochs", type=int, default=10)
    parser.add_argument("--mape_min_denom", type=float, default=None)

    parser.add_argument("--epsilon_percentile", type=float, default=0.10)
    parser.add_argument("--epsilon_value", type=float, default=None)

    args = parser.parse_args()
    ensure_dir(args.out_dir)
    set_seed(args.seed)

    device = torch.device(f"cuda:{args.gpu}" if torch.cuda.is_available() else "cpu")
    print(f"[Device] {device}")

    src_dir = os.path.join(args.data_root, args.source)
    tgt_dir = os.path.join(args.data_root, args.target)

    Xs = load_city_data(args.source, src_dir)
    Xt = load_city_data(args.target, tgt_dir)

    As = load_adjacency_for_city(args.source, src_dir, epsilon_percentile=args.epsilon_percentile, epsilon_value=args.epsilon_value)
    At = load_adjacency_for_city(args.target, tgt_dir, epsilon_percentile=args.epsilon_percentile, epsilon_value=args.epsilon_value)

    print(f"[Data] {args.source}: X={Xs.shape}, A={As.shape}")
    print(f"[Data] {args.target}: X={Xt.shape}, A={At.shape}")

    splits = build_splits_with_target_7days(
        Xs, Xt,
        in_len=args.in_len, out_len=args.out_len,
        points_per_day=288,
        target_train_days=7
    )
    (Xs_tr, Xs_va, Xs_te, Xt_tr, Xt_va, Xt_te) = splits

    scaler_s = ZScoreScaler.fit(Xs_tr, per_node=True)
    scaler_t = ZScoreScaler.fit(Xt_tr, per_node=True)

    Xs_trn = scaler_s.transform(Xs_tr); Xs_van = scaler_s.transform(Xs_va); Xs_ten = scaler_s.transform(Xs_te)
    Xt_trn = scaler_t.transform(Xt_tr); Xt_van = scaler_t.transform(Xt_va); Xt_ten = scaler_t.transform(Xt_te)

    train_s, val_s, test_s, train_t, val_t, test_t = make_dataloaders(
        Xs_trn, Xs_van, Xs_ten,
        Xt_trn, Xt_van, Xt_ten,
        in_len=args.in_len, out_len=args.out_len,
        batch_size=args.batch_size
    )

    hyperedges = [int(x) for x in args.hyperedges.split(",")]
    model = D2MHyper(
        Ns=Xs.shape[1], Nt=Xt.shape[1],
        A_s=As, A_t=At,
        in_dim=1, hidden_dim=args.hidden_dim,
        hyperedges=hyperedges,
        heads=args.heads,
        out_len=args.out_len
    ).to(device)

    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    trainable_params = count_trainable_params(model)
    print(f"[Model] Trainable params: {trainable_params:,}")

    best_val = float("inf")
    best_path = os.path.join(args.out_dir, f"best_{args.source}_to_{args.target}.pt")
    wait = 0
    mse = nn.MSELoss()

    for ep in range(1, args.epochs + 1):
        t0 = time.time()
        p = min(1.0, ep / max(1, args.adv_warmup_epochs))
        # simple warm-up for adversarial signal to stabilize early training
        tr_loss, tr_ls, tr_lt, tr_adv = train_one_epoch(model, train_s, train_t, optimizer, device, args.lambda_adv, adv_alpha=p)

        model.eval()
        val_losses = []
        with torch.no_grad():
            for xt, yt in val_t:
                xt, yt = xt.to(device), yt.to(device)
                _, ytp, _ = model(None, xt, only_target=True)
                val_losses.append(mse(ytp, yt).item())
        val_loss = float(np.mean(val_losses)) if len(val_losses) > 0 else tr_loss
        dt = time.time() - t0

        print(f"Epoch {ep:03d} | train_loss={tr_loss:.6f} (Ls={tr_ls:.4f}, Lt={tr_lt:.4f}, Adv={tr_adv:.4f}, p={p:.2f}) | target_val_mse={val_loss:.6f} | time={dt:.1f}s")

        if val_loss < best_val - 1e-6:
            best_val = val_loss
            wait = 0
            torch.save(model.state_dict(), best_path)
        else:
            wait += 1
            if wait >= args.patience:
                print(f"[EarlyStop] best target_val_mse={best_val:.6f}")
                break

    model.load_state_dict(torch.load(best_path, map_location=device))
    if args.mape_min_denom is None:
        # heuristic: flow has many small values; use larger mask threshold
        mape_min_denom = 5.0 if args.task_type == 'flow' else 1.0
    else:
        mape_min_denom = float(args.mape_min_denom)

    metrics = eval_target(model, test_t, device, scaler_t, out_len=args.out_len, mape_min_denom=mape_min_denom)

    eff = measure_inference_and_memory(model, test_t, device)

    row = {
        "model": "D2MHyper",
        "task_type": args.task_type,
        "source": args.source,
        "target": args.target,

        "MAE_15": metrics["15min"]["MAE"],
        "RMSE_15": metrics["15min"]["RMSE"],
        "MAPE_15": metrics["15min"]["MAPE"],

        "MAE_30": metrics["30min"]["MAE"],
        "RMSE_30": metrics["30min"]["RMSE"],
        "MAPE_30": metrics["30min"]["MAPE"],

        "MAE_60": metrics["60min"]["MAE"],
        "RMSE_60": metrics["60min"]["RMSE"],
        "MAPE_60": metrics["60min"]["MAPE"],

        "MAE_avg": metrics["avg"]["MAE"],
        "RMSE_avg": metrics["avg"]["RMSE"],
        "MAPE_avg": metrics["avg"]["MAPE"],

        "trainable_params": trainable_params,
        "peak_gpu_gb": eff["peak_gpu_gb"],
        "infer_total_s": eff["infer_total_s"],
        "num_batches": eff["num_batches"],
        "num_samples": eff["num_samples"],
        "latency_ms_per_batch": eff["latency_ms_per_batch"],
        "latency_ms_per_sample": eff["latency_ms_per_sample"],
    }
    append_to_csv(args.results_csv, row)

    print("\n================ TEST RESULT (Target) ================")
    for k in ["15min", "30min", "60min", "avg"]:
        v = metrics[k]
        print(f"{k:5s} | MAE {v['MAE']:.4f} RMSE {v['RMSE']:.4f} MAPE {v['MAPE']:.4f}")
    print("======================================================")

    print("\n================ TRAINING RESOURCE ===================")
    print(f"Model size (trainable params): {trainable_params:,}")
    print(f"Peak GPU memory usage (GB)   : {eff['peak_gpu_gb']:.4f}")
    print("======================================================")

    print("\n================ INFERENCE TIME =======================")
    print(f"Total forward time (s): {eff['infer_total_s']:.4f}")
    print(f"Num batches           : {eff['num_batches']}")
    print(f"Num samples           : {eff['num_samples']}")
    print(f"Mean latency (ms/b)   : {eff['latency_ms_per_batch']:.4f}")
    print(f"Mean latency (ms/x)   : {eff['latency_ms_per_sample']:.6f}")
    print("======================================================")

    print(f"\n[Saved] {args.results_csv}")
    print(f"[Saved] best checkpoint: {best_path}")

if __name__ == "__main__":
    main()
