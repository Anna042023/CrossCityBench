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

from lib.TrainInits import MAE_torch, RMSE_torch, MAPE_torch, All_Metrics
def exists(x):
    return x is not None

# TODO: finetuner,微调器，用于微调模型
class FineTuner(object):
    """
    Follow STGCL s_train.py for now
    """
    def __init__(
        self,
        dataset,
        pretrained_encoder,
        decoder,
        loss,
        args,
        batch_size,
        learning_rate_enc,
        learning_rate_dec,
        weight_decay_enc,
        weight_decay_dec,
        ft=True,                    # default, finetuner finetune the model; if not, only train the decoder
        opt_name='adam',
    ):
        super().__init__()



        # self.adj = adj              # The adjacency matrix is from https://arxiv.org/pdf/2108.11873.pdf: weighted with self_loops
        self.loss = torch.nn.L1Loss().to(args.device)

        self.args = args

        self.ft = ft
        self.batch_size = batch_size
        self.opt_name = opt_name
        self.learning_rate_enc = learning_rate_enc
        self.learning_rate_dec = learning_rate_dec
        self.weight_decay_enc = weight_decay_enc
        self.weight_decay_dec = weight_decay_dec

        self.dataset_name = args.dataset
        self.in_horizon = args.horizon
        self.out_horizon = args.horizon
        self.dtype = torch.float32

        self.dataset_name = args.dataset

        self.pretrained_encoder = pretrained_encoder.to(self.dtype)

        self.device = next(self.pretrained_encoder.parameters()).device
        self.decoder = decoder.to(self.device).to(self.dtype)
        # datasets
        # if self.dataset_name == 'pems_03':
        #     input_data = './data/pems_03'
        # elif self.dataset_name == 'pems_04':
        #     input_data = './data/pems_04'
        # elif self.dataset_name == 'pems_07':
        #     input_data = './data/pems_07'
        # elif self.dataset_name == 'pems_08':
        #     input_data = './data/pems_08'
        # elif self.dataset_name == 'MERT-LA':
        #     input_data = './data/MERT-LA'
        # else:
        #     raise NotImplementedError

        # self.dataloader = load_dataset(input_data, self.batch_size, self.batch_size, self.batch_size, device=self.device, dtype=self.dtype)
        # self.scaler = self.dataloader['scaler']

        # optimizer
        optimizer = Adam if self.opt_name == 'adam' else AdamW
        if self.ft:
            self.opt = optimizer(
                [{'params': self.pretrained_encoder.parameters(), 'lr': self.learning_rate_enc, 'weight_decay': self.weight_decay_enc, 'eps': self.args.eps_enc},
                {'params': self.decoder.parameters(), 'lr': self.learning_rate_dec, 'weight_decay': self.weight_decay_dec, 'eps': self.args.eps_dec}]
            )
        else:
            self.opt = optimizer(self.decoder.parameters(), lr=self.learning_rate_dec, weight_decay=self.weight_decay_dec, eps=self.args.eps_dec)
        self.scheduler = get_scheduler(self.opt, policy=self.args.ft_sched_policy, nepoch_fix=self.args.ft_num_epoch_fix_lr, nepoch=self.args.ft_epoch,
        decay_step=self.args.ft_decay_step, gamma=self.args.ft_gamma, milestones=self.args.ft_milestones)

        self.epoch = 0
        self.train_loss_list = []
        self.valid_loss_list = []
        self.best_valid_loss = float('inf')
        self.batches_seen = None
        print('Finetuner initialization done.')

    def _get_error_info(self, prediction, target):
        mae = masked_mae(prediction, target, 0.0).item()
        rmse = masked_rmse(prediction, target, 0.0).item()
        mape = masked_mape(prediction, target, 0.0).item()
        error_info = {'mae': mae, 'rmse': rmse, 'mape': mape}
        return error_info

    def save(self, to_save_path):
        data = {
            'epoch': self.epoch,
            'train_loss_list': self.train_loss_list,
            'valid_loss_list': self.train_loss_list,
            'best_valid_loss': self.best_valid_loss,
            'batches_seen': self.batches_seen,
            'pretrained_encoder': self.pretrained_encoder.state_dict(),
            'decoder': self.decoder.state_dict(),
            'opt': self.opt.state_dict(),
            'sched': self.scheduler.state_dict() if exists(self.scheduler) else None,
        }
        torch.save(data, to_save_path)
        return

    def load(self, to_load_path):
        if self.args.backbone == 'dcrnn':
            self.pretrained_encoder(torch.rand(1, self.in_horizon, self.args.num_nodes, self.args.in_dim).to(self.device).to(self.dtype))
            self.decoder(torch.rand(1, self.in_horizon, self.args.num_nodes, self.args.rnn_dim).to(self.device).to(self.dtype),
            torch.rand(1, self.out_horizon, self.args.num_nodes, self.args.out_dim).to(self.device).to(self.dtype), batches_seen=0)
            optimizer = Adam if self.opt_name == 'adam' else AdamW
            if self.ft:
                self.opt = optimizer(
                    [{'params': self.pretrained_encoder.parameters(), 'lr': self.learning_rate_enc, 'weight_decay': self.weight_decay_enc, 'eps': self.args.eps_enc},
                    {'params': self.decoder.parameters(), 'lr': self.learning_rate_dec, 'weight_decay': self.weight_decay_dec, 'eps': self.args.eps_dec}]
                )
            else:
                self.opt = optimizer(self.decoder.parameters(), lr=self.learning_rate_dec, weight_decay=self.weight_decay_dec, eps=self.args.eps_dec)
            self.scheduler = get_scheduler(self.opt, policy=self.args.ft_sched_policy, nepoch_fix=self.args.ft_num_epoch_fix_lr, nepoch=self.args.ft_epoch, \
            decay_step=self.args.ft_decay_step, gamma=self.args.ft_gamma, milestones=self.args.ft_milestones)
        device = self.device
        data = torch.load(to_load_path, map_location=device)
        self.epoch = data['epoch']
        self.train_loss_list = data['train_loss_list']
        self.valid_loss_list = data['valid_loss_list']
        self.best_valid_loss = data['best_valid_loss']
        self.batches_seen = data['batches_seen']
        self.pretrained_encoder.load_state_dict(data['pretrained_encoder'])
        self.decoder.load_state_dict(data['decoder'])
        self.opt.load_state_dict(data['opt'])
        if exists(data['sched']):
            self.scheduler.load_state_dict(data['sched'])  
        else: self.scheduler = None
        print(">>> finish loading pretrained-encoder, decoder model ckpt from path '{}'".format(to_load_path))
        return


    def test_load(self, to_load_path):
        if self.args.backbone == 'dcrnn':
            self.pretrained_encoder(torch.rand(1, self.in_horizon, self.args.num_nodes, self.args.in_dim).to(self.device).to(self.dtype))
            self.decoder(torch.rand(1, self.in_horizon, self.args.num_nodes, self.args.rnn_dim).to(self.device).to(self.dtype),
            torch.rand(1, self.out_horizon, self.args.num_nodes, self.args.out_dim).to(self.device).to(self.dtype), batches_seen=0)
        device = self.device
        data = torch.load(to_load_path, map_location=device)
        self.pretrained_encoder.load_state_dict(data['pretrained_encoder'])
        self.decoder.load_state_dict(data['decoder'])
        print(">>> finish loading pretrained-encoder, decoder model ckpt from path '{}'".format(to_load_path))
        return

    def train(self,train_loader,scaler):
        """
        finetune model for one epoch
        """ 
        if self.ft:
            self.pretrained_encoder.train()
        else:
            self.pretrained_encoder.eval()
        self.decoder.train()
        t_s = time.time()
        epoch_loss = 0.
        epoch_iter = 0
        total_mae, total_rmse, total_mape = 0, 0, 0
        epoch_error_info = {}
        self.batches_seen = len(train_loader) * self.epoch    # this is for dcrnn specific training
        # train_loader.shuffle()

        for batch_idx, (data, target) in enumerate(train_loader):
            # torch.cuda.empty_cache()
            x = data[..., :self.args.input_dim].to(self.args.device) # B, T_in, N, 1
            y = target[..., :self.args.output_dim].to(self.args.device)  # B, T_out, N, 1
            # self.optimizer.zero_grad()
        #
        # for idx, (x, y) in enumerate(self.dataloader['train_loader'].get_iterator()):
        #     x = x[...,:self.args.in_dim]
        #     y = y[...,:self.args.out_dim]
            pretrained_encoder = self.pretrained_encoder.float()
            all_states, encoded_state, _, _ = pretrained_encoder.encode(x, mask_s=0, mask_f=0)
            # if self.args.backbone == 'dcrnn':
            #     output = self.decoder(all_states, scaler.transform(y), self.batches_seen)
            # elif self.args.backbone == 'gwnet' or self.args.backbone == 'mtgnn':
            #     output = self.decoder(encoded_state)
            # else:
            output = self.decoder(encoded_state.unsqueeze(1))  #state bfnt(64)

            loss = self.loss(output, y[...,:self.args.output_dim])
            error_info = self._get_error_info(output, y[...,:self.args.output_dim])

            # output = scaler.inverse_transform(output)
            output = scaler.inverse_transform(output)
            label = scaler.inverse_transform(y)

            total_mae += MAE_torch(output, label).item()
            total_rmse += RMSE_torch(output, label).item()
            total_mape += MAPE_torch(output, label).item()

            for key, value in error_info.items():
                if key not in epoch_error_info:
                    epoch_error_info[key] = value
                else:
                    epoch_error_info[key] += value

            if batch_idx % self.args.log_step == 0:
                self.args.logger.info('F Train Epoch {}: {}/{} Loss: {:.6f}'.format(
                    self.epoch, batch_idx, len(train_loader), loss.item()))

            # if self.batches_seen == 0 and self.args.backbone == 'dcrnn':   # dcrnn only
            #     optimizer = Adam if self.opt_name == 'adam' else AdamW
            #     if self.ft:
            #         self.opt = optimizer(
            #             [{'params': self.pretrained_encoder.parameters(), 'lr': self.learning_rate_enc, 'weight_decay': self.weight_decay_enc, 'eps': self.args.eps_enc},
            #             {'params': self.decoder.parameters(), 'lr': self.learning_rate_dec, 'weight_decay': self.weight_decay_dec, 'eps': self.args.eps_dec}]
            #         )
            #     else:
            #         self.opt = optimizer(self.decoder.parameters(), lr=self.learning_rate_dec, weight_decay=self.weight_decay_dec, eps=self.args.eps_dec)
            #     self.scheduler = get_scheduler(self.opt, policy=self.args.ft_sched_policy, nepoch_fix=self.args.ft_num_epoch_fix_lr, nepoch=self.args.ft_epoch, \
            #     decay_step=self.args.ft_decay_step, gamma=self.args.ft_gamma, milestones=self.args.ft_milestones)

            self.opt.zero_grad()
            loss.backward()
            if exists(self.args.ft_clip_grad) and self.args.ft_clip_grad != 'None':
                nn.utils.clip_grad_norm_(self.pretrained_encoder.parameters(), max_norm=self.args.ft_clip_grad)
                nn.utils.clip_grad_norm_(self.decoder.parameters(), max_norm=self.args.ft_clip_grad)
            self.opt.step()
            epoch_loss += loss.item()
            self.batches_seen += 1
            epoch_iter += 1
        if not isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau) and exists(self.scheduler):
            self.scheduler.step()
        
        self.epoch += 1
        epoch_loss /= epoch_iter
        for key, value in epoch_error_info.items():
            epoch_error_info[key] /= epoch_iter
        if self.ft:
            en_lr = self.opt.param_groups[0]['lr']
            de_lr = self.opt.param_groups[1]['lr']
        else:
            en_lr = -1
            de_lr = self.opt.param_groups[0]['lr']
        dt = time.time() - t_s
        self.train_loss_list.append(epoch_loss)

        mae = total_mae / len(train_loader)
        rmse = total_rmse / len(train_loader)
        mape = total_mape / len(train_loader)
        self.args.logger.info('**********Finetuner Train Epoch {}: MAE: {:.6f} RMSE: {:.6f} MAPE: {:.6f}'.format(self.epoch, mae, rmse, mape))
        return en_lr, de_lr, epoch_loss, epoch_error_info, dt
    
    @torch.no_grad()
    def valid(self,val_loader,scaler):
        self.pretrained_encoder.eval()
        self.decoder.eval()
        total_iter = 0
        total_mae, total_rmse, total_mape = 0, 0, 0
        epoch_error_info = {}
        for batch_idx, (data, target) in enumerate(val_loader):
            x = data[..., :self.args.input_dim].to(self.args.device)  # B, T_in, N, 1
            y = target[..., :self.args.output_dim].to(self.args.device)  # B, T_out, N, 1
            all_states, encoded_state, _, _ = self.pretrained_encoder.encode(x, mask_s=0, mask_f=0)

            output = self.decoder(encoded_state.unsqueeze(1))
            error_info = self._get_error_info(output, y[...,:self.args.output_dim])

            # output = scaler.inverse_transform(output)
            output = scaler.inverse_transform(output)
            label = scaler.inverse_transform(y)

            total_mae += MAE_torch(output, label).item()
            total_rmse += RMSE_torch(output, label).item()
            # total_mape += MAPE_torch(output, label).item()
            total_mape += masked_mape(output, label,0).item()

            for key, value in error_info.items():
                if key not in epoch_error_info:
                    epoch_error_info[key] = value
                else:
                    epoch_error_info[key] += value
            total_iter += 1

        for key, value in epoch_error_info.items():
            epoch_error_info[key] /= total_iter
        self.valid_loss_list.append(epoch_error_info['mae'])
        mae = total_mae / len(val_loader)
        rmse = total_rmse / len(val_loader)
        mape = total_mape / len(val_loader)
        self.args.logger.info('**********client{} Finetuner Val Epoch {}: MAE: {:.6f} RMSE: {:.6f} MAPE: {:.6f}'.format(self.args.cid,self.epoch, mae, rmse,
                                                                                                 mape))
        return epoch_error_info

    @torch.no_grad()
    def test(self,val_loader,scaler):
        """
        NOTE: test should only be called once
        """
        # set header and logger
        head = np.array(['metric'])
        for k in range(1, self.out_horizon + 1):
            head = np.append(head, [f'{k}'])
        log = np.zeros([4, self.out_horizon + 1])

        self.pretrained_encoder.eval()
        self.decoder.eval()
        total_iter = 0
        all_preds, all_targets = [], []
        for batch_idx, (data, target) in enumerate(val_loader):
        # for idx, (x, y) in enumerate(self.dataloader['test_loader'].get_iterator()):
            x = data[...,:self.args.input_dim].to(self.args.device)
            y = target[...,:self.args.output_dim].to(self.args.device)
            all_states, encoded_state, _, _ = self.pretrained_encoder.encode(x, mask_s=0, mask_f=0)
            # if self.args.backbone == 'dcrnn':
            #     output = self.decoder(all_states)
            # elif self.args.backbone == 'gwnet' or self.args.backbone == 'mtgnn':
            #     output = self.decoder(encoded_state)
            # else:
            output = self.decoder(encoded_state.unsqueeze(1))
            output = scaler.inverse_transform(output)  # [B, Tout, N, C=1]
            y = scaler.inverse_transform(y)  #
            all_preds.append(output)
            all_targets.append(y)
        
        all_preds = torch.cat(all_preds, dim=0).squeeze()           # [all_sample, T_out, N]
        all_targets = torch.cat(all_targets, dim=0).squeeze()       # [all_sample, T_out, N]

        ex_y_true = all_targets[:,:,0].cpu().numpy()
        ex_y_pred = all_preds[:,:,0].cpu().numpy()
        daf1 = pd.DataFrame(ex_y_true)
        daf2 = pd.DataFrame(ex_y_pred)
        with pd.ExcelWriter(f'result_{self.args.cid}_fedGEM_la.xlsx') as writer:  # 一个excel写入多页数据
            daf1.to_excel(writer, sheet_name='true', float_format='%.6f')
            daf2.to_excel(writer, sheet_name='pred', float_format='%.6f')
        # all_preds = np.concatenate(all_preds, 0).squeeze()
        # all_targets = np.concatenate(all_targets, 0).squeeze()
        #
        # # horizon-wise evaluation
        # metrics = metric(all_preds, all_targets, dim=(0, 2))        # [T_out]
        #
        # head = np.array(['metric'])
        # for k in range(1, self.out_horizon + 1):
        #     head = np.append(head, [f'{k}'])
        # head = np.append(head, ['average'])
        #
        # log = np.zeros([3, self.out_horizon])
        # m_names = []
        #
        # for idx, (k, v) in enumerate(metrics.items()):
        #     m_names.append(k)
        #     log[idx] = metrics[k]
        #
        # m_names = np.expand_dims(m_names, axis=1)
        # avg = np.mean(log, axis=1, keepdims=True)
        # log = np.concatenate([m_names, log, avg], axis=1)           # [3, 1+T+1]
        #
        # print_log = 'Average Test MAE: {:.4f}, Test MAPE: {:.4f}, Test RMSE: {:4f}'
        # print_log_specific = 'MAE at 15 min: {:.4f}, MAE at 30 min: {:.4f}, MAE at 60 min: {:4f}'
        # self.args.logger.info('---------client{}----------'.format(self.args.cid))
        # self.args.logger.info(print_log.format(avg[0,0], avg[1,0], avg[2,0]))
        # self.args.logger.info(print_log_specific.format(metrics['mae'][2], metrics['mae'][5], metrics['mae'][11]))
        # self.args.logger.info(metrics['mae'],metrics['mape'],metrics['rmse'])
        for t in range(y.shape[1]):
            mae, rmse, mape, _, _ = All_Metrics(all_preds[:, t, ...], all_targets[:, t, ...],
                                                self.args.mae_thresh, self.args.mape_thresh)
            self.args.logger.info("Horizon {:02d}, MAE: {:.2f}, RMSE: {:.2f}, MAPE: {:.4f}%".format(
                t + 1, mae, rmse, mape*100))
        mae, rmse, mape, _, _ = All_Metrics(all_preds, all_targets, self.args.mae_thresh, self.args.mape_thresh)
        self.args.logger.info("Average Horizon, MAE: {:.2f}, RMSE: {:.2f}, MAPE: {:.4f}%".format(
                    mae, rmse, mape*100))



        # save_csv_log(self.args, head, log, is_create=True, file_property='result', file_name='result')

    def plot(self):
        plt.figure()
        plt.plot(self.train_loss_list, 'r', label='Train loss')
        plt.plot(self.valid_loss_list, 'g', label='Val loss')
        plt.legend()
        plt.savefig(os.path.join(self.args.vis_dir, self.args.id + '_ft.png'))
        plt.close()
