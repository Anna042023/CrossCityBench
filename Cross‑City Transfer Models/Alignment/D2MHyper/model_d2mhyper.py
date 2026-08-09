import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------
# Gradient Reversal Layer (GRL)
# ---------------------------
class GradReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.alpha * grad_output, None


def grl(x, alpha=1.0):
    return GradReverse.apply(x, alpha)


# ---------------------------
# Simple GCN layer: H' = A_hat H W
# ---------------------------
class GCNLayer(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.lin = nn.Linear(in_dim, out_dim)

    def forward(self, H, A_hat):
        B, S, N, D = H.shape
        H1 = self.lin(H)
        out = torch.einsum("ij,bsjd->bsid", A_hat, H1)
        return out


def normalize_adj(A):
    if isinstance(A, np.ndarray):
        A = torch.from_numpy(A).float()
    A = A.float()
    N = A.shape[0]
    I = torch.eye(N, device=A.device)
    A = A + I
    deg = A.sum(dim=1)
    deg_inv_sqrt = torch.pow(deg.clamp(min=1e-6), -0.5)
    D_inv_sqrt = torch.diag(deg_inv_sqrt)
    return D_inv_sqrt @ A @ D_inv_sqrt


# ---------------------------
# Hypergraph message passing block
# ---------------------------
class HyperMP(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.ln = nn.LayerNorm(hidden_dim)

    def forward(self, H, A_h):
        Z = torch.einsum("bsen,bsnd->bsed", A_h.transpose(-1, -2), H)
        Hn = torch.einsum("bsne,bsed->bsnd", A_h, Z)
        Hn = self.ln(F.relu(Hn))
        return Hn


# ---------------------------
# Multi-scale fusion over scales using MultiheadAttention
# ---------------------------
def _auto_fix_heads(hidden_dim: int, heads: int) -> int:
    if heads <= 0:
        return 1
    if hidden_dim % heads == 0:
        return heads
    # choose closest divisor of hidden_dim
    candidates = [h for h in range(1, hidden_dim + 1) if hidden_dim % h == 0]
    best = min(candidates, key=lambda h: (abs(h - heads), -h))
    print(f"[Fix] hidden_dim={hidden_dim} not divisible by heads={heads}. Auto set heads={best}.")
    return best


class ScaleFusion(nn.Module):
    def __init__(self, hidden_dim, heads):
        super().__init__()
        heads = _auto_fix_heads(hidden_dim, heads)
        self.mha = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=heads, batch_first=True)
        self.ln = nn.LayerNorm(hidden_dim)

    def forward(self, reps_list):
        M = len(reps_list)
        X = torch.stack(reps_list, dim=3)  # (B,S,N,M,D)
        B, S, N, M, D = X.shape
        X = X.reshape(B * S * N, M, D)
        out, _ = self.mha(X, X, X, need_weights=False)
        out = self.ln(out)
        out = out.mean(dim=1)
        out = out.reshape(B, S, N, D)
        return out


# ---------------------------
# D2MHyper
# ---------------------------
class D2MHyper(nn.Module):
    def __init__(
        self,
        Ns, Nt,
        A_s, A_t,
        in_dim=1,
        hidden_dim=64,
        hyperedges=(20, 80, 200),
        heads=3,
        out_len=12
    ):
        super().__init__()
        self.Ns = Ns
        self.Nt = Nt
        self.Nsum = Ns + Nt
        self.hidden_dim = hidden_dim
        self.out_len = out_len
        self.M = len(hyperedges)
        self.hyperedges = list(hyperedges)

        A_s = normalize_adj(A_s)
        A_t = normalize_adj(A_t)
        self.register_buffer("A_s_hat", A_s)
        self.register_buffer("A_t_hat", A_t)

        self.in_proj = nn.Linear(in_dim, hidden_dim)
        self.gru = nn.GRU(input_size=hidden_dim, hidden_size=hidden_dim, batch_first=True)

        self.gcn_s = GCNLayer(hidden_dim, hidden_dim)
        self.gcn_t = GCNLayer(hidden_dim, hidden_dim)

        self.B_share = nn.ParameterList([nn.Parameter(torch.randn(E, hidden_dim) * 0.02) for E in self.hyperedges])
        self.B_s = nn.ParameterList([nn.Parameter(torch.randn(E, hidden_dim) * 0.02) for E in self.hyperedges])
        self.B_t = nn.ParameterList([nn.Parameter(torch.randn(E, hidden_dim) * 0.02) for E in self.hyperedges])

        self.hgmp = nn.ModuleList([HyperMP(hidden_dim) for _ in self.hyperedges])

        self.gk_mlp = nn.ModuleList([nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        ) for _ in self.hyperedges])

        # scale fusion (now auto-fixes heads internally)
        self.fuse_private = ScaleFusion(hidden_dim, heads=heads)
        self.fuse_share = ScaleFusion(hidden_dim, heads=heads)

        self.fuse_high_s = nn.Sequential(nn.Linear(hidden_dim * 2, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, hidden_dim))
        self.fuse_high_t = nn.Sequential(nn.Linear(hidden_dim * 2, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, hidden_dim))

        self.disc = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

        self.pred_mlp_s = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_len)
        )
        self.pred_mlp_t = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_len)
        )

    def _temporal_encode(self, X):
        B, S, N, C = X.shape
        Xp = self.in_proj(X)
        Xp = Xp.permute(0, 2, 1, 3).contiguous()
        Xp = Xp.view(B * N, S, self.hidden_dim)
        H, _ = self.gru(Xp)
        H = H.view(B, N, S, self.hidden_dim).permute(0, 2, 1, 3).contiguous()
        return H

    def _gen_hypergraph(self, H, Bm):
        logits = torch.einsum("bsnd,ed->bsne", H, Bm)
        A_h = F.softmax(logits, dim=-1)
        return A_h

    def _global_knowledge(self, H_pri, Bm, mlp):
        scores = torch.einsum("bsnd,ed->bsne", H_pri, Bm)
        att = F.softmax(scores, dim=-1)
        gk = torch.einsum("bsne,ed->bsnd", att, Bm)
        out = mlp(torch.cat([H_pri, gk], dim=-1))
        return out

    def forward(self, Xs, Xt, only_target=False, grl_alpha=1.0):
        if only_target:
            Ht = self._temporal_encode(Xt)
            HGt = self.gcn_t(Ht, self.A_t_hat)

            pri_list_t = []
            for m, E in enumerate(self.hyperedges):
                Aht = self._gen_hypergraph(Ht, self.B_t[m])
                Ht_pri = self.hgmp[m](Ht, Aht)
                Ht_pri = self._global_knowledge(Ht_pri, self.B_t[m], self.gk_mlp[m])
                pri_list_t.append(Ht_pri)

            Ht_pri_fused = self.fuse_private(pri_list_t)
            Ht_share = torch.zeros_like(Ht_pri_fused)
            HHt = self.fuse_high_t(torch.cat([Ht_pri_fused, Ht_share], dim=-1))

            feat_t = torch.cat([HGt[:, -1], HHt[:, -1]], dim=-1)
            out_t = self.pred_mlp_t(feat_t)
            out_t = out_t.permute(0, 2, 1).unsqueeze(-1).contiguous()
            return None, out_t, torch.tensor(0.0, device=out_t.device)

        X = torch.cat([Xs, Xt], dim=2)
        Htemp = self._temporal_encode(X)

        Hs = Htemp[:, :, :self.Ns]
        Ht = Htemp[:, :, self.Ns:]

        HGs = self.gcn_s(Hs, self.A_s_hat)
        HGt = self.gcn_t(Ht, self.A_t_hat)

        share_list = []
        pri_list_s = []
        pri_list_t = []

        for m, E in enumerate(self.hyperedges):
            Ah_share = self._gen_hypergraph(Htemp, self.B_share[m])
            H_share_m = self.hgmp[m](Htemp, Ah_share)
            share_list.append(H_share_m)

            Ah_s = self._gen_hypergraph(Hs, self.B_s[m])
            Ah_t = self._gen_hypergraph(Ht, self.B_t[m])

            Hs_pri_m = self.hgmp[m](Hs, Ah_s)
            Ht_pri_m = self.hgmp[m](Ht, Ah_t)

            Hs_pri_m = self._global_knowledge(Hs_pri_m, self.B_s[m], self.gk_mlp[m])
            Ht_pri_m = self._global_knowledge(Ht_pri_m, self.B_t[m], self.gk_mlp[m])

            pri_list_s.append(Hs_pri_m)
            pri_list_t.append(Ht_pri_m)

        H_share = self.fuse_share(share_list)
        Hs_share = H_share[:, :, :self.Ns]
        Ht_share = H_share[:, :, self.Ns:]

        Hs_pri = self.fuse_private(pri_list_s)
        Ht_pri = self.fuse_private(pri_list_t)

        HHs = self.fuse_high_s(torch.cat([Hs_pri, Hs_share], dim=-1))
        HHt = self.fuse_high_t(torch.cat([Ht_pri, Ht_share], dim=-1))

        Hpri_joint = torch.cat([Hs_pri, Ht_pri], dim=2)

        pri_logits = self.disc(grl(Hpri_joint, grl_alpha))
        sha_logits = self.disc(grl(H_share, grl_alpha))

        pri_labels = torch.zeros_like(pri_logits)
        sha_labels = torch.ones_like(sha_logits)

        adv_loss = F.binary_cross_entropy_with_logits(pri_logits, pri_labels) + \
                   F.binary_cross_entropy_with_logits(sha_logits, sha_labels)

        feat_s = torch.cat([HGs[:, -1], HHs[:, -1]], dim=-1)
        feat_t = torch.cat([HGt[:, -1], HHt[:, -1]], dim=-1)

        out_s = self.pred_mlp_s(feat_s)
        out_t = self.pred_mlp_t(feat_t)

        out_s = out_s.permute(0, 2, 1).unsqueeze(-1).contiguous()
        out_t = out_t.permute(0, 2, 1).unsqueeze(-1).contiguous()
        return out_s, out_t, adv_loss
