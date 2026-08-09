import numpy as np

def _mae(y, x):
    return float(np.mean(np.abs(y - x)))

def _rmse(y, x):
    return float(np.sqrt(np.mean((y - x) ** 2)))

def _mape(y, x, min_denom=1.0, eps=1e-5, mask_zero=True):
    """MAPE (%) with robust masking for traffic data.

    Many traffic datasets (especially **flow**) contain very small/zero values
    at night or due to missingness. Vanilla MAPE explodes in those regions.

    We follow the common "masked MAPE" practice:
      - mask out |true| <= max(eps, min_denom)
      - compute mean(|pred-true|/|true|) * 100

    Args:
        min_denom: the minimum |true| allowed in denominator.
                  Typical: flow=1 or 5; speed=0.1 or 1.
    """
    denom = np.abs(x)
    thr = max(float(eps), float(min_denom))
    if mask_zero:
        m = denom > thr
        if np.sum(m) == 0:
            return float("nan")
        return float(np.mean(np.abs((y[m] - x[m]) / denom[m])) * 100.0)
    else:
        denom = np.maximum(denom, thr)
        return float(np.mean(np.abs((y - x) / denom)) * 100.0)

def compute_metrics_horizons(pred, true, out_len=12, mape_min_denom=1.0):
    """
    pred,true: (B,out,N,1) in real scale
    5-min interval: 15min=3, 30min=6, 60min=12
    avg: average over all out_len steps
    NOTE: MAPE returned in percentage (%)
    """
    assert pred.shape == true.shape
    pred = pred[..., 0]  # (B,out,N)
    true = true[..., 0]

    def at_step(k):  # 1-indexed step
        idx = k - 1
        p = pred[:, idx]
        t = true[:, idx]
        return {
            "MAE": _mae(p, t),
            "RMSE": _rmse(p, t),
            "MAPE": _mape(p, t, min_denom=mape_min_denom),
        }

    p_all = pred.reshape(-1)
    t_all = true.reshape(-1)
    avg = {
        "MAE": _mae(p_all, t_all),
        "RMSE": _rmse(p_all, t_all),
        "MAPE": _mape(p_all, t_all, min_denom=mape_min_denom),
    }

    return {
        "15min": at_step(3),
        "30min": at_step(6),
        "60min": at_step(12 if out_len >= 12 else out_len),
        "avg": avg
    }
