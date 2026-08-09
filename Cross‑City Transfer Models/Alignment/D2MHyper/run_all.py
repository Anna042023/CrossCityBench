import os
import argparse
import subprocess
from utils import ensure_dir

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", type=str, default="/home/zc/wanganna/")
    parser.add_argument("--out_dir", type=str, default="./outputs")
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)

    # 论文设置
    parser.add_argument("--in_len", type=int, default=12)
    parser.add_argument("--out_len", type=int, default=12)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--hidden_dim", type=int, default=64)
    parser.add_argument("--heads", type=int, default=4)  # 64 可被 4 整除（更合理）
    parser.add_argument("--hyperedges", type=str, default="20,80,200")
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--lambda_adv", type=float, default=1.0)

    # 邻接构造（仅对 PEMS03/08 的 csv 边表有效）
    parser.add_argument("--epsilon_percentile", type=float, default=0.10)
    parser.add_argument("--epsilon_value", type=float, default=None)

    args = parser.parse_args()
    ensure_dir(args.out_dir)

    tasks = [
        ("PEMS03", "PEMS08", "flow"),
        ("PEMS-BAY", "METR-LA", "speed"),
    ]

    results_csv = os.path.join(args.out_dir, "d2mhyper_results.csv")
    if os.path.exists(results_csv):
        os.remove(results_csv)

    for src, tgt, task_type in tasks:
        cmd = [
            "python", "train_one_task.py",
            "--data_root", args.data_root,
            "--source", src,
            "--target", tgt,
            "--task_type", task_type,
            "--out_dir", args.out_dir,
            "--results_csv", results_csv,
            "--gpu", str(args.gpu),
            "--seed", str(args.seed),
            "--in_len", str(args.in_len),
            "--out_len", str(args.out_len),
            "--batch_size", str(args.batch_size),
            "--hidden_dim", str(args.hidden_dim),
            "--heads", str(args.heads),
            "--hyperedges", args.hyperedges,
            "--lr", str(args.lr),
            "--epochs", str(args.epochs),
            "--patience", str(args.patience),
            "--lambda_adv", str(args.lambda_adv),
            "--epsilon_percentile", str(args.epsilon_percentile),
        ]
        if args.epsilon_value is not None:
            cmd += ["--epsilon_value", str(args.epsilon_value)]

        print("\n==============================")
        print(f"Running task: {src} -> {tgt} ({task_type})")
        print("==============================\n")
        subprocess.check_call(cmd)

    print("\nAll tasks done.")
    print(f"Saved CSV: {results_csv}")

if __name__ == "__main__":
    main()
