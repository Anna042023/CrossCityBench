from __future__ import annotations

import numpy as np


def mae(y_true, y_pred):
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true, y_pred, threshold: float = 1e-5, mode: str = "mask"):
    if mode == "legacy":
        return float(np.mean(np.abs(y_pred - y_true) / (np.abs(y_true) + 1e-5)) * 100.0)
    mask = np.isfinite(y_true) & np.isfinite(y_pred) & (np.abs(y_true) > threshold)
    if not np.any(mask):
        return float("nan")
    return float(np.mean(np.abs(y_pred[mask] - y_true[mask]) / np.abs(y_true[mask])) * 100.0)


def metric_dict(y_true, y_pred, mape_threshold: float = 1e-5, mape_mode: str = "mask"):
    return {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "MAPE": mape(y_true, y_pred, threshold=mape_threshold, mode=mape_mode),
    }


def horizon_report(y_true, y_pred, horizon_steps=(3, 6, 12), mape_threshold=1e-5, mape_mode="mask"):
    """y_true/y_pred: [samples, horizon, nodes]. Average is over all forecast steps."""
    out = {}
    for h in horizon_steps:
        idx = h - 1
        if idx >= y_true.shape[1]:
            continue
        out[str(h)] = metric_dict(y_true[:, idx], y_pred[:, idx], mape_threshold, mape_mode)
    out["Average"] = metric_dict(y_true, y_pred, mape_threshold, mape_mode)
    return out
