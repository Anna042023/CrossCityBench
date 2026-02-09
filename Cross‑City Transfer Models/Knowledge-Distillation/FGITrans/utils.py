# utils.py
import torch
import numpy as np

# === 指标函数：用于 pems03 → pems08（无缺失值，使用对称/简单指标） ===
def masked_mae_simple(preds, labels):
    return torch.abs(preds - labels).mean()

def masked_rmse_simple(preds, labels):
    return torch.sqrt(((preds - labels) ** 2).mean())

def masked_mape_symmetric(preds, labels):
    numerator = torch.abs(preds - labels)
    denominator = (torch.abs(preds) + torch.abs(labels)).clamp(min=1e-3)
    return (numerator / (denominator / 2)).mean() * 100

# === 指标函数：用于 pems-bay → metr-la（有缺失值，使用 masked 版本） ===
def masked_mae_masked(preds, labels, null_val=np.nan):
    if np.isnan(null_val):
        mask = torch.logical_not(torch.isnan(labels))
    else:
        mask = (labels != null_val)
    mask = mask.float()
    mask_mean = torch.mean(mask)
    if mask_mean < 1e-6:
        return torch.mean(torch.abs(preds - labels))
    mask = mask / mask_mean
    mask = torch.where(torch.isnan(mask), torch.zeros_like(mask), mask)
    loss = torch.abs(preds - labels)
    loss = loss * mask
    loss = torch.where(torch.isnan(loss), torch.zeros_like(loss), loss)
    return torch.mean(loss)

def masked_rmse_masked(preds, labels, null_val=np.nan):
    if np.isnan(null_val):
        mask = torch.logical_not(torch.isnan(labels))
    else:
        mask = (labels != null_val)
    mask = mask.float()
    mask_mean = torch.mean(mask)
    if mask_mean < 1e-6:
        return torch.sqrt(torch.mean((preds - labels) ** 2))
    mask = mask / mask_mean
    mask = torch.where(torch.isnan(mask), torch.zeros_like(mask), mask)
    diff = preds - labels
    diff_squared = diff ** 2
    diff_squared = diff_squared * mask
    diff_squared = torch.where(torch.isnan(diff_squared), torch.zeros_like(diff_squared), diff_squared)
    mse = torch.sum(diff_squared) / torch.sum(mask)
    return torch.sqrt(mse + 1e-8)

def masked_mape_standard(preds, labels, null_val=np.nan, eps=1e-5):
    if np.isnan(null_val):
        mask = torch.logical_not(torch.isnan(labels))
    else:
        mask = (labels != null_val)
    mask = mask & (labels.abs() > eps)
    mask = mask.float()
    mask_sum = torch.sum(mask)
    if mask_sum < 1e-6:
        return torch.tensor(100.0)
    abs_diff = torch.abs(preds - labels)
    mape = abs_diff / (torch.abs(labels) + eps)
    mape = mape * mask
    mape = torch.where(torch.isnan(mape), torch.zeros_like(mape), mape)
    return torch.sum(mape) / mask_sum * 100

# === 统一入口：根据数据集对返回对应的指标函数 ===
def get_metric_functions(source_dataset, target_dataset):
    # 判断是否属于 pems-bay → metr-la 类型（含缺失值）
    if (source_dataset == 'pems-bay' and target_dataset == 'metr-la') or \
       (target_dataset in ['pems-bay', 'metr-la']):
        return masked_mae_masked, masked_rmse_masked, masked_mape_standard
    # 否则使用简单版本（如 pems03 → pems08）
    else:
        return masked_mae_simple, masked_rmse_simple, masked_mape_symmetric

# === 其他工具函数（保持不变）===
def pseudo_huber_loss(pred, target, delta=1.0):
    diff = pred - target
    return delta ** 2 * (torch.sqrt(1 + (diff / delta) ** 2) - 1)

def gaussian_kernel(x, y, sigma=1.0):
    x = x.view(x.size(0), -1)
    y = y.view(y.size(0), -1)
    dist = torch.cdist(x, y, p=2)
    return torch.exp(-dist ** 2 / (2 * sigma ** 2))

def mmd_rsf(x, y, sigma=1.0):
    k_xx = gaussian_kernel(x, x, sigma)
    k_yy = gaussian_kernel(y, y, sigma)
    k_xy = gaussian_kernel(x, y, sigma)
    n = x.size(0)
    m = y.size(0)
    mmd = k_xx.sum() / (n * n) + k_yy.sum() / (m * m) - 2 * k_xy.sum() / (n * m)
    return torch.clamp(mmd, min=0)