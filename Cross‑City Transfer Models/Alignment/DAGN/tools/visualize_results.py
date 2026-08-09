#!/usr/bin/env python3
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run_dir", required=True)
    p.add_argument("--sensor", type=int, default=0)
    p.add_argument("--sample", type=int, default=0)
    a = p.parse_args()
    d = Path(a.run_dir)

    pred_path = d / "predictions.npz"
    if pred_path.exists():
        z = np.load(pred_path)
        yt, yp = z["y_true"], z["y_pred"]
        s = min(a.sensor, yt.shape[1] - 1)
        i = min(a.sample, yt.shape[0] - 1)
        plt.figure(figsize=(7, 3.5))
        plt.plot(yt[i, s, :, 0], marker="o", label="Ground Truth")
        plt.plot(yp[i, s, :, 0], marker="s", label="DAGN")
        plt.xlabel("Prediction Step")
        plt.ylabel("Traffic State")
        plt.legend()
        plt.tight_layout()
        out = d / f"prediction_sensor{s}_sample{i}.png"
        plt.savefig(out, dpi=200)
        plt.close()
        print("saved", out)

    struct_path = d / "learned_structures.npz"
    if struct_path.exists():
        z = np.load(struct_path)
        if "theta_cross_city" in z:
            theta = z["theta_cross_city"]
            plt.figure(figsize=(8, 5))
            plt.imshow(theta, aspect="auto", interpolation="nearest")
            plt.colorbar(label="Cross-city Probability")
            plt.xlabel("Source Node")
            plt.ylabel("Target Node")
            plt.tight_layout()
            out = d / "cross_city_probability.png"
            plt.savefig(out, dpi=200)
            plt.close()
            print("saved", out)

        if "attention_target" in z:
            attn = z["attention_target"]
            # first batch item: [N,T] -> show T x N for readability
            mat = attn[0].T
            plt.figure(figsize=(8, 4))
            plt.imshow(mat, aspect="auto", interpolation="nearest")
            plt.colorbar(label="Attention")
            plt.xlabel("Target Node")
            plt.ylabel("Time Step")
            plt.tight_layout()
            out = d / "target_attention.png"
            plt.savefig(out, dpi=200)
            plt.close()
            print("saved", out)


if __name__ == "__main__":
    main()
