#!/usr/bin/env bash
set -euo pipefail

DATA_ROOT=${1:-./datasets}
GPU=${2:-0}

python run.py --data_root "$DATA_ROOT" --task pems03_to_pems04   --device cuda:${GPU}
python run.py --data_root "$DATA_ROOT" --task pems03_to_pems08   --device cuda:${GPU}
python run.py --data_root "$DATA_ROOT" --task metrla_to_pemsbay   --device cuda:${GPU}
python run.py --data_root "$DATA_ROOT" --task pemsbay_to_metrla   --device cuda:${GPU}
# Uncomment if SZ-Taxi is available:
# python run.py --data_root "$DATA_ROOT" --task pemsbay_to_sztaxi --device cuda:${GPU}
