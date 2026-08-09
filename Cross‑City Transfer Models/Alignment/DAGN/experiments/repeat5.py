#!/usr/bin/env python3
"""Run five independent seeds, matching the paper's five-run reporting protocol."""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--python", default=sys.executable)
    p.add_argument("--seeds", nargs="+", type=int, default=[2023, 2024, 2025, 2026, 2027])
    p.add_argument("args", nargs=argparse.REMAINDER)
    a = p.parse_args()
    forwarded = a.args[1:] if a.args and a.args[0] == "--" else a.args
    run_py = str(Path(__file__).resolve().parents[1] / "run.py")
    for seed in a.seeds:
        cmd = [a.python, run_py] + forwarded + ["--seed", str(seed)]
        print("\n>>>", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
