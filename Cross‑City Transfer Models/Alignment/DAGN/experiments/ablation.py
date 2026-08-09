#!/usr/bin/env python3
"""Run the Table-6 ablation variants: M1, M2, M3a, M3b, M4a, M4b, full."""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--python", default=sys.executable)
    p.add_argument("--variants", nargs="+", default=["M1", "M2", "M3a", "M3b", "M4a", "M4b", "full"])
    p.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to run.py after --")
    a = p.parse_args()
    forwarded = a.args[1:] if a.args and a.args[0] == "--" else a.args
    run_py = str(Path(__file__).resolve().parents[1] / "run.py")
    for v in a.variants:
        cmd = [a.python, run_py] + forwarded + ["--variant", v]
        print("\n>>>", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
