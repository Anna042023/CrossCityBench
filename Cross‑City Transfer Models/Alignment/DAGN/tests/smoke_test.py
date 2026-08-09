#!/usr/bin/env python3
"""Small shape/loss smoke test that does not require traffic datasets."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch
from dagn.model import DAGN


def main():
    torch.manual_seed(1)
    b, ns, nt, t = 2, 5, 3, 4
    model = DAGN(ns, nt, seq_len=t, emb_dim=8, temporal_dim=8,
                 spatial_dim=6, discriminator_hidden=4, predictor_hidden=8)
    xs = torch.randn(b, ns, t, 1)
    xt = torch.randn(b, nt, t, 1)
    As = torch.eye(ns)
    At = torch.eye(nt)
    out = model(xs, xt, As, At, return_aux=True)
    assert out['pred_source'].shape == (b, ns, t, 1)
    assert out['pred_target'].shape == (b, nt, t, 1)
    assert out['adjacency'].shape == (ns + nt, ns + nt)
    loss = model.graph_reconstruction_loss(As, At)
    assert torch.isfinite(loss)
    print('DAGN smoke test: OK')


if __name__ == '__main__':
    main()
