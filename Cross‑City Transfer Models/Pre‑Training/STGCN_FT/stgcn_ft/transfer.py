from __future__ import annotations

from typing import Dict, List, Tuple

import torch


def transfer_shape_compatible_parameters(source: torch.nn.Module, target: torch.nn.Module):
    """Copy all trainable parameters whose names and shapes match.

    This is necessary because the supplied STGCN has node-dependent LayerNorm affine
    parameters and a node-specific output bias. Those tensors cannot be copied when
    source and target cities have different sensor counts. All shared temporal and
    graph-convolution weights are transferred.
    """
    src = dict(source.named_parameters())
    copied: List[str] = []
    skipped: List[Tuple[str, str]] = []
    with torch.no_grad():
        for name, p_t in target.named_parameters():
            p_s = src.get(name)
            if p_s is None:
                skipped.append((name, "missing_in_source"))
            elif tuple(p_s.shape) != tuple(p_t.shape):
                skipped.append((name, f"shape {tuple(p_s.shape)} -> {tuple(p_t.shape)}"))
            else:
                p_t.copy_(p_s)
                copied.append(name)
    return copied, skipped
