from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


class GradientReverseFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, lambd):
        ctx.lambd = lambd
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.lambd * grad_output, None


def grad_reverse(x, lambd=1.0):
    return GradientReverseFn.apply(x, float(lambd))


class DomainDiscriminator(nn.Module):
    """
    The paper states that the discriminators are fully connected layers.
    We flatten each node's complete temporal feature sequence, apply GRL,
    and classify source vs target.
    """
    def __init__(self, seq_len: int, feat_dim: int, hidden_dim: int = 32):
        super().__init__()
        in_dim = seq_len * feat_dim
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2),
        )

    def forward(self, x, grl_lambda=1.0):
        # x: [B,N,T,D]
        b, n, t, d = x.shape
        z = x.reshape(b * n, t * d)
        z = grad_reverse(z, grl_lambda)
        return self.net(z)


class CrossCityGraphStructureLearning(nn.Module):
    def __init__(self, n_source: int, n_target: int, emb_dim: int = 32, tau: float = 0.5):
        super().__init__()
        self.n_source = n_source
        self.n_target = n_target
        self.emb_dim = emb_dim
        self.tau = tau

        self.source_embedding = nn.Parameter(torch.empty(n_source, emb_dim))
        self.target_embedding = nn.Parameter(torch.empty(n_target, emb_dim))
        nn.init.xavier_uniform_(self.source_embedding)
        nn.init.xavier_uniform_(self.target_embedding)

        # Eq. (3): Z_i = FC(FC(E_i)). Shared projection for both domains.
        self.fc1 = nn.Linear(emb_dim, emb_dim)
        self.fc2 = nn.Linear(emb_dim, emb_dim)

    def node_features(self):
        zs = self.fc2(F.relu(self.fc1(self.source_embedding)))
        zt = self.fc2(F.relu(self.fc1(self.target_embedding)))
        return zs, zt

    def probabilities(self):
        zs, zt = self.node_features()
        scale = math.sqrt(self.emb_dim)
        # Eqs. (4)-(6) are dot products but the paper also states theta in [0,1].
        # Sigmoid makes the dot-product score a valid Bernoulli probability.
        theta_s = torch.sigmoid((zs @ zs.t()) / scale)
        theta_t = torch.sigmoid((zt @ zt.t()) / scale)
        theta_cc = torch.sigmoid((zt @ zs.t()) / scale)  # [Nt,Ns]
        eps = 1e-6
        return (
            theta_s.clamp(eps, 1 - eps),
            theta_t.clamp(eps, 1 - eps),
            theta_cc.clamp(eps, 1 - eps),
        )

    @staticmethod
    def _binary_concrete(theta, tau, hard=True):
        eps = 1e-6
        u1 = torch.rand_like(theta).clamp(eps, 1 - eps)
        u2 = torch.rand_like(theta).clamp(eps, 1 - eps)
        g1 = -torch.log(-torch.log(u1))
        g2 = -torch.log(-torch.log(u2))
        logits = torch.log(theta) - torch.log1p(-theta)
        soft = torch.sigmoid((logits + g1 - g2) / tau)
        if not hard:
            return soft
        hard_adj = (soft >= 0.5).to(soft.dtype)
        return hard_adj.detach() - soft.detach() + soft

    def learned_adjacency(self, training=True, hard_eval=True):
        theta_s, theta_t, theta_cc = self.probabilities()
        if training:
            a_s = self._binary_concrete(theta_s, self.tau, hard=True)
            a_t = self._binary_concrete(theta_t, self.tau, hard=True)
            a_cc = self._binary_concrete(theta_cc, self.tau, hard=True)
        else:
            if hard_eval:
                a_s = (theta_s >= 0.5).float()
                a_t = (theta_t >= 0.5).float()
                a_cc = (theta_cc >= 0.5).float()
            else:
                a_s, a_t, a_cc = theta_s, theta_t, theta_cc

        top = torch.cat([a_s, a_cc.t()], dim=1)
        bottom = torch.cat([a_cc, a_t], dim=1)
        full = torch.cat([top, bottom], dim=0)
        return full, (theta_s, theta_t, theta_cc)

    def reconstruction_loss(self, prior_s, prior_t):
        theta_s, theta_t, _ = self.probabilities()
        # Mean BCE is the numerically practical counterpart of Eqs. (8)-(9).
        ls = F.binary_cross_entropy(theta_s, prior_s)
        lt = F.binary_cross_entropy(theta_t, prior_t)
        return ls + lt


class TemporalFeatureExtractor(nn.Module):
    def __init__(self, in_dim=1, hidden_dim=64):
        super().__init__()
        # The paper explicitly uses two GRU layers.
        self.gru = nn.GRU(
            input_size=in_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
        )

    def forward(self, x):
        # x: [B,N,T,C]
        b, n, t, c = x.shape
        z = x.reshape(b * n, t, c)
        y, _ = self.gru(z)
        return y.reshape(b, n, t, -1)


class SpatialFeatureExtractor(nn.Module):
    def __init__(self, in_dim=64, out_dim=32):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)

    def forward(self, h, adj):
        # Eq. (17): ReLU(A_bar H W + b)
        z = self.linear(h)  # [B,N,T,D]
        z = torch.einsum("nm,bmtd->bntd", adj, z)
        return F.relu(z)


class GlobalSpatialTemporalAttention(nn.Module):
    """
    Implements Eqs. (20)-(22) as closely as their index notation permits:
    for each time step, each node's query is compared with its own global
    node embedding, scores are normalized over nodes, and a global context
    is formed as the weighted sum of node embeddings. The context is then
    broadcast to every node, yielding [B,N,T,d_emb] as required by Eq. (23).
    """
    def __init__(self, spatial_dim=32, emb_dim=32):
        super().__init__()
        self.query = nn.Linear(spatial_dim, emb_dim)
        self.scale = math.sqrt(emb_dim)

    def forward(self, h, embeddings, return_attention=False):
        # h: [B,N,T,D], embeddings: [N,E]
        q = self.query(h)
        scores = (q * embeddings[None, :, None, :]).sum(dim=-1) / self.scale
        attn = torch.softmax(scores, dim=1)  # normalize over nodes
        context = torch.einsum("bnt,ne->bte", attn, embeddings)
        k = context[:, None, :, :].expand(-1, h.shape[1], -1, -1)
        if return_attention:
            return k, attn
        return k


class MLPGlobalFusion(nn.Module):
    """M4b: replace attention with two FC layers and an intermediate ReLU."""
    def __init__(self, spatial_dim=32, emb_dim=32, hidden_dim=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(spatial_dim + emb_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, emb_dim),
        )

    def forward(self, h, embeddings):
        e = embeddings[None, :, None, :].expand(h.shape[0], -1, h.shape[2], -1)
        return self.net(torch.cat([h, e], dim=-1))


class PredictionHead(nn.Module):
    def __init__(self, in_dim, hidden_dim=32, out_dim=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, x):
        return self.net(x)


class DAGN(nn.Module):
    """
    Paper-faithful DAGN reproduction with configurable dimensions where the
    paper does not disclose exact values.

    Variants:
      full : full DAGN
      M1   : temporal+spatial extractors only; prior block graph, no adv/GSTA
      M2   : full model but graph reconstruction loss disabled by trainer
      M3a  : temporal adversarial loss disabled by trainer
      M3b  : spatial adversarial loss disabled by trainer
      M4a  : remove GSTA
      M4b  : replace GSTA attention with MLP fusion
    """
    def __init__(
        self,
        n_source,
        n_target,
        seq_len=12,
        in_dim=1,
        out_dim=1,
        emb_dim=32,
        temporal_dim=64,
        spatial_dim=32,
        discriminator_hidden=32,
        predictor_hidden=32,
        tau=0.5,
        variant="full",
        normalize_adj=True,
        hard_graph_eval=True,
    ):
        super().__init__()
        self.n_source = n_source
        self.n_target = n_target
        self.seq_len = seq_len
        self.variant = variant
        self.normalize_adj = normalize_adj
        self.hard_graph_eval = hard_graph_eval

        self.temporal = TemporalFeatureExtractor(in_dim, temporal_dim)
        self.spatial = SpatialFeatureExtractor(temporal_dim, spatial_dim)

        self.use_ccgsl = variant != "M1"
        self.use_gsta = variant not in {"M1", "M4a"}
        self.use_mlp_gsta = variant == "M4b"
        self.use_temporal_adv = variant not in {"M1", "M3a"}
        self.use_spatial_adv = variant not in {"M1", "M3b"}

        if self.use_ccgsl:
            self.ccgsl = CrossCityGraphStructureLearning(n_source, n_target, emb_dim, tau)
        else:
            self.ccgsl = None

        if self.use_temporal_adv:
            self.temporal_discriminator = DomainDiscriminator(seq_len, temporal_dim, discriminator_hidden)
        else:
            self.temporal_discriminator = None

        if self.use_spatial_adv:
            self.spatial_discriminator = DomainDiscriminator(seq_len, spatial_dim, discriminator_hidden)
        else:
            self.spatial_discriminator = None

        if self.use_gsta:
            if self.use_mlp_gsta:
                self.gsta = MLPGlobalFusion(spatial_dim, emb_dim, predictor_hidden)
            else:
                self.gsta = GlobalSpatialTemporalAttention(spatial_dim, emb_dim)
            pred_in = spatial_dim + emb_dim
        else:
            self.gsta = None
            pred_in = spatial_dim

        self.predictor = PredictionHead(pred_in, predictor_hidden, out_dim)

    @staticmethod
    def _block_prior(prior_s, prior_t):
        ns, nt = prior_s.shape[0], prior_t.shape[0]
        zeros_st = prior_s.new_zeros(ns, nt)
        zeros_ts = prior_t.new_zeros(nt, ns)
        return torch.cat([
            torch.cat([prior_s, zeros_st], dim=1),
            torch.cat([zeros_ts, prior_t], dim=1),
        ], dim=0)

    def _prepare_adj(self, adj):
        if not self.normalize_adj:
            return adj
        n = adj.shape[0]
        a = adj + torch.eye(n, device=adj.device, dtype=adj.dtype)
        deg = a.sum(dim=1, keepdim=True).clamp_min(1.0)
        return a / deg

    def forward(self, x_source, x_target, prior_s, prior_t, grl_lambda=1.0, return_aux=False):
        if x_source.shape[0] != x_target.shape[0]:
            raise ValueError("Source and target batch sizes must match")
        if x_source.shape[2] != self.seq_len or x_target.shape[2] != self.seq_len:
            raise ValueError(
                f"Model seq_len={self.seq_len}, got source={x_source.shape[2]}, target={x_target.shape[2]}"
            )

        x = torch.cat([x_source, x_target], dim=1)
        h_td = self.temporal(x)

        theta = None
        if self.use_ccgsl:
            adj, theta = self.ccgsl.learned_adjacency(self.training, self.hard_graph_eval)
        else:
            adj = self._block_prior(prior_s, prior_t)
        adj = self._prepare_adj(adj)

        h_sd = self.spatial(h_td, adj)
        hs_td, ht_td = torch.split(h_td, [self.n_source, self.n_target], dim=1)
        hs_sd, ht_sd = torch.split(h_sd, [self.n_source, self.n_target], dim=1)

        temporal_logits = None
        spatial_logits = None
        if self.temporal_discriminator is not None:
            temporal_logits = (
                self.temporal_discriminator(hs_td, grl_lambda),
                self.temporal_discriminator(ht_td, grl_lambda),
            )
        if self.spatial_discriminator is not None:
            spatial_logits = (
                self.spatial_discriminator(hs_sd, grl_lambda),
                self.spatial_discriminator(ht_sd, grl_lambda),
            )

        attention = None
        if self.use_gsta:
            es = self.ccgsl.source_embedding
            et = self.ccgsl.target_embedding
            if self.use_mlp_gsta:
                ks = self.gsta(hs_sd, es)
                kt = self.gsta(ht_sd, et)
            else:
                ks, attn_s = self.gsta(hs_sd, es, return_attention=True)
                kt, attn_t = self.gsta(ht_sd, et, return_attention=True)
                attention = (attn_s, attn_t)
            fs = torch.cat([hs_sd, ks], dim=-1)
            ft = torch.cat([ht_sd, kt], dim=-1)
        else:
            fs, ft = hs_sd, ht_sd

        pred_s = self.predictor(fs)
        pred_t = self.predictor(ft)

        out = {
            "pred_source": pred_s,
            "pred_target": pred_t,
            "temporal_logits": temporal_logits,
            "spatial_logits": spatial_logits,
            "theta": theta,
        }
        if return_aux:
            out["attention"] = attention
            out["adjacency"] = adj
            out["h_td"] = h_td
            out["h_sd"] = h_sd
        return out

    def graph_reconstruction_loss(self, prior_s, prior_t):
        if self.ccgsl is None:
            return prior_s.new_tensor(0.0)
        return self.ccgsl.reconstruction_loss(prior_s, prior_t)
