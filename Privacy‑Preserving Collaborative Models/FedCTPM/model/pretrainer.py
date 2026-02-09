import os
import sys
import csv
import math
import time
import pickle
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import torch
import torch.nn as nn
from torch.optim import Adam, AdamW
from torch.utils.data import DataLoader
from einops import rearrange
import matplotlib.pyplot as plt

sys.path.append('../')
from utils.dataset_pems import load_dataset
from utils.log_utils import save_csv_log
from utils.torch_utils import get_scheduler
from utils.loss_utils import masked_mae, masked_mape, masked_rmse, metric

def exists(x):
    return x is not None


class PreTrainer(object):
    def __init__(
        self,
        dataset,
        model,
        args,
        batch_size,
        pt_learning_rate,
        pt_weight_decay,
        opt_name='adam',
    ):
        super().__init__()

        self.model = model
        self.device = next(self.model.parameters()).device
        # self.adj = adj  # The adjacency matrix is from https://arxiv.org/pdf/2108.11873.pdf: weighted with self_loops

        self.args = args

        self.batch_size = batch_size
        self.opt_name = opt_name
        self.learning_rate = pt_learning_rate
        self.weight_decay = pt_weight_decay

        self.horizon = args.horizon
        self.horizon = args.horizon
        self.dtype = torch.float64

        self.dataset_name = dataset
        # datasets
        # if self.dataset_name == 'pems_03':
        #     input_data = './data/pems_03'
        # elif self.dataset_name == 'pems_04':
        #     input_data = './data/pems_04'
        # elif self.dataset_name == 'pems_07':
        #     input_data = './data/pems_07'
        # elif self.dataset_name == 'pems_08':
        #     input_data = './data/pems_08'
        # else:
        #     raise NotImplementedError

        # self.dataloader = load_dataset(input_data, self.batch_size, self.batch_size, self.batch_size, device=self.device, dtype=self.dtype)
        # self.scaler = self.dataloader['scaler']

        # optimizer
        optimizer = Adam if self.opt_name == 'adam' else AdamW
        self.opt = optimizer(self.model.parameters(), lr=self.learning_rate, eps=self.args.pt_eps, weight_decay=self.weight_decay)

        self.scheduler = get_scheduler(self.opt, policy=self.args.pt_sched_policy, nepoch_fix=self.args.pt_num_epoch_fix_lr, nepoch=self.args.train_epoch,
            decay_step=self.args.pt_decay_step, gamma=self.args.pt_gamma, milestones=self.args.pt_milestones)
        
        self.epoch = 0
        self.train_loss_list = []
        self.best_train_loss = float('inf')
        self.batches_seen = None
        print('Pretrainer initialization done.')

    def save(self, to_save_path):
        data = {
            'epoch': self.epoch,
            'train_loss_list': self.train_loss_list,
            'best_train_loss': self.best_train_loss,
            'batches_seen': self.batches_seen,
            'model': self.model.state_dict(),
            'opt': self.opt.state_dict(),
            'sched': self.scheduler.state_dict() if exists(self.scheduler) else None,
        }
        torch.save(data, to_save_path)
        return

    def load(self, to_load_path):
        if self.args.backbone == 'dcrnn':
            self.model(torch.rand(1, self.horizon, self.args.num_nodes, self.args.in_dim).to(self.device).to(self.dtype))
            optimizer = Adam if self.opt_name == 'adam' else AdamW
            self.opt = optimizer(self.model.parameters(), lr=self.learning_rate, eps=self.args.pt_eps, weight_decay=self.weight_decay)
            self.scheduler = get_scheduler(self.opt, policy=self.args.pt_sched_policy, nepoch_fix=self.args.pt_num_epoch_fix_lr, nepoch=self.args.train_epoch,
                decay_step=self.args.pt_decay_step, gamma=self.args.pt_gamma, milestones=self.args.pt_milestones)
        device = self.device
        data = torch.load(to_load_path, map_location=device)
        self.epoch = data['epoch']
        self.train_loss_list = data['train_loss_list']
        self.best_train_loss = data['best_train_loss']
        self.batches_seen = data['batches_seen']
        self.model.load_state_dict(data['model'])
        self.opt.load_state_dict(data['opt'])
        if exists(data['sched']):
            self.scheduler.load_state_dict(data['sched'])  
        else: self.scheduler = None
        print(">>> finish loading pretrainer model ckpt from path '{}'".format(to_load_path))
        return


    def train(self,train_loader,scaler):
        """
        pretrain model for one epoch
        """ 
        self.model.train()
        t_s = time.time()
        epoch_loss = 0.
        epoch_iter = 0
        epoch_loss_info = {}
        self.batches_seen = len(train_loader) * self.epoch    # this is for dcrnn specific training
        model_configs = {**self.args.mask_specs, **self.args.loss_specs}
        # self.dataloader['train_loader'].shuffle()

        # TODO: epoch-wise mask: generate f_mask, s_mask here instead
        if self.args.epoch_wise_mask:
            x_holder = torch.rand(self.batch_size, self.horizon, self.args.num_nodes, self.args.input_dim).to(self.device)
            s_mask, _ = self.model.structure_masking(x_holder, mask_ratio=self.args.mask_s, mask=None, **self.args)
            _, f_mask = self.model.feature_masking(x_holder, mask_ratio=self.args.mask_f, mask=None, **self.args)
            model_configs = {**model_configs, 's_mask': s_mask, 'f_mask': f_mask}

        for batch_idx, (data, target) in enumerate(train_loader):
            # torch.cuda.empty_cache()
            x = data[..., :self.args.input_dim].to(self.args.device) # B, T_in, N, 1
            y = target[..., :self.args.output_dim].to(self.args.device)  # B, T_out, N, 1

        # for idx, (x, _) in enumerate(self.dataloader['train_loader'].get_iterator()):
        #     x = x[...,:self.args.in_dim]  #BTND
            loss, loss_info = self.model(x, batches_seen=self.batches_seen, **model_configs)
            for key, value in loss_info.items():
                if key not in epoch_loss_info:
                    epoch_loss_info[key] = value
                else:
                    epoch_loss_info[key] += value

            if self.batches_seen == 0 and self.args.backbone == 'dcrnn':   # dcrnn only
                optimizer = Adam if self.opt_name == 'adam' else AdamW
                self.opt = optimizer(self.model.parameters(), lr=self.learning_rate, eps=self.args.pt_eps, weight_decay=self.weight_decay)
                self.scheduler = get_scheduler(self.opt, policy=self.args.pt_sched_policy, nepoch_fix=self.args.pt_num_epoch_fix_lr, nepoch=self.args.train_epoch,
                decay_step=self.args.pt_decay_step, gamma=self.args.pt_gamma, milestones=self.args.pt_milestones)

            self.opt.zero_grad()
            loss.backward()
            if exists(self.args.pt_clip_grad) and self.args.pt_clip_grad != 'None':
                nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=self.args.pt_clip_grad)
            self.opt.step()
            epoch_loss += loss.item()
            self.batches_seen += 1
            epoch_iter += 1
        if not isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau) and exists(self.scheduler):
            self.scheduler.step()
        
        self.epoch += 1
        epoch_loss /= epoch_iter
        for key, value in epoch_loss_info.items():
            epoch_loss_info[key] /= epoch_iter
        lr = self.opt.param_groups[0]['lr']
        dt = time.time() - t_s
        self.train_loss_list.append(epoch_loss)
        return lr, epoch_loss, epoch_loss_info, dt 
    
    def plot(self):
        plt.figure()
        plt.plot(self.train_loss_list, 'r', label='Train loss')
        plt.legend()
        plt.savefig(os.path.join(self.args.vis_dir, self.args.cid + '_pt.png'))
        plt.close()
