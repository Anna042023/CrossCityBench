import numpy as np


def _mask(y_true, y_pred):
    return np.isfinite(y_true) & np.isfinite(y_pred)


def mae(y_true, y_pred):
    m = _mask(y_true, y_pred)
    return float(np.mean(np.abs(y_true[m] - y_pred[m]))) if m.any() else float("nan")


def rmse(y_true, y_pred):
    m = _mask(y_true, y_pred)
    return float(np.sqrt(np.mean((y_true[m] - y_pred[m]) ** 2))) if m.any() else float("nan")


def mape(y_true, y_pred, threshold=1e-5):
    m = _mask(y_true, y_pred) & (np.abs(y_true) > threshold)
    if not m.any():
        return float("nan")
    return float(np.mean(np.abs((y_true[m] - y_pred[m]) / y_true[m])) * 100.0)


def metric_dict(y_true, y_pred, mape_threshold=1e-5):
    return {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "MAPE": mape(y_true, y_pred, mape_threshold),
    }


def horizon_metrics(y_true, y_pred, interval_minutes=5, mape_threshold=1e-5):
    """
    y_true/y_pred: [samples, nodes, horizon, channels]

    The paper reports 15/30/60 min and an Average over the complete
    one-hour prediction horizon. For 5-min data these are steps 3/6/12;
    for 15-min data these are steps 1/2/4.
    """
    horizon = y_true.shape[2]
    requested = [15, 30, 60]
    out = {}
    for minutes in requested:
        step = minutes // interval_minutes
        if step < 1 or step > horizon:
            continue
        out[f"{minutes}min"] = metric_dict(
            y_true[:, :, step - 1 : step, :],
            y_pred[:, :, step - 1 : step, :],
            mape_threshold,
        )
    out["Average"] = metric_dict(y_true, y_pred, mape_threshold)
    return out
