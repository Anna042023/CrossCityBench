# train.py
import argparse
import gc
import json
import os
import time
from datetime import datetime

import numpy as np
import torch

from data_loader import get_dataloaders
from model import FGITrans
from utils import get_metric_functions  # 指标函数入口


def generate_time_features(seq_len, batch_size, start_idx=0):
    """
    tod: [B, T] in [0, 287]
    dow: [B, T] in [0, 6]
    """
    tod = (torch.arange(start_idx, start_idx + seq_len) % 288).long()
    dow = (torch.arange(start_idx, start_idx + seq_len) // 288 % 7).long()
    tod = tod.unsqueeze(0).expand(batch_size, -1)
    dow = dow.unsqueeze(0).expand(batch_size, -1)
    return tod, dow


def evaluate(model, test_loader, device, dataset, horizons=(3, 6, 12), source_dataset=None, target_dataset=None):
    """
    输出：horizons对应(3,6,12) -> (15/30/60min) + average
    """
    model.eval()
    results = {h: {"mae": [], "rmse": [], "mape": []} for h in horizons}

    mae_func, rmse_func, mape_func = get_metric_functions(source_dataset, target_dataset)

    mean_val = torch.tensor(dataset.mean_val, dtype=torch.float32).to(device)
    std_val = torch.tensor(dataset.std_val, dtype=torch.float32).to(device)

    with torch.no_grad():
        for x, y in test_loader:
            B, T_in, N, D = x.shape
            x = x.to(device)
            y = y.to(device)

            tod, dow = generate_time_features(T_in, B, 0)
            tod = tod.to(device)
            dow = dow.to(device)

            outputs = model(None, x, tod, dow)
            pred = outputs["tgt_pred"]  # [B, T_out, N, 1]

            # 反归一化
            pred_denorm = pred * std_val + mean_val
            y_denorm = y * std_val + mean_val

            for h in horizons:
                if h <= pred_denorm.shape[1]:
                    y_h = y_denorm[:, h - 1 : h]      # [B, 1, N, 1]
                    pred_h = pred_denorm[:, h - 1 : h]

                    mae = mae_func(pred_h, y_h).item()
                    rmse = rmse_func(pred_h, y_h).item()
                    mape = mape_func(pred_h, y_h).item()

                    # 过滤极端异常
                    if np.isfinite(mape) and mape < 1000:
                        results[h]["mae"].append(mae)
                        results[h]["rmse"].append(rmse)
                        results[h]["mape"].append(mape)

    final_results = {}
    for h in horizons:
        if results[h]["mae"]:
            final_results[h] = {
                "MAE": float(np.mean(results[h]["mae"])),
                "RMSE": float(np.mean(results[h]["rmse"])),
                "MAPE": float(np.mean(results[h]["mape"])),
            }
        else:
            final_results[h] = {"MAE": 0.0, "RMSE": 0.0, "MAPE": 0.0}

    valid_h = [h for h in horizons if results[h]["mae"]]
    if valid_h:
        avg_mae = float(np.mean([final_results[h]["MAE"] for h in valid_h]))
        avg_rmse = float(np.mean([final_results[h]["RMSE"] for h in valid_h]))
        avg_mape = float(np.mean([final_results[h]["MAPE"] for h in valid_h]))
    else:
        avg_mae = avg_rmse = avg_mape = 0.0

    final_results["average"] = {"MAE": avg_mae, "RMSE": avg_rmse, "MAPE": avg_mape}
    return final_results


def _count_trainable_params(model: torch.nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def _gpu_peak_gb() -> float:
    """
    返回 CUDA peak allocated memory (GB). 若无GPU则返回0。
    """
    if not torch.cuda.is_available():
        return 0.0
    peak_bytes = torch.cuda.max_memory_allocated()
    return float(peak_bytes / (1024 ** 3))


def measure_inference_time(
    model,
    test_loader,
    device,
    input_len: int,
    warmup_batches: int = 5,
    max_batches: int = None,
):
    """
    统计与你截图一致的推理指标：
    - Total forward time (s)
    - Num batches
    - Num samples
    - Mean latency (ms/b)
    - Mean latency (ms/x)
    """
    model.eval()

    def _sync():
        if device.type == "cuda":
            torch.cuda.synchronize()

    total_time = 0.0
    num_batches = 0
    num_samples = 0

    with torch.no_grad():
        # warmup（不计时）
        w = 0
        for x, _ in test_loader:
            if w >= warmup_batches:
                break
            B = x.size(0)
            x = x.to(device)
            tod, dow = generate_time_features(input_len, B, 0)
            tod = tod.to(device)
            dow = dow.to(device)
            _ = model(None, x, tod, dow)
            w += 1
        _sync()

        # timed
        for x, _ in test_loader:
            if max_batches is not None and num_batches >= max_batches:
                break

            B = x.size(0)
            x = x.to(device)
            tod, dow = generate_time_features(input_len, B, 0)
            tod = tod.to(device)
            dow = dow.to(device)

            _sync()
            t0 = time.time()
            _ = model(None, x, tod, dow)
            _sync()
            t1 = time.time()

            total_time += (t1 - t0)
            num_batches += 1
            num_samples += B

    if num_batches == 0:
        ms_per_batch = 0.0
    else:
        ms_per_batch = total_time / num_batches * 1000.0

    if num_samples == 0:
        ms_per_sample = 0.0
    else:
        ms_per_sample = total_time / num_samples * 1000.0

    return {
        "total_forward_time_s": float(total_time),
        "num_batches": int(num_batches),
        "num_samples": int(num_samples),
        "mean_latency_ms_per_batch": float(ms_per_batch),
        "mean_latency_ms_per_sample": float(ms_per_sample),
    }


def save_report_txt(path, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def append_pareto_csv(csv_path: str, row: dict):
    """
    追加保存一行，用于帕累托实验：后续你可以用这个csv画 MAE vs latency / memory / params 等。
    """
    import csv

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    file_exists = os.path.exists(csv_path)

    # 固定列顺序（方便你画图）
    fieldnames = [
        "timestamp",
        "source",
        "target",
        "epochs",
        "batch_size",
        "lr",
        "d_model",
        "num_layers",
        "trainable_params",
        "peak_gpu_memory_gb",
        "infer_total_forward_time_s",
        "infer_num_batches",
        "infer_num_samples",
        "infer_mean_latency_ms_per_batch",
        "infer_mean_latency_ms_per_sample",
        "mae_15",
        "rmse_15",
        "mape_15",
        "mae_30",
        "rmse_30",
        "mape_30",
        "mae_60",
        "rmse_60",
        "mape_60",
        "mae_avg",
        "rmse_avg",
        "mape_avg",
    ]

    # 补齐缺失键
    out = {k: row.get(k, "") for k in fieldnames}

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True)
    parser.add_argument("--target", type=str, required=True)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--save_dir", type=str, default="./checkpoints")
    parser.add_argument("--d_model", type=int, default=64)
    parser.add_argument("--num_layers", type=int, default=2)

    # 推理统计相关（帕累托实验常用：为了更快拿点）
    parser.add_argument("--infer_warmup", type=int, default=5, help="warmup batches for inference timing")
    parser.add_argument("--infer_max_batches", type=int, default=None, help="limit timed batches for inference timing")

    args = parser.parse_args()
    os.makedirs(args.save_dir, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_len = 12

    print("Loading data...")
    src_loader, tgt_loader, test_loader, src_nodes, tgt_nodes, src_dim, tgt_dim = get_dataloaders(
        args.source,
        args.target,
        data_root="/home/zc/wanganna/",
        input_len=input_len,
        batch_size=args.batch_size,
    )

    print(f"Data info - Source Nodes: {src_nodes}, Target Nodes: {tgt_nodes}, Src Dim: {src_dim}, Tgt Dim: {tgt_dim}")
    test_dataset = test_loader.dataset

    # 建模
    model = FGITrans(
        src_nodes=src_nodes,
        tgt_nodes=tgt_nodes,
        src_input_dim=src_dim,
        tgt_input_dim=tgt_dim,
        d_model=args.d_model,
        n_heads=4,
        num_layers=args.num_layers,
        da=16,
        dropout=0.1,
        delta=1.0,
        temp=2.0,
        alpha=0.1,
        beta=0.5,
        sigma=1.0,
    ).to(device)

    trainable_params = _count_trainable_params(model)
    print(f"Model parameters: {trainable_params:,}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    best_mae = float("inf")
    best_rmse = float("inf")
    best_mape = float("inf")

    print(f"\nTraining: {args.source} → {args.target}")
    print(f"Epochs: {args.epochs}, Batch Size: {args.batch_size}, Learning Rate: {args.lr}")
    print(f"Model Config - d_model: {args.d_model}, num_layers: {args.num_layers}")
    print("=" * 80)

    # checkpoint
    model_path = os.path.join(args.save_dir, f"fgitrans_{args.source}_to_{args.target}_best.pth")
    start_epoch = 0
    if os.path.exists(model_path):
        try:
            checkpoint = torch.load(model_path, map_location=device, weights_only=False)
            model.load_state_dict(checkpoint["model_state_dict"])
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            start_epoch = int(checkpoint["epoch"])
            best_mae = float(checkpoint["best_mae"])
            best_rmse = float(checkpoint["best_rmse"])
            best_mape = float(checkpoint["best_mape"])
            print(f"Resuming training from epoch {start_epoch}")
            print(f"Previous best - MAE: {best_mae:.2f}, RMSE: {best_rmse:.2f}, MAPE: {best_mape:.2f}%")
        except Exception as e:
            print(f"Could not load checkpoint: {e}")
            print("Starting training from scratch")

    # 资源统计：GPU peak（训练过程）
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    accumulation_steps = 2

    for epoch in range(start_epoch, args.epochs):
        model.train()
        total_loss = 0.0
        num_batches = 0
        epoch_start_time = time.time()

        src_iter = iter(src_loader)
        tgt_iter = iter(tgt_loader)
        optimizer.zero_grad(set_to_none=True)

        for i in range(min(len(src_loader), len(tgt_loader))):
            try:
                src_x, src_y = next(src_iter)
                tgt_x, tgt_y = next(tgt_iter)
            except StopIteration:
                break

            B = src_x.size(0)
            src_x = src_x.to(device)
            src_y = src_y.to(device)
            tgt_x = tgt_x.to(device)
            tgt_y = tgt_y.to(device)

            start_idx = i * args.batch_size
            tod, dow = generate_time_features(input_len, B, start_idx)
            tod = tod.to(device)
            dow = dow.to(device)

            outputs = model(src_x, tgt_x, tod, dow)
            loss, _ = model.compute_losses(outputs, src_y, tgt_y)

            loss = loss / accumulation_steps
            loss.backward()

            if (i + 1) % accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)

            total_loss += float(loss.item()) * accumulation_steps
            num_batches += 1

            if i % 100 == 0 and torch.cuda.is_available():
                torch.cuda.empty_cache()

        scheduler.step()

        epoch_time = time.time() - epoch_start_time
        avg_loss = total_loss / max(1, num_batches)
        current_lr = optimizer.param_groups[0]["lr"]

        print(
            f"Epoch {epoch + 1:3d}/{args.epochs} | Time: {epoch_time:5.2f}s | "
            f"Loss: {avg_loss:.4f} | LR: {current_lr:.6f}",
            end="",
        )

        # eval
        if (epoch + 1) % 5 == 0 or (epoch + 1) == args.epochs:
            results = evaluate(
                model,
                test_loader,
                device,
                test_dataset,
                horizons=(3, 6, 12),
                source_dataset=args.source,
                target_dataset=args.target,
            )
            avg_mae = results["average"]["MAE"]
            avg_rmse = results["average"]["RMSE"]
            avg_mape = results["average"]["MAPE"]
            print(f" | Test - MAE: {avg_mae:.2f}, RMSE: {avg_rmse:.2f}, MAPE: {avg_mape:.2f}%", end="")

            # Trend check
            horizon_trend = [results[h]["MAE"] for h in (3, 6, 12) if h in results]
            if len(horizon_trend) == 3:
                trend = "✓" if horizon_trend[0] < horizon_trend[1] < horizon_trend[2] else "✗"
                print(f" | Trend: {trend}", end="")

            # save best
            if avg_mae < best_mae and avg_mape < 50:
                best_mae, best_rmse, best_mape = float(avg_mae), float(avg_rmse), float(avg_mape)
                torch.save(
                    {
                        "epoch": epoch + 1,
                        "model_state_dict": model.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                        "best_mae": best_mae,
                        "best_rmse": best_rmse,
                        "best_mape": best_mape,
                        "config": {
                            "src_nodes": src_nodes,
                            "tgt_nodes": tgt_nodes,
                            "src_input_dim": src_dim,
                            "tgt_input_dim": tgt_dim,
                            "d_model": args.d_model,
                            "num_layers": args.num_layers,
                        },
                    },
                    model_path,
                )
                print(" ✅", end="")

        print()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # load best for final
    if os.path.exists(model_path):
        try:
            checkpoint = torch.load(model_path, map_location=device, weights_only=False)
            model.load_state_dict(checkpoint["model_state_dict"])
            print(f"\nLoaded best model from epoch {checkpoint['epoch']}")
            print(
                f"Best metrics - MAE: {checkpoint['best_mae']:.2f}, "
                f"RMSE: {checkpoint['best_rmse']:.2f}, MAPE: {checkpoint['best_mape']:.2f}%"
            )
        except Exception as e:
            print(f"Error loading best model: {e}")
            print("Using last model for evaluation")
    else:
        print("\nBest model not found, using last model")

    # final metrics
    final_results = evaluate(
        model,
        test_loader,
        device,
        test_dataset,
        horizons=(3, 6, 12),
        source_dataset=args.source,
        target_dataset=args.target,
    )

    # ====== TRAINING RESOURCE (与你图一致) ======
    peak_gpu_gb = _gpu_peak_gb()

    # ====== INFERENCE TIME (与你图一致) ======
    infer_stats = measure_inference_time(
        model=model,
        test_loader=test_loader,
        device=device,
        input_len=input_len,
        warmup_batches=args.infer_warmup,
        max_batches=args.infer_max_batches,
    )

    # ====== 打印结果（格式对齐截图） ======
    # horizons=3,6,12 对应 15/30/60 min
    h_map = {3: "15min", 6: "30min", 12: "60min"}
    print("\n" + "=" * 22 + " TEST RESULT (Target) " + "=" * 22)
    for h in (3, 6, 12):
        r = final_results.get(h, {"MAE": 0, "RMSE": 0, "MAPE": 0})
        print(
            f"{h_map[h]:<5} |  MAE {r['MAE']:.4f}  RMSE {r['RMSE']:.4f}  MAPE {r['MAPE']:.4f}"
        )
    r = final_results["average"]
    print(f"{'avg':<5} |  MAE {r['MAE']:.4f}  RMSE {r['RMSE']:.4f}  MAPE {r['MAPE']:.4f}")
    print("=" * 70)

    print("\n" + "=" * 22 + " TRAINING RESOURCE " + "=" * 22)
    print(f"Model size (trainable params): {trainable_params:,}")
    print(f"Peak GPU memory usage (GB)    : {peak_gpu_gb:.4f}")
    print("=" * 70)

    print("\n" + "=" * 24 + " INFERENCE TIME " + "=" * 24)
    print(f"Total forward time (s): {infer_stats['total_forward_time_s']:.4f}")
    print(f"Num batches           : {infer_stats['num_batches']}")
    print(f"Num samples           : {infer_stats['num_samples']}")
    print(f"Mean latency (ms/b)   : {infer_stats['mean_latency_ms_per_batch']:.4f}")
    print(f"Mean latency (ms/x)   : {infer_stats['mean_latency_ms_per_sample']:.6f}")
    print("=" * 70)

    # ====== 保存最终模型 ======
    final_model_path = os.path.join(args.save_dir, f"fgitrans_{args.source}_to_{args.target}_final.pth")
    torch.save({"model_state_dict": model.state_dict(), "final_metrics": final_results["average"]}, final_model_path)

    # ====== 保存 report.txt / metrics.json ======
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = []
    report_lines.append("=" * 22 + " TEST RESULT (Target) " + "=" * 22)
    for h in (3, 6, 12):
        rr = final_results.get(h, {"MAE": 0, "RMSE": 0, "MAPE": 0})
        report_lines.append(
            f"{h_map[h]:<5} |  MAE {rr['MAE']:.4f}  RMSE {rr['RMSE']:.4f}  MAPE {rr['MAPE']:.4f}"
        )
    rr = final_results["average"]
    report_lines.append(f"{'avg':<5} |  MAE {rr['MAE']:.4f}  RMSE {rr['RMSE']:.4f}  MAPE {rr['MAPE']:.4f}")
    report_lines.append("=" * 70)
    report_lines.append("")
    report_lines.append("=" * 22 + " TRAINING RESOURCE " + "=" * 22)
    report_lines.append(f"Model size (trainable params): {trainable_params:,}")
    report_lines.append(f"Peak GPU memory usage (GB)    : {peak_gpu_gb:.4f}")
    report_lines.append("=" * 70)
    report_lines.append("")
    report_lines.append("=" * 24 + " INFERENCE TIME " + "=" * 24)
    report_lines.append(f"Total forward time (s): {infer_stats['total_forward_time_s']:.4f}")
    report_lines.append(f"Num batches           : {infer_stats['num_batches']}")
    report_lines.append(f"Num samples           : {infer_stats['num_samples']}")
    report_lines.append(f"Mean latency (ms/b)   : {infer_stats['mean_latency_ms_per_batch']:.4f}")
    report_lines.append(f"Mean latency (ms/x)   : {infer_stats['mean_latency_ms_per_sample']:.6f}")
    report_lines.append("=" * 70)
    report_lines.append("")
    report_lines.append(f"[Saved model] {final_model_path}")
    report_lines.append(f"[Timestamp ] {timestamp}")

    report_txt_path = os.path.join(args.save_dir, f"fgitrans_{args.source}_to_{args.target}_report.txt")
    save_report_txt(report_txt_path, "\n".join(report_lines))

    metrics_json = {
        "timestamp": timestamp,
        "source": args.source,
        "target": args.target,
        "trainable_params": trainable_params,
        "peak_gpu_memory_gb": peak_gpu_gb,
        "final_results": final_results,
        "inference": infer_stats,
        "config": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "d_model": args.d_model,
            "num_layers": args.num_layers,
        },
    }
    json_path = os.path.join(args.save_dir, f"fgitrans_{args.source}_to_{args.target}_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_json, f, ensure_ascii=False, indent=2)

    # ====== 追加保存：pareto_results.csv ======
    # 把 3/6/12 对应的指标展开成列（更适合画帕累托）
    r15 = final_results.get(3, {"MAE": 0, "RMSE": 0, "MAPE": 0})
    r30 = final_results.get(6, {"MAE": 0, "RMSE": 0, "MAPE": 0})
    r60 = final_results.get(12, {"MAE": 0, "RMSE": 0, "MAPE": 0})
    ravg = final_results["average"]

    pareto_row = {
        "timestamp": timestamp,
        "source": args.source,
        "target": args.target,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "lr": args.lr,
        "d_model": args.d_model,
        "num_layers": args.num_layers,
        "trainable_params": trainable_params,
        "peak_gpu_memory_gb": peak_gpu_gb,
        "infer_total_forward_time_s": infer_stats["total_forward_time_s"],
        "infer_num_batches": infer_stats["num_batches"],
        "infer_num_samples": infer_stats["num_samples"],
        "infer_mean_latency_ms_per_batch": infer_stats["mean_latency_ms_per_batch"],
        "infer_mean_latency_ms_per_sample": infer_stats["mean_latency_ms_per_sample"],
        "mae_15": r15["MAE"],
        "rmse_15": r15["RMSE"],
        "mape_15": r15["MAPE"],
        "mae_30": r30["MAE"],
        "rmse_30": r30["RMSE"],
        "mape_30": r30["MAPE"],
        "mae_60": r60["MAE"],
        "rmse_60": r60["RMSE"],
        "mape_60": r60["MAPE"],
        "mae_avg": ravg["MAE"],
        "rmse_avg": ravg["RMSE"],
        "mape_avg": ravg["MAPE"],
    }

    pareto_csv_path = os.path.join(args.save_dir, "pareto_results.csv")
    append_pareto_csv(pareto_csv_path, pareto_row)

    print(f"\n[Saved] report txt : {report_txt_path}")
    print(f"[Saved] metrics json: {json_path}")
    print(f"[Saved] pareto csv  : {pareto_csv_path}")
    print(f"[Saved] final model : {final_model_path}")


if __name__ == "__main__":
    main()
