#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dagn.data import (
    canonical_name, resolve_data_path, resolve_adj_path, resolve_sensor_ids_path,
    load_traffic_array, load_sensor_ids, load_adjacency,
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_root", default="./datasets")
    p.add_argument("--dataset", required=True)
    p.add_argument("--data", default=None)
    p.add_argument("--adj", default=None)
    p.add_argument("--sensor_ids", default=None)
    p.add_argument("--feature_idx", type=int, default=0)
    p.add_argument("--allow_identity_adj", action="store_true")
    a = p.parse_args()
    name = canonical_name(a.dataset)
    dp = resolve_data_path(a.data_root, name, a.data)
    ap = resolve_adj_path(a.data_root, name, a.adj)
    sp = resolve_sensor_ids_path(a.data_root, name, a.sensor_ids)
    x = load_traffic_array(dp, name, a.feature_idx)
    ids = load_sensor_ids(sp)
    adj = load_adjacency(ap, x.shape[1], ids, a.allow_identity_adj)
    print("data:", dp)
    print("adj :", ap)
    print("ids :", sp)
    print("shape:", x.shape)
    print("adj shape:", adj.shape, "edges(undirected count approx):", int(adj.sum() / 2))
    print("value range:", float(x.min()), float(x.max()))


if __name__ == "__main__":
    main()
