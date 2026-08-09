#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    paper = json.loads((root / "paper_results.json").read_text())
    summary = json.loads((Path(a.run_dir) / "summary.json").read_text())
    task = summary["task"].upper().replace("SZ-TAXI", "SZ-TAXI")
    # canonical task strings in summary already match except casing of SZ-TAXI.
    key = next((k for k in paper if k.upper() == task), None)
    if key is None:
        raise KeyError(f"No paper result stored for task {summary['task']}")
    print("Task:", key)
    print("metric         reproduced      paper       delta")
    for h in ["15min", "30min", "60min", "Average"]:
        for metric in ["MAE", "RMSE", "MAPE"]:
            r = summary["metrics"][h][metric]
            q = paper[key][h][metric]
            print(f"{h:8s} {metric:5s}  {r:12.4f}  {q:9.4f}  {r-q:+9.4f}")


if __name__ == "__main__":
    main()
