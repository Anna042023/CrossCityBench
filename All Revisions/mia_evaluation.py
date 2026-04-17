#!/usr/bin/env python3
"""
mia_evaluation.py

Shadow-model based Membership Inference Attack (MIA) with a threshold-based
membership classifier.

Reported metric:
    membership advantage = max_threshold (TPR - FPR)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class AttackResult:
    best_threshold: float
    membership_advantage: float
    tpr: float
    fpr: float


class SimpleLinearRegressor:
    def __init__(self, input_dim: int, reg: float = 1e-3):
        self.w = np.zeros((input_dim, 1), dtype=np.float64)
        self.reg = reg

    def fit(self, x: np.ndarray, y: np.ndarray) -> None:
        xtx = x.T @ x
        ridge = self.reg * np.eye(x.shape[1])
        self.w = np.linalg.solve(xtx + ridge, x.T @ y)

    def predict(self, x: np.ndarray) -> np.ndarray:
        return x @ self.w


def build_demo_dataset(
    n_samples: int = 4000,
    input_dim: int = 16,
    noise_std: float = 0.5,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n_samples, input_dim))
    w_true = rng.normal(size=(input_dim, 1))
    y = x @ w_true + noise_std * rng.normal(size=(n_samples, 1))
    return x.astype(np.float64), y.astype(np.float64)


def per_sample_loss(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    return np.mean((y_true - y_pred) ** 2, axis=1)


def split_member_nonmember(
    x: np.ndarray,
    y: np.ndarray,
    member_ratio: float,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    idx = rng.permutation(len(x))
    n_member = int(len(x) * member_ratio)
    member_idx = idx[:n_member]
    nonmember_idx = idx[n_member:]
    return x[member_idx], y[member_idx], x[nonmember_idx], y[nonmember_idx]


def train_shadow_models(
    x: np.ndarray,
    y: np.ndarray,
    n_shadow: int = 5,
    member_ratio: float = 0.8,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    member_scores: List[float] = []
    nonmember_scores: List[float] = []

    for _ in range(n_shadow):
        local_rng = np.random.default_rng(int(rng.integers(0, 1_000_000)))
        x_mem, y_mem, x_non, y_non = split_member_nonmember(x, y, member_ratio, local_rng)

        model = SimpleLinearRegressor(input_dim=x.shape[1])
        model.fit(x_mem, y_mem)

        mem_score = -per_sample_loss(y_mem, model.predict(x_mem))
        non_score = -per_sample_loss(y_non, model.predict(x_non))

        member_scores.extend(mem_score.tolist())
        nonmember_scores.extend(non_score.tolist())

    return np.asarray(member_scores), np.asarray(nonmember_scores)


def membership_advantage(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> AttackResult:
    all_scores = np.concatenate([member_scores, nonmember_scores])
    thresholds = np.unique(np.quantile(all_scores, np.linspace(0.0, 1.0, 1001)))

    best_adv, best_thr, best_tpr, best_fpr = -1.0, 0.0, 0.0, 0.0
    for thr in thresholds:
        tpr = float(np.mean(member_scores >= thr))
        fpr = float(np.mean(nonmember_scores >= thr))
        adv = tpr - fpr
        if adv > best_adv:
            best_adv, best_thr, best_tpr, best_fpr = adv, float(thr), tpr, fpr

    return AttackResult(best_thr, float(best_adv), best_tpr, best_fpr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_shadow", type=int, default=5)
    parser.add_argument("--member_ratio", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    x, y = build_demo_dataset(seed=args.seed)
    split = int(0.8 * len(x))
    x_train, y_train = x[:split], y[:split]

    member_scores, nonmember_scores = train_shadow_models(
        x_train, y_train, n_shadow=args.n_shadow, member_ratio=args.member_ratio, seed=args.seed
    )
    result = membership_advantage(member_scores, nonmember_scores)

    print("=== Membership Inference Attack (MIA) ===")
    print(f"Shadow models: {args.n_shadow}")
    print(f"Best threshold: {result.best_threshold:.6f}")
    print(f"TPR: {result.tpr:.6f}")
    print(f"FPR: {result.fpr:.6f}")
    print(f"Membership advantage max(TPR-FPR): {result.membership_advantage:.6f}")


if __name__ == "__main__":
    main()
