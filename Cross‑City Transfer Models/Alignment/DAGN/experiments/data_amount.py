#!/usr/bin/env python3
"""Reproduce the RQ3 target-data amount study (3/10/30 days)."""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--python", default=sys.executable)
    p.add_argument("--days", nargs="+", type=int, default=[3, 10, 30])
    p.add_argument("args", nargs=argparse.REMAINDER)
    a = p.parse_args()
    forwarded = a.args[1:] if a.args and a.args[0] == "--" else a.args
    run_py = str(Path(__file__).resolve().parents[1] / "run.py")
    for d in a.days:
        cmd = [a.python, run_py] + forwarded + ["--target_train_days", str(d)]
        print("\n>>>", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
