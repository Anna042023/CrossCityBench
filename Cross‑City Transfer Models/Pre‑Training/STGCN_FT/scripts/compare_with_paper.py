#!/usr/bin/env python3
import argparse, json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--result', required=True, help='Path to seed_x/results.json')
    p.add_argument('--reference', default=str(Path(__file__).resolve().parents[1] / 'paper_stgcn_ft_reference.json'))
    args = p.parse_args()
    with open(args.result, 'r', encoding='utf-8') as f:
        result = json.load(f)
    with open(args.reference, 'r', encoding='utf-8') as f:
        refs = json.load(f)
    task = result['task']
    cur = result['metrics']
    ref = refs[task]
    print(f'Task: {task}')
    print('Horizon   Metric    Current      Paper       Delta')
    for h in ['3','6','12','Average']:
        for m in ['MAE','RMSE','MAPE']:
            c=float(cur[h][m]); r=float(ref[h][m])
            print(f'{h:>7s}   {m:<5s}   {c:10.4f}  {r:10.4f}  {c-r:+10.4f}')

if __name__ == '__main__':
    main()
