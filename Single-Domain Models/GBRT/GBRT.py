import os
import json
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

warnings.filterwarnings("ignore")


# ============================================================
# 1. 随机种子
# ============================================================
def set_seed(seed: int = 2026):
    np.random.seed(seed)


# ============================================================
# 2. 数据读取
# ============================================================
def load_traffic_data(path, feature_idx=0, npz_key=None):
    """
    返回：
        data: np.ndarray, shape = [T, N]
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"数据文件不存在: {path}")

    suffix = path.suffix.lower()

    if suffix == ".npz":
        obj = np.load(path, allow_pickle=True)

        if npz_key is not None:
            if npz_key not in obj.files:
                raise KeyError(
                    f"指定的 npz_key='{npz_key}' 不存在。"
                    f"可用 key: {obj.files}"
                )
            arr = obj[npz_key]
        else:
            # 优先寻找交通数据常用 key
            preferred_keys = ["data", "x", "flow", "speed", "values"]
            key = None
            for k in preferred_keys:
                if k in obj.files:
                    key = k
                    break

            if key is None:
                key = obj.files[0]

            print(f"[Data] NPZ keys = {obj.files}")
            print(f"[Data] 自动使用 key = '{key}'")
            arr = obj[key]

    elif suffix == ".npy":
        arr = np.load(path, allow_pickle=True)

    elif suffix == ".csv":
        df = pd.read_csv(path)

        # 删除可能的时间列
        non_numeric = [
            c for c in df.columns
            if not pd.api.types.is_numeric_dtype(df[c])
        ]
        if non_numeric:
            print(f"[Data] 忽略非数值列: {non_numeric}")
            df = df.drop(columns=non_numeric)

        arr = df.values

    else:
        raise ValueError(
            f"暂不支持文件格式: {suffix}，请使用 .npz / .npy / .csv"
        )

    arr = np.asarray(arr)

    print(f"[Data] 原始 shape = {arr.shape}")

    # 常见情况：[T, N, C]
    if arr.ndim == 3:
        if feature_idx >= arr.shape[-1]:
            raise ValueError(
                f"feature_idx={feature_idx} 超出最后一维大小 {arr.shape[-1]}"
            )
        arr = arr[:, :, feature_idx]

    # [T, N]
    elif arr.ndim == 2:
        pass

    # [T]
    elif arr.ndim == 1:
        arr = arr[:, None]

    else:
        raise ValueError(
            f"不支持的数据维度: {arr.ndim}，期望 [T]、[T,N] 或 [T,N,C]"
        )

    arr = arr.astype(np.float32)

    # Inf -> NaN
    arr[~np.isfinite(arr)] = np.nan

    # 用每个节点的训练时序中位数/全局中位数思想做基础缺失填补
    # 这里为了预构造样本，先使用节点中位数填补
    for n in range(arr.shape[1]):
        col = arr[:, n]
        valid = np.isfinite(col)

        if valid.any():
            median = np.nanmedian(col)
        else:
            median = 0.0

        col[~valid] = median
        arr[:, n] = col

    print(f"[Data] 使用后的 shape = {arr.shape} = [T, N]")
    print(
        f"[Data] min={arr.min():.4f}, "
        f"max={arr.max():.4f}, mean={arr.mean():.4f}"
    )

    return arr


# ============================================================
# 3. 数据切分
# ============================================================
def temporal_split(data, train_ratio=0.7, val_ratio=0.1):
    """
    严格按时间切分，避免未来信息泄漏。
    """
    T = len(data)

    train_end = int(T * train_ratio)
    val_end = int(T * (train_ratio + val_ratio))

    return train_end, val_end


# ============================================================
# 4. 特征构造
# ============================================================
def make_samples(
    data,
    history,
    horizon,
    start_t,
    end_t,
    steps_per_day=288,
    include_time_features=True,
    include_node_id=True,
):
    """
    为单个 horizon 构造监督学习样本。

    对于每个时间 t 和节点 n：
        X = [x(t-history), ..., x(t-1)]
        y = x(t+horizon-1)

    为防止切分边界的数据泄漏：
        target index 必须位于 [start_t, end_t)

    参数
    ----
    data: [T, N]
    history: 历史长度
    horizon: 预测步数
    start_t/end_t:
        约束目标值 y 所在的时间区间。
    """
    T, N = data.shape

    X_all = []
    y_all = []

    # t 表示预测起点，其第 horizon 步目标是 t+horizon-1
    min_t = max(history, start_t - horizon + 1)
    max_t = min(T - horizon + 1, end_t - horizon + 1)

    if max_t <= min_t:
        raise ValueError(
            f"无法构造样本: start={start_t}, end={end_t}, "
            f"history={history}, horizon={horizon}"
        )

    node_denominator = max(N - 1, 1)

    for t in range(min_t, max_t):
        target_t = t + horizon - 1

        if not (start_t <= target_t < end_t):
            continue

        # [history, N] -> [N, history]
        lag_features = data[t-history:t, :].T

        features = [lag_features]

        if include_time_features:
            # 如果 5min 一个时间步，则 288 steps/day
            slot = target_t % steps_per_day
            angle = 2.0 * np.pi * slot / steps_per_day

            sin_t = np.full((N, 1), np.sin(angle), dtype=np.float32)
            cos_t = np.full((N, 1), np.cos(angle), dtype=np.float32)

            # 周周期，默认每周 7 天
            week_steps = steps_per_day * 7
            week_slot = target_t % week_steps
            week_angle = 2.0 * np.pi * week_slot / week_steps

            sin_w = np.full((N, 1), np.sin(week_angle), dtype=np.float32)
            cos_w = np.full((N, 1), np.cos(week_angle), dtype=np.float32)

            features.extend([sin_t, cos_t, sin_w, cos_w])

        if include_node_id:
            # 归一化 node id，作为一个简单的空间标识
            node_ids = (
                np.arange(N, dtype=np.float32) / node_denominator
            ).reshape(-1, 1)
            features.append(node_ids)

        X_t = np.concatenate(features, axis=1)
        y_t = data[target_t, :]

        X_all.append(X_t)
        y_all.append(y_t)

    X = np.concatenate(X_all, axis=0).astype(np.float32)
    y = np.concatenate(y_all, axis=0).astype(np.float32)

    return X, y


# ============================================================
# 5. 训练集下采样
# ============================================================
def subsample_training_data(X, y, max_samples, seed=2026):
    """
    标准 GradientBoostingRegressor 在超大交通数据集上可能较慢。
    因此提供随机下采样。
    max_samples <= 0 表示使用全部训练样本。
    """
    if max_samples is None or max_samples <= 0:
        return X, y

    if len(X) <= max_samples:
        return X, y

    rng = np.random.default_rng(seed)
    ids = rng.choice(len(X), size=max_samples, replace=False)

    return X[ids], y[ids]


# ============================================================
# 6. 指标
# ============================================================
def masked_mae(y_true, y_pred):
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if mask.sum() == 0:
        return np.nan
    return np.mean(np.abs(y_true[mask] - y_pred[mask]))


def masked_rmse(y_true, y_pred):
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if mask.sum() == 0:
        return np.nan
    return np.sqrt(np.mean((y_true[mask] - y_pred[mask]) ** 2))


def masked_mape(y_true, y_pred, threshold=1e-5):
    """
    MAPE 对接近 0 的真实值极其敏感，因此过滤 |y_true| <= threshold。
    返回百分数。
    """
    mask = (
        np.isfinite(y_true)
        & np.isfinite(y_pred)
        & (np.abs(y_true) > threshold)
    )

    if mask.sum() == 0:
        return np.nan

    return (
        np.mean(
            np.abs(
                (y_true[mask] - y_pred[mask])
                / y_true[mask]
            )
        )
        * 100.0
    )


def evaluate(y_true, y_pred, mape_threshold=1e-5):
    return {
        "MAE": masked_mae(y_true, y_pred),
        "RMSE": masked_rmse(y_true, y_pred),
        "MAPE": masked_mape(
            y_true, y_pred, threshold=mape_threshold
        ),
    }


# ============================================================
# 7. GBRT 模型
# ============================================================
def build_gbrt(args):
    """
    sklearn GradientBoostingRegressor = 经典 GBRT。
    """
    return GradientBoostingRegressor(
        loss="huber" if args.loss == "huber" else "squared_error",
        learning_rate=args.learning_rate,
        n_estimators=args.n_estimators,
        subsample=args.subsample,
        criterion="friedman_mse",
        min_samples_split=args.min_samples_split,
        min_samples_leaf=args.min_samples_leaf,
        max_depth=args.max_depth,
        max_features=args.max_features,
        random_state=args.seed,
        verbose=0,
    )


# ============================================================
# 8. 主流程
# ============================================================
def run(args):
    set_seed(args.seed)

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    data = load_traffic_data(
        args.data,
        feature_idx=args.feature_idx,
        npz_key=args.npz_key,
    )

    T, N = data.shape

    train_end, val_end = temporal_split(
        data,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
    )

    print("\n" + "=" * 80)
    print("GBRT Traffic Forecasting")
    print("=" * 80)
    print(f"Data             : {args.data}")
    print(f"Time steps       : {T}")
    print(f"Nodes            : {N}")
    print(f"History          : {args.history}")
    print(f"Horizons         : {args.horizons}")
    print(
        f"Split            : train [0,{train_end}), "
        f"val [{train_end},{val_end}), "
        f"test [{val_end},{T})"
    )
    print(f"Train ratio      : {args.train_ratio}")
    print(f"Val ratio        : {args.val_ratio}")
    print(f"Estimators       : {args.n_estimators}")
    print(f"Learning rate    : {args.learning_rate}")
    print(f"Max depth        : {args.max_depth}")
    print(f"Max train samples: {args.max_train_samples}")
    print("=" * 80)

    all_results = {}
    predictions_to_save = {}

    for horizon in args.horizons:
        print("\n" + "=" * 80)
        print(f"[Horizon = {horizon}]")
        print("=" * 80)

        # ---------------------------
        # Train
        # ---------------------------
        X_train, y_train = make_samples(
            data=data,
            history=args.history,
            horizon=horizon,
            start_t=0,
            end_t=train_end,
            steps_per_day=args.steps_per_day,
            include_time_features=not args.no_time_features,
            include_node_id=not args.no_node_id,
        )

        # ---------------------------
        # Validation
        # ---------------------------
        X_val, y_val = make_samples(
            data=data,
            history=args.history,
            horizon=horizon,
            start_t=train_end,
            end_t=val_end,
            steps_per_day=args.steps_per_day,
            include_time_features=not args.no_time_features,
            include_node_id=not args.no_node_id,
        )

        # ---------------------------
        # Test
        # ---------------------------
        X_test, y_test = make_samples(
            data=data,
            history=args.history,
            horizon=horizon,
            start_t=val_end,
            end_t=T,
            steps_per_day=args.steps_per_day,
            include_time_features=not args.no_time_features,
            include_node_id=not args.no_node_id,
        )

        print(
            f"Raw samples      : "
            f"train={len(X_train)}, "
            f"val={len(X_val)}, "
            f"test={len(X_test)}"
        )
        print(f"Feature dim      : {X_train.shape[1]}")

        X_train_fit, y_train_fit = subsample_training_data(
            X_train,
            y_train,
            max_samples=args.max_train_samples,
            seed=args.seed + horizon,
        )

        print(f"Fit samples      : {len(X_train_fit)}")

        # ---------------------------
        # 模型训练
        # ---------------------------
        model = build_gbrt(args)

        print("[Train] Training GBRT ...")
        model.fit(X_train_fit, y_train_fit)

        # ---------------------------
        # 验证
        # ---------------------------
        val_pred = model.predict(X_val)
        val_metrics = evaluate(
            y_val,
            val_pred,
            mape_threshold=args.mape_threshold,
        )

        print(
            f"[VAL]  H={horizon:<2d} | "
            f"MAE={val_metrics['MAE']:.4f} | "
            f"RMSE={val_metrics['RMSE']:.4f} | "
            f"MAPE={val_metrics['MAPE']:.4f}%"
        )

        # ---------------------------
        # 测试
        # ---------------------------
        test_pred = model.predict(X_test)
        test_metrics = evaluate(
            y_test,
            test_pred,
            mape_threshold=args.mape_threshold,
        )

        print(
            f"[TEST] H={horizon:<2d} | "
            f"MAE={test_metrics['MAE']:.4f} | "
            f"RMSE={test_metrics['RMSE']:.4f} | "
            f"MAPE={test_metrics['MAPE']:.4f}%"
        )

        all_results[str(horizon)] = {
            "MAE": float(test_metrics["MAE"]),
            "RMSE": float(test_metrics["RMSE"]),
            "MAPE": float(test_metrics["MAPE"]),
        }

        predictions_to_save[f"y_true_h{horizon}"] = y_test
        predictions_to_save[f"y_pred_h{horizon}"] = test_pred.astype(
            np.float32
        )

        # 保存模型
        model_path = save_dir / f"gbrt_horizon_{horizon}.joblib"
        joblib.dump(model, model_path)
        print(f"[Save] Model -> {model_path}")

        # 释放本 horizon 大数组
        del X_train, y_train
        del X_train_fit, y_train_fit
        del X_val, y_val
        del X_test, y_test
        del val_pred, test_pred
        del model

    # ========================================================
    # Average
    # ========================================================
    maes = [all_results[str(h)]["MAE"] for h in args.horizons]
    rmses = [all_results[str(h)]["RMSE"] for h in args.horizons]
    mapes = [all_results[str(h)]["MAPE"] for h in args.horizons]

    average = {
        "MAE": float(np.mean(maes)),
        "RMSE": float(np.mean(rmses)),
        "MAPE": float(np.mean(mapes)),
    }

    all_results["Average"] = average

    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)

    for h in args.horizons:
        r = all_results[str(h)]

        if args.steps_per_day == 288:
            minute = h * 5
            label = f"{minute}min"
        else:
            label = f"H={h}"

        print(
            f"{label:<10s} | "
            f"MAE {r['MAE']:.4f} | "
            f"RMSE {r['RMSE']:.4f} | "
            f"MAPE {r['MAPE']:.4f}%"
        )

    print("-" * 80)
    print(
        f"{'Average':<10s} | "
        f"MAE {average['MAE']:.4f} | "
        f"RMSE {average['RMSE']:.4f} | "
        f"MAPE {average['MAPE']:.4f}%"
    )
    print("=" * 80)

    # 保存指标
    result_path = save_dir / "results.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 保存预测
    pred_path = save_dir / "predictions.npz"
    np.savez_compressed(pred_path, **predictions_to_save)

    print(f"[Save] Results     -> {result_path}")
    print(f"[Save] Predictions -> {pred_path}")


# ============================================================
# 9. 参数
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="GBRT for Traffic Flow Forecasting"
    )

    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="数据文件路径：npz/npy/csv",
    )
    parser.add_argument(
        "--npz_key",
        type=str,
        default=None,
        help="NPZ 中的数据 key；默认自动识别 data/x/flow/speed",
    )
    parser.add_argument(
        "--feature_idx",
        type=int,
        default=0,
        help="对于 [T,N,C] 数据选择哪个通道，默认 0",
    )

    parser.add_argument(
        "--history",
        type=int,
        default=12,
        help="历史输入长度，默认 12",
    )
    parser.add_argument(
        "--horizons",
        type=int,
        nargs="+",
        default=[3, 6, 12],
        help="预测 Horizon，例如 3 6 12",
    )
    parser.add_argument(
        "--steps_per_day",
        type=int,
        default=288,
        help="每天时间步数，5min 数据默认 288",
    )

    parser.add_argument(
        "--train_ratio",
        type=float,
        default=0.7,
    )
    parser.add_argument(
        "--val_ratio",
        type=float,
        default=0.1,
    )

    # GBRT 参数
    parser.add_argument(
        "--n_estimators",
        type=int,
        default=200,
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--max_depth",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--min_samples_split",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--min_samples_leaf",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--subsample",
        type=float,
        default=0.9,
    )
    parser.add_argument(
        "--max_features",
        type=str,
        default=None,
        choices=[None, "sqrt", "log2"],
    )
    parser.add_argument(
        "--loss",
        type=str,
        default="huber",
        choices=["huber", "squared_error"],
    )

    parser.add_argument(
        "--max_train_samples",
        type=int,
        default=300000,
        help=(
            "GBRT 最大训练样本数；交通数据很大时用于加速。"
            "设为 -1 使用全部训练样本。"
        ),
    )

    parser.add_argument(
        "--mape_threshold",
        type=float,
        default=1e-5,
        help="计算 MAPE 时忽略绝对值小于该值的真实值",
    )

    parser.add_argument(
        "--no_time_features",
        action="store_true",
        help="关闭时间周期 sin/cos 特征",
    )
    parser.add_argument(
        "--no_node_id",
        action="store_true",
        help="关闭 node id 特征",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=2026,
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default="./runs/gbrt",
    )

    # 仅用于提醒：sklearn GBRT 使用 CPU
    parser.add_argument(
        "--device_note",
        type=str,
        default="cpu",
        help="仅作为记录；sklearn GradientBoostingRegressor 使用 CPU",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args)
