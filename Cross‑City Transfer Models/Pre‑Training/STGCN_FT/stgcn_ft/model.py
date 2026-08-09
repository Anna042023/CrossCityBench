from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F


class TemporalConvLayer(nn.Module):
    """PyTorch port of the temporal_conv_layer in the supplied STGCN code."""

    def __init__(self, kt: int, c_in: int, c_out: int, act_func: str = "relu"):
        super().__init__()
        self.kt = int(kt)
        self.c_in = int(c_in)
        self.c_out = int(c_out)
        self.act_func = act_func.upper()

        if c_in > c_out:
            self.input_proj = nn.Conv2d(c_in, c_out, kernel_size=(1, 1), bias=False)
        else:
            self.input_proj = None

        out_channels = 2 * c_out if self.act_func == "GLU" else c_out
        self.temporal_conv = nn.Conv2d(
            c_in,
            out_channels,
            kernel_size=(kt, 1),
            stride=(1, 1),
            padding=0,
            bias=True,
        )

    def _residual(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, N, C]
        b, t, n, c = x.shape
        if self.c_in > self.c_out:
            z = x.permute(0, 3, 1, 2)  # [B,C,T,N]
            z = self.input_proj(z).permute(0, 2, 3, 1)
        elif self.c_in < self.c_out:
            pad = x.new_zeros((b, t, n, self.c_out - self.c_in))
            z = torch.cat([x, pad], dim=-1)
        else:
            z = x
        return z[:, self.kt - 1 :, :, :]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self._residual(x)
        z = x.permute(0, 3, 1, 2)  # [B,C,T,N]
        conv = self.temporal_conv(z).permute(0, 2, 3, 1)

        if self.act_func == "GLU":
            p, q = torch.split(conv, self.c_out, dim=-1)
            return (p + residual) * torch.sigmoid(q)
        if self.act_func == "LINEAR":
            return conv
        if self.act_func == "SIGMOID":
            return torch.sigmoid(conv)
        if self.act_func == "RELU":
            return F.relu(conv + residual)
        raise ValueError(f"Unknown temporal activation: {self.act_func}")


class ChebGraphConv(nn.Module):
    """Chebyshev spectral graph convolution used by the original STGCN."""

    def __init__(self, ks: int, c_in: int, c_out: int, cheb_polynomials: torch.Tensor):
        super().__init__()
        if cheb_polynomials.ndim != 3:
            raise ValueError("cheb_polynomials must have shape [Ks, N, N]")
        if cheb_polynomials.shape[0] != ks:
            raise ValueError("Ks mismatch between model and graph kernel")
        self.ks = int(ks)
        self.c_in = int(c_in)
        self.c_out = int(c_out)
        self.register_buffer("cheb_polynomials", cheb_polynomials.float())
        self.theta = nn.Linear(ks * c_in, c_out, bias=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B,T,N,Cin], cheb: [K,N,N]
        # support: [B,T,N,Cin,K] where the flattened order is C then K,
        # matching the supplied TensorFlow implementation.
        support = torch.einsum("knm,btmc->btnck", self.cheb_polynomials, x)
        b, t, n, c, k = support.shape
        support = support.reshape(b, t, n, c * k)
        return self.theta(support)


class SpatialConvLayer(nn.Module):
    def __init__(self, ks: int, c_in: int, c_out: int, cheb_polynomials: torch.Tensor):
        super().__init__()
        self.c_in = int(c_in)
        self.c_out = int(c_out)
        if c_in > c_out:
            self.input_proj = nn.Conv2d(c_in, c_out, kernel_size=(1, 1), bias=False)
        else:
            self.input_proj = None
        self.gconv = ChebGraphConv(ks, c_in, c_out, cheb_polynomials)

    def _residual(self, x: torch.Tensor) -> torch.Tensor:
        b, t, n, c = x.shape
        if self.c_in > self.c_out:
            return self.input_proj(x.permute(0, 3, 1, 2)).permute(0, 2, 3, 1)
        if self.c_in < self.c_out:
            pad = x.new_zeros((b, t, n, self.c_out - self.c_in))
            return torch.cat([x, pad], dim=-1)
        return x

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.relu(self.gconv(x) + self._residual(x))


class NodeLayerNorm(nn.Module):
    """LayerNorm over [node, channel], matching the supplied TF1 STGCN."""

    def __init__(self, n_nodes: int, channels: int, eps: float = 1e-6):
        super().__init__()
        self.norm = nn.LayerNorm((n_nodes, channels), eps=eps, elementwise_affine=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.norm(x)


class STConvBlock(nn.Module):
    def __init__(
        self,
        ks: int,
        kt: int,
        channels: Sequence[int],
        n_nodes: int,
        cheb_polynomials: torch.Tensor,
        dropout: float = 0.0,
    ):
        super().__init__()
        c_si, c_t, c_oo = [int(v) for v in channels]
        self.temporal_in = TemporalConvLayer(kt, c_si, c_t, act_func="GLU")
        self.spatial = SpatialConvLayer(ks, c_t, c_t, cheb_polynomials)
        # Original code uses default relu for the second temporal layer.
        self.temporal_out = TemporalConvLayer(kt, c_t, c_oo, act_func="relu")
        self.layer_norm = NodeLayerNorm(n_nodes, c_oo)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.temporal_in(x)
        x = self.spatial(x)
        x = self.temporal_out(x)
        x = self.layer_norm(x)
        return self.dropout(x)


class OutputLayer(nn.Module):
    def __init__(self, t_kernel: int, channels: int, n_nodes: int):
        super().__init__()
        self.temporal_in = TemporalConvLayer(t_kernel, channels, channels, act_func="GLU")
        self.layer_norm = NodeLayerNorm(n_nodes, channels)
        self.temporal_out = TemporalConvLayer(1, channels, channels, act_func="sigmoid")
        self.fc = nn.Conv2d(channels, 1, kernel_size=(1, 1), bias=False)
        # The supplied TF implementation has a node-specific bias [N,1].
        self.node_bias = nn.Parameter(torch.zeros(1, 1, n_nodes, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.temporal_in(x)
        x = self.layer_norm(x)
        x = self.temporal_out(x)
        y = self.fc(x.permute(0, 3, 1, 2)).permute(0, 2, 3, 1)
        y = y + self.node_bias
        return y


@dataclass
class STGCNConfig:
    n_his: int = 12
    ks: int = 3
    kt: int = 3
    blocks: tuple = ((1, 32, 64), (64, 32, 128))
    dropout: float = 0.0


class STGCN(nn.Module):
    """One-step STGCN, kept close to the user-supplied IJCAI'18 implementation.

    Multi-step forecasting is performed autoregressively, exactly like its tester.py.
    """

    def __init__(self, n_nodes: int, cheb_polynomials: torch.Tensor, config: STGCNConfig | None = None):
        super().__init__()
        self.n_nodes = int(n_nodes)
        self.config = config or STGCNConfig()
        self.n_his = self.config.n_his

        ko = self.n_his
        blocks = []
        for channels in self.config.blocks:
            blocks.append(
                STConvBlock(
                    self.config.ks,
                    self.config.kt,
                    channels,
                    self.n_nodes,
                    cheb_polynomials,
                    self.config.dropout,
                )
            )
            ko -= 2 * (self.config.kt - 1)
        if ko <= 1:
            raise ValueError(f"Output temporal kernel Ko must be > 1, got {ko}")

        self.st_blocks = nn.ModuleList(blocks)
        last_channels = int(self.config.blocks[-1][-1])
        self.output_layer = OutputLayer(ko, last_channels, self.n_nodes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Accept [B,T,N] or [B,T,N,1]
        if x.ndim == 3:
            x = x.unsqueeze(-1)
        if x.ndim != 4:
            raise ValueError(f"Expected [B,T,N,1], got {tuple(x.shape)}")
        if x.shape[1] != self.n_his:
            raise ValueError(f"Expected history={self.n_his}, got T={x.shape[1]}")
        if x.shape[2] != self.n_nodes:
            raise ValueError(f"Expected n_nodes={self.n_nodes}, got N={x.shape[2]}")

        z = x
        for block in self.st_blocks:
            z = block(z)
        y = self.output_layer(z)  # [B,1,N,1]
        return y[:, 0, :, 0]

    @torch.no_grad()
    def autoregressive_forecast(self, history: torch.Tensor, horizon: int) -> torch.Tensor:
        """history: [B,n_his,N], return [B,horizon,N]."""
        self.eval()
        x = history
        if x.ndim == 4:
            x = x[..., 0]
        preds = []
        for _ in range(int(horizon)):
            y = self(x)
            preds.append(y)
            x = torch.cat([x[:, 1:, :], y.unsqueeze(1)], dim=1)
        return torch.stack(preds, dim=1)
