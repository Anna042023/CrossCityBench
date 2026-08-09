#!/usr/bin/env bash
set -euo pipefail

DATA_ROOT="${1:-/data/wanganna/CauCrossNet/datasets}"
GPU="${2:-0}"

export CUDA_VISIBLE_DEVICES="$GPU"

python train_stgcn_ft.py --data_root "$DATA_ROOT" --task pems03_to_pems04 --device cuda:0 --save_dir runs/stgcn_ft
python train_stgcn_ft.py --data_root "$DATA_ROOT" --task pems03_to_pems08 --device cuda:0 --save_dir runs/stgcn_ft
python train_stgcn_ft.py --data_root "$DATA_ROOT" --task pemsbay_to_metrla --device cuda:0 --save_dir runs/stgcn_ft
python train_stgcn_ft.py --data_root "$DATA_ROOT" --task metrla_to_pemsbay --device cuda:0 --save_dir runs/stgcn_ft
