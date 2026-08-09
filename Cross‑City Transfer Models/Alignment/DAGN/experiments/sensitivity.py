#!/usr/bin/env python3
"""Reproduce RQ4 sweeps for d_emb, alpha, beta."""
import argparse
import subprocess
import sys
from pathlib import Path


def run_sweep(run_py, py, forwarded, key, values):
    for value in values:
        cmd = [py, run_py] + forwarded + [f"--{key}", str(value)]
        print("\n>>>", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--python", default=sys.executable)
    p.add_argument("--sweep", choices=["emb_dim", "alpha", "beta"], required=True)
    p.add_argument("args", nargs=argparse.REMAINDER)
    a = p.parse_args()
    forwarded = a.args[1:] if a.args and a.args[0] == "--" else a.args
    run_py = str(Path(__file__).resolve().parents[1] / "run.py")
    values = {
        "emb_dim": [4, 8, 16, 32, 64],
        "alpha": [0.3, 0.5, 0.8, 1.0, 1.5],
        "beta": [1, 2, 3, 4, 5],
    }[a.sweep]
    run_sweep(run_py, a.python, forwarded, a.sweep, values)


if __name__ == "__main__":
    main()
