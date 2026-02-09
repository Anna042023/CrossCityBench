import torch
import math
import os
import time
import copy
import numpy as np
from lib.TrainInits import MAE_torch, RMSE_torch, MAPE_torch, All_Metrics
from model.STGMAE import AGCRN_Decoder
from model.finetuner import FineTuner
from utils import *
import torch.nn.functional as F
from einops import rearrange, repeat
import pandas as pd
# from utils.log_utils import save_ckpt


class Trainer(object):
    def __init__(self, model, loss, optimizer, train_loader, val_loader, test_loader,
                 scaler, args, lr_scheduler=None, logger=None):
        super(Trainer, self).__init__()
        self.model = model
        self.loss = loss
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.scaler = scaler
        self.args = args
        self.lr_scheduler = lr_scheduler
        self.train_per_epoch = len(train_loader)
        if val_loader != None:
            self.val_per_epoch = len(val_loader)

        # self.pretrained_encoder = copy.deepcopy(self.model).to(torch.float32)
        self.pretrained_encoder = self.model
        self.decoder = AGCRN_Decoder(
            out_dim=args.output_dim,
            rnn_units=args.rnn_units,
            horizon=args.horizon,
            de_mlp=args.de_mlp,
        )

        self.finetuner = FineTuner(
            dataset=args.dataset,
            pretrained_encoder=self.pretrained_encoder,
            decoder=self.decoder,
            loss=args.loss_func,  # for now, just use same loss: mask_mae
            args=args,
            batch_size=args.batch_size,
            learning_rate_enc=args.lr_enc,
            learning_rate_dec=args.lr_dec,
            weight_decay_enc=args.wd_enc,
            weight_decay_dec=args.wd_dec,
            ft=args.ft,  # default, finetuner finetune the model; if not, only train the decoder
            opt_name=args.opt_name,
        )

        #log
        if os.path.isdir(args.log_dir) == False and not args.debug:
            os.makedirs(args.log_dir, exist_ok=True)
        self.logger = logger

    def val_epoch(self, epoch, val_dataloader):
        self.model.eval()
        total_val_loss = 0
        total_mae, total_rmse, total_mape = 0, 0, 0

        with torch.no_grad():
            for batch_idx, (data, target) in enumerate(val_dataloader):
                torch.cuda.empty_cache()
                data = data[..., :self.args.input_dim].to(self.args.device)
                label = target[..., :self.args.output_dim].to(self.args.device)
                # output = self.model(data)
                # # if self.args.real_value:
                # #     label = self.scaler.inverse_transform(label)
                # loss = self.loss(output, label)
                # total_val_loss += loss.item()

                val_loss, val_loss_info,_ = self.model(data)
                total_val_loss += val_loss

                # output = self.scaler.inverse_transform(output)
                # label = self.scaler.inverse_transform(label)
                #
                # total_mae += MAE_torch(output, label).item()
                # total_rmse += RMSE_torch(output, label).item()
                # total_mape += MAPE_torch(output, label).item()

        # mae = total_mae / len(val_dataloader)
        # rmse = total_rmse / len(val_dataloader)
        # mape = total_mape / len(val_dataloader)
        val_loss = total_val_loss / len(val_dataloader)
        self.logger.info('**********Val Epoch {}: Average Loss: {:.6f}'.format(epoch, val_loss))
        # self.logger.info('**********Val Epoch {}: MAE: {:.6f} RMSE: {:.6f} MAPE: {:.6f}'.format(epoch, mae, rmse, mape))
        return val_loss

    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        total_mae, total_rmse, total_mape = 0, 0, 0

        for batch_idx, (data, target) in enumerate(self.train_loader):
            torch.cuda.empty_cache()
            data = data[..., :self.args.input_dim].to(self.args.device) # B, T_in, N, 1
            label = target[..., :self.args.output_dim].to(self.args.device)  # B, T_out, N, 1
            self.optimizer.zero_grad()

            #data and target shape: B, T, N, F; output shape: B, T, N, F
            # output = self.model(data)
            # # if self.args.real_value:
            # #     label = self.scaler.inverse_transform(label)
            #
            # loss = self.loss(output, label)
            loss, loss_info, _ = self.model(data)

            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()

            # output = self.scaler.inverse_transform(output)
            # label = self.scaler.inverse_transform(label)
            #
            # total_mae += MAE_torch(output, label).item()
            # total_rmse += RMSE_torch(output, label).item()
            # total_mape += MAPE_torch(output, label).item()

            #log information
            if batch_idx % self.args.log_step == 0:
                self.logger.info('Train Epoch {}: {}/{} Loss: {:.6f}'.format(
                    epoch, batch_idx, self.train_per_epoch, loss.item()))

        train_epoch_loss = total_loss/self.train_per_epoch
        # mae = total_mae / self.train_per_epoch
        # rmse = total_rmse / self.train_per_epoch
        # mape = total_mape / self.train_per_epoch
        self.logger.info('**********Train Epoch {}: Average Loss: {:.6f}'.format(epoch, train_epoch_loss))
        # self.logger.info('**********Train Epoch {}: MAE: {:.6f} RMSE: {:.6f} MAPE: {:.6f}'.format(epoch, mae, rmse, mape))

        #learning rate decay
        if self.args.lr_decay:
            self.lr_scheduler.step()
        return train_epoch_loss

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
        target = target[..., :1]

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

    def train(self):
        best_model = None
        best_loss = float('inf')
        not_improved_count = 0
        train_loss_list = []
        val_loss_list = []
        start_time = time.time()
        for epoch in range(1, self.args.epochs + 1):
            for ep in range(1, (self.args.local_epochs + 1) if self.args.fedavg else 2):
                torch.cuda.empty_cache()
                #epoch_time = time.time()
                train_epoch_loss = self.train_epoch(epoch)
                #print(time.time()-epoch_time)
                #exit()
                if self.val_loader == None:
                    val_dataloader = self.test_loader
                else:
                    val_dataloader = self.val_loader
                val_epoch_loss = self.val_epoch(epoch, val_dataloader)

                #print('LR:', self.optimizer.param_groups[0]['lr'])
                train_loss_list.append(train_epoch_loss)
                val_loss_list.append(val_epoch_loss)
                if train_epoch_loss > 1e6:
                    self.logger.warning('Gradient explosion detected. Ending...')
                    break
                #if self.val_loader == None:
                #val_epoch_loss = train_epoch_loss
                if val_epoch_loss < best_loss:
                    best_loss = val_epoch_loss
                    not_improved_count = 0
                    best_state = True
                else:
                    not_improved_count += 1
                    best_state = False
                # early stop
                if self.args.early_stop:
                    if not_improved_count == self.args.early_stop_patience:
                        self.logger.info("Validation performance didn\'t improve for {} epochs. "
                                        "Training stops.".format(self.args.early_stop_patience))
                        break
                # save the best state
                if best_state == True:
                    self.logger.info('*********************************Current best model saved!')
                    best_model = copy.deepcopy(self.model.state_dict())
                    # file_name = ['ckpt_' + self.args.cid + '_pt_best.pth.tar', 'ckpt_' + self.args.cid + '_pt_last.pth.tar']
                    save_path = os.path.join('pre-trained', self.args.dataset, str(self.args.num_clients), f'client_{self.args.cid}_16metis.pth')
                    torch.save(best_model, save_path)

            if self.args.fedavg:
                self.model.fedavg()
                self.optimizer = torch.optim.Adam(params=self.model.parameters(), lr=self.args.lr_init, eps=1.0e-8,
                                weight_decay=0, amsgrad=False)

        training_time = time.time() - start_time
        self.logger.info("Total training time: {:.4f}min, best loss: {:.6f}".format((training_time / 60), best_loss))

        # -save the best model to file
        # -if not self.args.debug:
        #  -   torch.save(best_model, self.best_path)
        #  -   self.logger.info("Saving current best model to " + self.best_path)

        #test---------------------------------------------------------------------------------------
        # -best_model_dict = torch.load(save_path, map_location=self.finetuner.device)
        # save_path = os.path.join('pre-trained', self.args.dataset, str(self.args.num_clients),
        #                          f'client_{self.args.cid}_gem_dfsmask.pth')

        self.model.load_state_dict(best_model)
        for param in self.model.parameters():
            print(param.dtype)

        best_finetune_loss = float('inf')
        wait = 0
        for epoch in range(1, self.args.epochs + 1):
            # print(self.finetuner.dtype)
            en_lr, de_lr, epoch_loss, epoch_loss_info, dt = self.finetuner.train(self.train_loader,self.scaler)

            valid_loss_info = self.finetuner.valid(self.val_loader,self.scaler)
            log = 'Epoch: {:03d}, Finetune Train Loss: {:.4f}, Valid Loss: {:.4f}'
            print(log.format(epoch, epoch_loss, valid_loss_info['mae']))

            if valid_loss_info['mae'] < best_finetune_loss:
                is_best = True
                best_finetune_loss = valid_loss_info['mae']
                self.finetuner.best_finetune_loss = best_finetune_loss
                wait = 0
            else:
                is_best = False
                wait += 1
            # ft_save_path = os.path.join('pre-trained', self.args.dataset, str(self.args.num_clients),
            #                          f'client_{self.args.cid}_ft.pth')
            # ft_dict = self.pretrained_encoder.state_dict()
            # torch.save(ft_dict, ft_save_path)
            # file_name = ['ckpt_' + cfg.id + '_ft_best.pth.tar', 'ckpt_' + cfg.id + '_ft_last.pth.tar']
            # save_ckpt(cfg, finetuner, is_best=is_best, file_name=file_name)
            if is_best == True:
                self.logger.info('*********************************Current Finetuner best model saved!')
                best_ft_model = copy.deepcopy(self.pretrained_encoder.state_dict())
                # file_name = ['ckpt_' + self.args.cid + '_pt_best.pth.tar', 'ckpt_' + self.args.cid + '_pt_last.pth.tar']
                save_path = os.path.join('pre-trained', self.args.dataset, str(self.args.num_clients),
                                         f'client_{self.args.cid}_16metis_ft.pth')
                torch.save(best_ft_model, save_path)
        # save_path = os.path.join('pre-trained', self.args.dataset, str(self.args.num_clients),
        #                          f'client_{self.args.cid}_gem_dfsmask_ft.pth')
        # best_ft_dict = torch.load(save_path, map_location=self.finetuner.device)


        self.pretrained_encoder.load_state_dict(best_ft_model)
        # self.test(self.model, self.args, self.test_loader, self.scaler, self.logger)
        self.finetuner.test(self.test_loader, self.scaler)

    def save_checkpoint(self):
        state = {
            'state_dict': self.model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'config': self.args
        }
        torch.save(state, self.best_path)
        self.logger.info("Saving current best model to " + self.best_path)

    @staticmethod
    def test(model, args, data_loader, scaler, logger, path=None):
        if path != None:
            check_point = torch.load(path)
            state_dict = check_point['state_dict']
            args = check_point['config']
            model.load_state_dict(state_dict)
            model.to(args.device)
        model.eval()
        y_pred = []
        y_true = []
        with torch.no_grad():
            for batch_idx, (data, target) in enumerate(data_loader):
                torch.cuda.empty_cache()
                data = data[..., :args.input_dim].to(args.device)
                label = target[..., :args.output_dim].to(args.device)
                # output = model(data, target, teacher_forcing_ratio=0)
                _,_,output = model(data)
                y_true.append(label)
                y_pred.append(output)
        y_true = scaler.inverse_transform(torch.cat(y_true, dim=0))
        y_pred = scaler.inverse_transform(torch.cat(y_pred, dim=0))
        ex_y_true = y_true.cpu().numpy()
        ex_y_pred = y_pred.cpu().numpy()
        daf1 = pd.DataFrame(ex_y_true)
        daf2 = pd.DataFrame(ex_y_pred)
        with pd.ExcelWriter('result_3.xlsx') as writer:  # 一个excel写入多页数据
            daf1.to_excel(writer, sheet_name='page1', float_format='%.6f')
            daf2.to_excel(writer, sheet_name='page2', float_format='%.6f')
        # np.save('./{}_true.npy'.format(args.dataset), y_true.cpu().numpy())
        # np.save('./{}_pred.npy'.format(args.dataset), y_pred.cpu().numpy())
        for t in range(y_true.shape[1]):
            mae, rmse, mape, _, _ = All_Metrics(y_pred[:, t, ...], y_true[:, t, ...],
                                                args.mae_thresh, args.mape_thresh)
            logger.info("Horizon {:02d}, MAE: {:.2f}, RMSE: {:.2f}, MAPE: {:.4f}%".format(
                t + 1, mae, rmse, mape*100))
        mae, rmse, mape, _, _ = All_Metrics(y_pred, y_true, args.mae_thresh, args.mape_thresh)
        logger.info("Average Horizon, MAE: {:.2f}, RMSE: {:.2f}, MAPE: {:.4f}%".format(
                    mae, rmse, mape*100))

    @staticmethod
    def _compute_sampling_threshold(global_step, k):
        """
        Computes the sampling probability for scheduled sampling using inverse sigmoid.
        :param global_step:
        :param k:
        :return:
        """
        return k / (k + math.exp(global_step / k))
    
    def val_epoch_save(self, val_dataloader):
        self.model.eval()

        MAE_per_nodes = [0 for _ in range(self.args.num_nodes)]
        RMSE_per_nodes = [0 for _ in range(self.args.num_nodes)]
        MAPE_per_nodes = [0 for _ in range(self.args.num_nodes)]

        with torch.no_grad():
            for batch_idx, (data, target) in enumerate(val_dataloader):
                torch.cuda.empty_cache()
                data = data[..., :self.args.input_dim].to(self.args.device)
                label = target[..., :self.args.output_dim].to(self.args.device)
                output = self.model(data)

                output = self.scaler.inverse_transform(output)
                label = self.scaler.inverse_transform(label)

                for i in range(self.args.num_nodes):
                    output_i, label_i = output[:,:,i,:], label[:,:,i,:]
                    MAE_per_nodes[i] += MAE_torch(output_i, label_i).item()
                    RMSE_per_nodes[i] += RMSE_torch(output_i, label_i).item()
                    MAPE_per_nodes[i] += MAPE_torch(output_i, label_i).item()


        for i in range(self.args.num_nodes):
            MAE_per_nodes[i] /= len(val_dataloader)
            RMSE_per_nodes[i] /= len(val_dataloader)
            MAPE_per_nodes[i] /= len(val_dataloader)
        torch.save(torch.Tensor([MAE_per_nodes, RMSE_per_nodes, MAPE_per_nodes]), f'Error_{self.args.inter_dropout}.pth')
