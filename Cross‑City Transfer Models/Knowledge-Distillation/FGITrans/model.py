# model.py
import torch
import torch.nn as nn
from utils import pseudo_huber_loss, mmd_rsf


class STAE(nn.Module):
    def __init__(self, num_nodes, input_dim, d_model, da=16):
        super().__init__()
        self.fc_feat = nn.Linear(input_dim, d_model)
        self.d_model = d_model
        self.num_nodes = num_nodes
        self.day_embed = nn.Embedding(7, d_model)
        self.time_embed = nn.Embedding(288, d_model)

        # 使用更稳定的初始化
        self.Ea = nn.Parameter(torch.randn(1, num_nodes, da) * 0.01)
        self.spatial_proj = nn.Linear(da, d_model)

        # 添加归一化层
        self.norm = nn.LayerNorm(d_model * 4)  # feat_emb + time_emb + spatial_emb

    def forward(self, x, tod, dow):
        B, T, N, D = x.shape
        #x_flat = x.view(B * T * N, D)
        x_flat = x.reshape(B * T * N, D)
        feat_emb = self.fc_feat(x_flat)
        feat_emb = feat_emb.view(B, T, N, -1)

        # 时间嵌入
        tod_emb = self.time_embed(tod).unsqueeze(2).expand(-1, -1, N, -1)
        dow_emb = self.day_embed(dow).unsqueeze(2).expand(-1, -1, N, -1)
        time_emb = torch.cat([tod_emb, dow_emb], dim=-1)

        # 空间嵌入
        Ea_exp = self.Ea.expand(B, T, -1, -1)
        spatial_emb = self.spatial_proj(Ea_exp)

        out = torch.cat([feat_emb, time_emb, spatial_emb], dim=-1)
        out = self.norm(out)
        return out


class TemporalSpatialTransformer(nn.Module):
    def __init__(self, d_in, d_model, n_heads, num_layers, dropout=0.1):
        super().__init__()
        self.input_proj = nn.Linear(d_in, d_model)
        torch.nn.init.xavier_uniform_(self.input_proj.weight, gain=0.1)

        # 时间编码器
        temporal_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dropout=dropout,
            batch_first=True, activation='gelu'  # 使用GELU激活函数
        )
        self.temporal_encoder = nn.TransformerEncoder(temporal_layer, num_layers=num_layers)

        # 空间编码器
        spatial_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dropout=dropout,
            batch_first=True, activation='gelu'
        )
        self.spatial_encoder = nn.TransformerEncoder(spatial_layer, num_layers=num_layers)

        # 添加残差连接和归一化
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x):
        B, T, N, _ = x.shape
        x = self.input_proj(x)

        # 时间维度编码
        x_temp = x.permute(0, 2, 1, 3).contiguous().view(B * N, T, -1)
        z_te = self.temporal_encoder(x_temp)
        z_te = self.norm1(z_te)
        z_te = z_te.view(B, N, T, -1).permute(0, 2, 1, 3)

        # 空间维度编码
        z_sp = z_te.contiguous().view(B * T, N, -1)
        z_sp = self.spatial_encoder(z_sp)
        z_sp = self.norm2(z_sp)
        z_sp = z_sp.view(B, T, N, -1)

        return z_te, z_sp


class FGITransBranch(nn.Module):
    def __init__(self, num_nodes, input_dim, d_model, n_heads, num_layers, da, dropout):
        super().__init__()
        self.stae = STAE(num_nodes, input_dim, d_model, da)
        self.transformer = TemporalSpatialTransformer(
            d_in=d_model * 4, d_model=d_model, n_heads=n_heads,
            num_layers=num_layers, dropout=dropout
        )

        # 改进的预测头：多层预测
        self.pred_head = nn.Sequential(
            nn.Linear(d_model, d_model * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 2, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, 1)
        )

        # 初始化
        for layer in self.pred_head:
            if isinstance(layer, nn.Linear):
                torch.nn.init.xavier_uniform_(layer.weight, gain=0.1)
                torch.nn.init.zeros_(layer.bias)

    def forward(self, x, tod, dow):
        emb = self.stae(x, tod, dow)
        z_te, z_sp = self.transformer(emb)
        out = self.pred_head(z_sp)
        return out, z_te, z_sp


class AlignmentBranch(nn.Module):
    def __init__(self, d_model, n_heads, num_layers, dropout=0.1):
        super().__init__()
        self.cross_attn = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 4, d_model)
        )
        self.pred_head = nn.Linear(d_model, 1)
        torch.nn.init.xavier_uniform_(self.pred_head.weight, gain=0.1)

    def forward(self, query, key_value):
        B, T, N, D = query.shape
        query_flat = query.view(B * T, N, D)
        key_value_flat = key_value.view(B * T, N, D)

        attn_out, _ = self.cross_attn(query_flat, key_value_flat, key_value_flat)
        out = self.norm1(attn_out + query_flat)
        ffn_out = self.ffn(out)
        out = self.norm2(ffn_out + out)
        out = out.view(B, T, N, D)
        pred = self.pred_head(out)
        return pred, out


class FGITrans(nn.Module):
    def __init__(self, src_nodes, tgt_nodes, src_input_dim, tgt_input_dim, d_model=64, n_heads=4, num_layers=2,
                 da=16, dropout=0.1, delta=1.0, temp=2.0, alpha=1.0, beta=2.5, sigma=1.0):
        super().__init__()
        self.source_branch = FGITransBranch(src_nodes, src_input_dim, d_model, n_heads, num_layers, da, dropout)
        self.target_branch = FGITransBranch(tgt_nodes, tgt_input_dim, d_model, n_heads, num_layers, da, dropout)

        # 只有在节点数相同时才使用对齐分支
        self.use_alignment = (src_nodes == tgt_nodes)
        if self.use_alignment:
            self.alignment_branch = AlignmentBranch(d_model, n_heads, num_layers, dropout)
        else:
            self.alignment_branch = None

        self.delta = delta
        self.temp = temp
        self.alpha = alpha
        self.beta = beta
        self.sigma = sigma

    def forward(self, src_x, tgt_x, tod, dow):
        if src_x is not None:
            src_pred, src_z_te, src_z_sp = self.source_branch(src_x, tod, dow)
        else:
            B, T, N, D = tgt_x.shape
            device = tgt_x.device
            src_pred = torch.zeros(B, T, N, 1, device=device)
            dim = self.target_branch.transformer.input_proj.out_features
            src_z_te = torch.zeros(B, T, N, dim, device=device)
            src_z_sp = torch.zeros(B, T, N, dim, device=device)

        tgt_pred, tgt_z_te, tgt_z_sp = self.target_branch(tgt_x, tod, dow)

        if self.use_alignment and src_x is not None:
            align_pred, _ = self.alignment_branch(src_z_sp.detach(), tgt_z_sp.detach())
        else:
            align_pred = tgt_pred.clone()

        return {
            'src_pred': src_pred, 'tgt_pred': tgt_pred, 'align_pred': align_pred,
            'src_z_te': src_z_te, 'src_z_sp': src_z_sp,
            'tgt_z_te': tgt_z_te, 'tgt_z_sp': tgt_z_sp
        }

    def compute_losses(self, outputs, src_y, tgt_y):
        src_pred, tgt_pred, align_pred = outputs['src_pred'], outputs['tgt_pred'], outputs['align_pred']

        # 只计算目标域的损失
        L_ph = pseudo_huber_loss(tgt_pred, tgt_y, self.delta).mean()

        # 对齐损失
        L_dtl = pseudo_huber_loss(tgt_pred, align_pred, self.delta).mean()

        # 总损失
        total_loss = L_ph + 0.1 * L_dtl

        loss_dict = {
            'L_ph': L_ph.item(),
            'L_dtl': L_dtl.item(),
            'total_loss': total_loss.item()
        }

        return total_loss, loss_dict