import sys
sys.path.append('../')
import torch
import torch.nn as nn
import torch.nn.functional as F
import einops
from einops import rearrange, repeat
from ..pf_utils import mask_path

"""
This AGCRN is used for 2-stage training scheme: Pretrain + Finetune
"""

class AVWGCN(nn.Module):
    # 定义AVWGCN类，继承自nn.Module
    def __init__(self, dim_in, dim_out, cheb_k, embed_dim):
        # 初始化函数，传入输入维度、输出维度、切比雪夫多项式的阶数、嵌入维度
        super(AVWGCN, self).__init__()
        # 调用父类的初始化函数
        self.cheb_k = cheb_k
        # 定义切比雪夫多项式的阶数
        self.weights_pool = nn.Parameter(torch.FloatTensor(embed_dim, cheb_k, dim_in, dim_out))
        # 定义权重池化参数，维度为(embed_dim, cheb_k, dim_in, dim_out)
        self.bias_pool = nn.Parameter(torch.FloatTensor(embed_dim, dim_out))
    
    def apply_s_mask(self, support, s_mask, normalize=False):
        """
        NOTE: mask: 1 is keep, 0 is masked
        """
        N, _ = support.shape
        
        # 将support与s_mask相乘，得到support_masked
        support_masked = support * s_mask
        # 如果normalize为True，则对support_masked进行softmax归一化
        if normalize:
            support_masked = F.softmax(support_masked, dim=1)

        # 返回support_masked
        return support_masked

    def forward(self, x, node_embeddings, s_mask, normalize=False):
        # 获取节点数量
        node_num = node_embeddings.shape[0]
        # 计算支持矩阵
        #! 自适应邻居矩阵
        supports = F.softmax(F.relu(torch.mm(node_embeddings, node_embeddings.transpose(0, 1))), dim=1) # [N, N]: row sum is 1

        #! 应用掩码
        supports = self.apply_s_mask(supports, s_mask, normalize)
        
        # 初始化支持集
        support_set = [torch.eye(node_num).to(supports.device), supports]
        # 计算Chebyshev多项式
        # 切比雪夫多项式的阶数:T_k=2L*T_k-1-T_k-2
        for k in range(2, self.cheb_k):
            support_set.append(torch.matmul(2 * supports, support_set[-1]) - support_set[-2])
        # 将支持集堆叠成张量
        supports = torch.stack(support_set, dim=0)
        #! 计算权重
        weights = torch.einsum('nd,dkio->nkio', node_embeddings, self.weights_pool)
        #! 计算偏置
        bias = torch.matmul(node_embeddings, self.bias_pool)
        # 计算图卷积
        x_g = torch.einsum("knm,bmc->bknc", supports, x)
        # 调整张量形状
        x_g = x_g.permute(0, 2, 1, 3)
        # 计算图卷积输出
        x_gconv = torch.einsum('bnki,nkio->bno', x_g, weights) + bias
        # 返回图卷积输出
        return x_gconv


class AGCRNCell(nn.Module):
    # 初始化AGCRNCell类
    def __init__(self, node_num, dim_in, dim_out, cheb_k, embed_dim):
        super(AGCRNCell, self).__init__()
        # 节点数量
        self.node_num = node_num
        # 隐藏层维度
        self.hidden_dim = dim_out
        # 定义门控单元
        self.gate = AVWGCN(dim_in+self.hidden_dim, 2*dim_out, cheb_k, embed_dim)
        # 定义更新单元
        self.update = AVWGCN(dim_in+self.hidden_dim, dim_out, cheb_k, embed_dim)

    # 前向传播
    def forward(self, x, state, node_embeddings, s_mask, normalize):
        # 将状态转换为与输入相同的设备
        #! hidden state
        state = state.to(x.device)
        # 将输入和状态连接起来
        input_and_state = torch.cat((x, state), dim=-1)
        #! 计算门控单元的输出(空间掩码)
        z_r = torch.sigmoid(self.gate(input_and_state, node_embeddings, s_mask, normalize))
        # 将输出分割为z和r
        z, r = torch.split(z_r, self.hidden_dim, dim=-1)
        # 计算候选隐藏状态
        candidate = torch.cat((x, z*state), dim=-1)
        # 计算更新后的隐藏状态
        hc = torch.tanh(self.update(candidate, node_embeddings, s_mask, normalize))
        # 计算新的隐藏状态
        h = r*state + (1-r)*hc
        # 返回新的隐藏状态
        return h

    # 初始化隐藏状态
    def init_hidden_state(self, batch_size):
        # 返回一个全零的隐藏状态
        return torch.zeros(batch_size, self.node_num, self.hidden_dim)


class AVWDCRNN(nn.Module):
    def __init__(self, node_num, dim_in, dim_out, cheb_k, embed_dim, num_layers=1):
        super(AVWDCRNN, self).__init__()
        # 断言num_layers至少为1，即编码器中至少有一个DCRNN层
        assert num_layers >= 1, 'At least one DCRNN layer in the Encoder.'
        self.node_num = node_num
        self.input_dim = dim_in
        self.num_layers = num_layers
        # 初始化DCRNN层
        self.dcrnn_cells = nn.ModuleList()
        self.dcrnn_cells.append(AGCRNCell(node_num, dim_in, dim_out, cheb_k, embed_dim))
        for _ in range(1, num_layers):
            self.dcrnn_cells.append(AGCRNCell(node_num, dim_out, dim_out, cheb_k, embed_dim))

    def forward(self, x, init_state, node_embeddings, s_mask, normalize):
        # 断言x的形状为[batch_size, seq_length, node_num, input_dim]
        assert x.shape[2] == self.node_num and x.shape[3] == self.input_dim
        seq_length = x.shape[1]
        current_inputs = x
        output_hidden = []
        # 遍历每一层DCRNN
        for i in range(self.num_layers):
            state = init_state[i]
            inner_states = []
            # 遍历序列长度
            for t in range(seq_length):
                # 将当前输入、状态、节点嵌入、掩码和归一化参数传入dcrnn_cells中的第i个cell，得到新的状态
                state = self.dcrnn_cells[i](current_inputs[:, t, :, :], state, node_embeddings, s_mask, normalize)
                # 将新的状态添加到inner_states列表中
                inner_states.append(state)
            output_hidden.append(state)
            current_inputs = torch.stack(inner_states, dim=1)
        return current_inputs, output_hidden

    def init_hidden(self, batch_size):
        # 初始化隐藏状态
        init_states = []
        for i in range(self.num_layers):
            init_states.append(self.dcrnn_cells[i].init_hidden_state(batch_size))
        return torch.stack(init_states, dim=0)


class InnerProductDecoder(nn.Module):
    """Decoder for using inner product for prediction."""
    def __init__(self, dropout, act=torch.sigmoid, with_proj=False, hid_dim=None):
        super(InnerProductDecoder, self).__init__()
        # 定义dropout层
        self.dropout = nn.Dropout(dropout)
        # 定义激活函数
        self.act = act
        # 如果with_proj为True，则定义一个1维卷积层
        self.proj = nn.Identity() if not with_proj else nn.Conv1d(hid_dim, hid_dim, kernel_size=1)

    def forward(self, z):
        """
        z: [B, N, F]
        """
        # 对输入进行dropout操作
        z = self.dropout(z)
        # 对输入进行投影操作，并重新排列维度
        z = self.proj(z.permute(0, 2, 1)).permute(0, 2, 1)
        # 计算邻接矩阵，使用bmm函数计算z和z的转置的乘积，并使用激活函数进行激活
        adj = self.act(torch.bmm(z, z.permute(0, 2, 1)))
        # 返回邻接矩阵
        return adj


class AGCRN(nn.Module):
    def __init__(
        self, 
        num_nodes, 
        embed_dim, 
        in_dim, 
        out_dim, 
        rnn_units, 
        num_layers, 
        cheb_k,
        in_horizon,
        out_horizon,
        stru_dec_drop,
        stru_dec_proj,
    ):
        # 初始化AGCRN类
        super(AGCRN, self).__init__()
        # 节点数量
        self.num_nodes = num_nodes
        # 输出维度
        self.output_dim = out_dim
        # 隐藏层维度
        self.hidden_dim = rnn_units
        # 输入时间步长
        self.in_horizon = in_horizon
        # 输出时间步长
        self.out_horizon = out_horizon
        # 结构解码器dropout率
        self.stru_dec_drop = stru_dec_drop

        # 节点嵌入
        self.node_embeddings = nn.Parameter(torch.randn(num_nodes, embed_dim), requires_grad=True)

        # mask token
        self.mask_token = nn.Parameter(torch.randn(rnn_units), requires_grad=True)

        # 编码器
        self.encoder = AVWDCRNN(num_nodes, rnn_units, rnn_units, cheb_k, embed_dim, num_layers)

        # 结构解码器
        self.structure_decoder = InnerProductDecoder(stru_dec_drop, act=lambda x: x, with_proj=stru_dec_proj, hid_dim=rnn_units)
        # 特征解码器
        self.feature_decoder = nn.Conv2d(1, in_horizon, kernel_size=(1, rnn_units), bias=True)
        
        # 特征嵌入
        self.to_feat_embedding = nn.Linear(in_dim, rnn_units)

        # 初始化参数
        self.init_parameters()

    def init_parameters(self):
        """follow STGCL way"""
        # 遍历模型中的所有参数
        for p in self.parameters():
            # 如果参数的维度大于1
            if p.dim() > 1:
                # 使用Xavier均匀分布初始化参数
                torch.nn.init.xavier_uniform_(p)
            else:
                # 使用均匀分布初始化参数
                torch.nn.init.uniform_(p)


    def get_support(self):
        """
        get current support: [N, N]: between 0 to 1 element-wise
        """
        # 计算节点嵌入矩阵的转置矩阵
        support = torch.sigmoid(torch.mm(self.node_embeddings, self.node_embeddings.transpose(0, 1)))
        # 返回支持矩阵
        return support


    def feature_masking(self, x, mask_ratio, mask_f_strategy='patch_uniform', mask=None, *args, **kwargs):
        """
        masking according to strategy: per sample masking on time axis
        x: [B, Tin, N, Din=1]
        NOTE: mask: 1 is keep, 0 is masked
        """
        B, T, N, D = x.shape

        # 如果mask不为空，则直接返回mask后的x和mask
        if mask is not None:
            x_masked = x * mask.unsqueeze(-1)
            return x_masked, mask

        # 如果mask_ratio为0，则返回全1的mask和x
        if mask_ratio == 0:
            mask = torch.ones([B, T, N], device=x.device)
            x_masked = x
            return x_masked, mask

        # 断言mask_f_strategy为'patch_uniform'
        assert mask_f_strategy == 'patch_uniform'
            
        # 获取patch_length，默认为1
        patch_length = kwargs.get('patch_length', 1)    # default is 1: collaspe to uniform
        # 断言patch_length小于等于T/2且T能被patch_length整除
        assert patch_length <= T / 2 and T % patch_length == 0, 'patch_length need to be smaller than sequence length and dividable.'
        # 计算patch数量
        num_patches = T // patch_length
        # 计算需要mask的patch数量
        num_masked_patches = round(num_patches * mask_ratio)
        
        # Initialize the mask with all ones: mask on T dim
        mask = torch.ones([B, T, N], device=x.device)  
        
        # Randomly select patches to be masked
        masked_indices = torch.randperm(num_patches)[:num_masked_patches]
        
        # Generate the indices to mask
        start_indices = (masked_indices * patch_length).to(dtype=torch.long, device=x.device)
        end_indices = (start_indices + patch_length).to(dtype=torch.long, device=x.device)

        ranges = torch.stack([torch.arange(start, end) for start, end in zip(start_indices, end_indices)])
        all_indices = torch.flatten(ranges).to(x.device)
        mask.scatter_(1, repeat(all_indices, 't -> b t n', b=B, n=N), 0)

        # mask by zero 
        x_masked = x * mask.unsqueeze(-1)


        return x_masked, mask


    def structure_masking(self, x, mask_ratio, mask_s_strategy='rw_fill', mask=None, *args, **kwargs):
        """
        NOTE: mask: 1 is keep, 0 is masked
        """
        B, _, N, _ = x.shape

        if mask is not None:
            return mask

        if mask_ratio == 0:
            return torch.ones(N, N, device=x.device)

        assert mask_s_strategy == 'rw_fill'
            
        goal_discard = round(N * N * mask_ratio)

        # STEP1: random-walk based path masking: fully connected graph 
        binaried_support = torch.ones_like(self.get_support())
        # walks_per_node = int(kwargs.get('walks_per_node', 10))
        # walk_length = int(kwargs.get('walk_length', 20))
        # start = kwargs.get('start', 'node')
        # p = int(kwargs.get('p', 1.0))
        # q = int(kwargs.get('q', 1.0))
        walks_per_node = self.args.walks_per_node
        walk_length = self.args.walk_length
        start = self.args.start
        p = self.args.p
        q = self.args.q
        masked_edge_index, num_discard = mask_path(binaried_support, mask_ratio=mask_ratio, walks_per_node=walks_per_node, \
        walk_length=walk_length, start=start, p=p, q=q) # [2, num_masked]
        
        # STEP2: if more, discard; else, uniform add
        mask = torch.ones_like(binaried_support)
        if goal_discard > num_discard:
            mask[masked_edge_index[0, :], masked_edge_index[1, :]] = 0
            # uniform masking
            remain_discard = goal_discard - num_discard
            remain_idx = torch.nonzero(binaried_support * mask)
            shuffled_idx = torch.randperm(remain_idx.size(0))
            mask_indices = shuffled_idx[:remain_discard]
            remain_actual_mask_idx = remain_idx[mask_indices]
            mask[remain_actual_mask_idx[:, 0], remain_actual_mask_idx[:, 1]] = 0
        else:
            masked_edge_index = masked_edge_index[:,:goal_discard]
            mask[masked_edge_index[0, :], masked_edge_index[1, :]] = 0

        return mask


    def encode(self, x, mask_s=0, mask_f=0, mask_s_strategy='rw_fill', mask_f_strategy='patch_uniform', *args, **kwargs):
        """
        input: [B, Tin, N, Din]
        output: [B, Tin, N, F], [B, N, F]
        """
        B, T, N, _ = x.shape
        init_state = self.encoder.init_hidden(x.shape[0])  # [L, B, N, F]

        raw_x = x[...,:1].clone()
        
        # random_masking for now: TODO: other strategies
        x_masked, f_mask = self.feature_masking(raw_x, mask_f, mask_f_strategy, mask=kwargs.get('f_mask', None), *args, **kwargs)

        # feature embedding with mask embedding
        embed_x = self.to_feat_embedding(x_masked)  # [B, T, N, F]
        embed_x = embed_x * f_mask.unsqueeze(-1) + repeat(self.mask_token, 'd -> b t n d', b=B, t=T, n=N) * (1 - f_mask.unsqueeze(-1))

        # structure mask:
        s_mask = self.structure_masking(raw_x, mask_s, mask_s_strategy, mask=kwargs.get('s_mask', None), *args, **kwargs)

        # encode
        normalize = kwargs.get('normalize', False)
        embedding, _ = self.encoder(embed_x, init_state, self.node_embeddings, s_mask, normalize=normalize)
        summary = embedding[:, -1:, :, :].squeeze(1)

        return embedding, summary, f_mask, s_mask


    def decode_structure(self, summary):
        """
        summary: [B, N, H]
        output: [B, N, N], between (0, 1)
        """
        return self.structure_decoder(summary)


    def decode_feature(self, summary):
        """
        summary: [B, N, H]
        output: [B, Tin, N, Din]
        """
        return self.feature_decoder(summary.unsqueeze(1))
        

    def forward_s_loss(self, target, pred, s_mask, l_type='cls_boost'):
        """
        target (support): [N, N]
        pred: [B, N, N]
        s_mask: [N, N]
        """
        # structure loss
        B = pred.shape[0]

        assert l_type == 'cls_boost'
        target = torch.ones_like(target)
        target = repeat(target, 'm n -> b m n', b=B)
        si_mask = repeat(abs(s_mask - 1), 'm n -> b m n', b=B)
        if torch.sum(si_mask) != 0:
            diff = F.binary_cross_entropy_with_logits(pred, target, reduction='none') * si_mask
            loss = torch.sum(diff) / torch.sum(si_mask)
        else:
            diff = F.binary_cross_entropy_with_logits(pred, target, reduction='none')
            loss = torch.mean(diff)

        return loss


    def forward_f_loss(self, target, pred, f_mask, l_type='reg_l1'):
        """
        target (support): [B, Tin, N, C=2]?
        pred: [B, Tin, N, C=1]
        f_mask: [B, Tin, N]
        """
        target = target[...,:1]

        # feature loss
        B, T, N, _ = pred.shape
        assert l_type == 'reg_l1'
        target, pred = target.squeeze(-1), pred.squeeze(-1)
        fi_mask = abs(f_mask - 1)
        if torch.sum(fi_mask) != 0:
            diff = torch.abs(torch.flatten(pred) - torch.flatten(target)) * torch.flatten(fi_mask)
            loss = torch.sum(diff) / torch.sum(fi_mask)
        else:
            # do not mask: this is for ablation
            diff = torch.abs(torch.flatten(pred) - torch.flatten(target))
            loss = torch.mean(diff)

        return loss


    def forward(self, x, mask_s=0, mask_f=0, mask_s_strategy='rw_fill', mask_f_strategy='patch_uniform', *args, **kwargs):
        # f_mask: [B, Tin, N]; s_mask: [N, N]
        embedding, summary, f_mask, s_mask = self.encode(x, mask_s, mask_f, mask_s_strategy, mask_f_strategy, *args, **kwargs)

        recon_s = self.decode_structure(summary)    # [B, N, N]
        recon_f = self.decode_feature(summary)      # [B, T, N, C=1]

        sl_type = kwargs.get('sl_type', 'cls_boost')
        fl_type = kwargs.get('fl_type', 'reg_l1')
        s_loss = self.forward_s_loss(self.get_support(), recon_s, s_mask, sl_type)
        f_loss = self.forward_f_loss(x, recon_f, f_mask, fl_type)

        s_weight = kwargs.get('sl_weight', 1.0)
        f_weight = kwargs.get('fl_weight', 1.0)
        loss = s_weight * s_loss + f_weight * f_loss
        
        loss_info = {'s_loss': s_loss.item(), 'f_loss': f_loss.item(), 'loss': loss.item()}
        return loss, loss_info


class AGCRN_Decoder(nn.Module):
    """
    agcrn decoder
    """
    def __init__(self, out_dim, rnn_units, horizon, de_mlp=False):
        super(AGCRN_Decoder, self).__init__()
        self.de_mlp = de_mlp
        if not self.de_mlp:
            self.end_conv = nn.Conv2d(1, horizon * out_dim, kernel_size=(1, rnn_units), bias=True)
        else:
            self.end_conv_1 = nn.Conv2d(rnn_units, rnn_units * 8, kernel_size=(1, 1), bias=True)
            self.end_conv_2 = nn.Conv2d(rnn_units * 8, horizon * out_dim, kernel_size=(1, 1), bias=True)
        
    def forward(self, input):
        if not self.de_mlp:
            x = self.end_conv(input)
        else:
            x = input.transpose(1,3)
            x = F.relu(self.end_conv_1(x))
            x = self.end_conv_2(x)
        return x



if __name__ == "__main__":
    B = 2
    Tin = 12
    N = 2
    D = 1
    Tout = 12


    torch.manual_seed(0)
    x = torch.randn(B, Tin, N, D)

    mdl= AGCRN(
        num_nodes=N, 
        embed_dim=B, 
        in_dim=D,
        out_dim=D, 
        rnn_units=2, 
        num_layers=4, 
        cheb_k=2, 
        in_horizon=Tin,
        out_horizon=Tout,
        stru_dec_drop=0.1,
    ) 

    decoder = AGCRN_Decoder(
        out_dim=1, rnn_units=2, horizon=Tout, de_mlp=True
    )
    _, encoded, _, _ = mdl.encode(x, mask_f_strategy='patch_uniform', mask_f=0.75, patch_length=3)
    exit()
    decoded = decoder(encoded.unsqueeze(1))
    print(encoded.shape)
    print(decoded.shape)