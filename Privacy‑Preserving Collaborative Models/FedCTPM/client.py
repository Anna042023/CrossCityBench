
import os
import sys
from lib.client_socket import ClientSocket
file_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(file_dir)
sys.path.append(file_dir)

import torch
import numpy as np
import torch.nn as nn
import argparse
import configparser
from datetime import datetime
# from model.AGCRN import AGCRN as Network
from model.STGMAE import AGCRN as Network
from model.BasicTrainer import Trainer
from lib.TrainInits import init_seed
from lib.dataloader import get_dataloader
from lib.logger import get_logger
from lib.TrainInits import print_model_parameters, get_memory_usage
from data.dividing import *

#*************************************************************************#
DEBUG = 'False'
DEVICE = 'cuda:0'

# DATASET = sys.argv[1] # PeMSD4 or PeMSD7 or PeMSD8 or METRLA or PEMSBAY
# del sys.argv[1]
# MODE = sys.argv[1] # CTR SGL FED
# del sys.argv[1]

DATASET = "METR_LA"
MODE = "FED"
#*************************************************************************#


def main(args):
    #load dataset
    train_loader, val_loader, test_loader, scaler = get_dataloader(args,
                                                            normalizer=args.normalizer,
                                                            single=False)
    #init model
    model = Network(args)
    model = model.to(args.device)
    for p in model.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform_(p)
        else:
            nn.init.uniform_(p)
    # print_model_parameters(model, only_num=False)
    args.logger.info(f"memory_usage: {get_memory_usage('cuda')}")

    #init loss function, optimizer
    if args.loss_func == 'mask_mae':
        from lib.metrics import MAE_torch
        def masked_mae_loss(scaler, mask_value):
            def loss(preds, labels):
                if scaler:
                    preds = scaler.inverse_transform(preds)
                    labels = scaler.inverse_transform(labels)
                mae = MAE_torch(pred=preds, true=labels, mask_value=mask_value)
                return mae
            return loss
        loss = masked_mae_loss(scaler, mask_value=0.0)
    elif args.loss_func == 'mae':
        loss = torch.nn.L1Loss().to(args.device)
    elif args.loss_func == 'mse':
        loss = torch.nn.MSELoss().to(args.device)
    elif args.loss_func == 'smae':
        loss = torch.nn.SmoothL1Loss().to(args.device)
    else:
        raise ValueError

    optimizer = torch.optim.Adam(params=model.parameters(), lr=args.lr_init, eps=1.0e-8,
                                weight_decay=0, amsgrad=False)
    #learning rate decay
    lr_scheduler = None
    if args.lr_decay:
        args.logger.info('Applying learning rate decay.')
        lr_decay_steps = [int(i) for i in list(args.lr_decay_step.split(','))]
        lr_scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer=optimizer,
                                                            milestones=lr_decay_steps,
                                                            gamma=args.lr_decay_rate)

    #start training
    trainer = Trainer(model, loss, optimizer, train_loader, val_loader, test_loader, scaler,
                    args, lr_scheduler=lr_scheduler, logger=args.logger)


    print_model_parameters(model, trainer.logger, only_num=False)
    
    if args.mode == 'train':
        trainer.train()

    elif args.mode == 'test':

        model.load_state_dict(torch.load(os.path.join('pre-trained', args.dataset, str(args.num_clients), f'client_{args.cid}_ft.pth')))
        args.logger.info("Load saved model")
        trainer.test(model, trainer.args, test_loader, scaler, trainer.logger)
        # finetuner.test(self.test_loader, self.scaler)
    else:
        raise ValueError



if __name__ == "__main__":
    #get configuration
    config_file = './config/{}.conf'.format(DATASET)
    # config_file = './config/{}_{}.conf'.format(DATASET, MODE)
    print('Read configuration file: %s' % (config_file))
    config = configparser.ConfigParser()
    config.read(config_file)

    args = argparse.ArgumentParser(description='arguments')

    # CTR SGL FED config
    args.add_argument('--num_clients', default=4, type=int)
    args.add_argument('--cid', default=4, type=int)
    args.add_argument('--divide', default="metis", type=str)

    # FED config
    args.add_argument('--fedavg', default=False, action='store_true')
    args.add_argument('--active_mode', default='adptpolu', choices=['softmax', 'sprtrelu', 'adptpolu'])
    args.add_argument('--act_k', default=2, type=int)
    args.add_argument('--local_epochs', default=2, type=int)
    args.add_argument('-sp', dest='server_port',default=50019)
    args.add_argument('-sip', dest='server_ip',default='127.0.0.1')
    args.add_argument('-cp', dest='self_port',default=50018)

    args.add_argument('--dataset', default=DATASET, type=str)
    args.add_argument('--exp_mode', default=MODE, choices=['CTR', 'SGL', 'FED'])
    #data
    args.add_argument('--num_nodes', default=config['data']['num_nodes'], type=int)
    args.add_argument('--lag', default=config['data']['lag'], type=int)
    args.add_argument('--horizon', default=config['data']['horizon'], type=int)
    args.add_argument('--val_ratio', default=config['data']['val_ratio'], type=float)
    args.add_argument('--test_ratio', default=config['data']['test_ratio'], type=float)

    args.add_argument('--normalizer', default=config['data']['normalizer'], type=str)
    args.add_argument('--column_wise', default=config['data']['column_wise'], type=eval)
    #model
    args.add_argument('--embed_dim', default=config['model']['embed_dim'], type=int)
    args.add_argument('--rnn_units', default=config['model']['rnn_units'], type=int)
    args.add_argument('--num_layers', default=config['model']['num_layers'], type=int)
    args.add_argument('--stru_dec_drop', default=config['model']['stru_dec_drop'], type=float)
    args.add_argument('--stru_dec_proj', default=config['model']['stru_dec_proj'], type=bool)

    #----------------------------------
    # args.add_argument('--mode', default='train') # mode can be pt: pretrain, ft: finetune, or train: do both
    args.add_argument('--load_pt', action='store_true', default=False)  # for continuous training in pretraining stage
    args.add_argument('--load_ft', action='store_true', default=False)  # for continuous training in finetuning stage
    args.add_argument('--load_best', action='store_true', default=False)  # for continuous training in finetuning stage
    #---------------------------------

    # args.add_argument('--mp_num_workers', default=config['model']['mp_num_workers'], type=int)
    args.add_argument('--accelerate', default=config['model']['accelerate'], type=eval)

    args.add_argument('--input_dim', default=config['model']['input_dim'], type=int)
    args.add_argument('--output_dim', default=config['model']['output_dim'], type=int)
    args.add_argument('--cheb_k', default=config['model']['cheb_order'], type=int)
    #train
    args.add_argument('--batch_size', default=config['train']['batch_size'], type=int)
    args.add_argument('--epochs', default=config['train']['epochs'], type=int)
    args.add_argument('--lr_init', default=config['train']['lr_init'], type=float)
    args.add_argument('--num_runs', default=config['train']['num_runs'], type=int)

    args.add_argument('--loss_func', default=config['train']['loss_func'], type=str)
    args.add_argument('--seed', default=config['train']['seed'], type=int)
    args.add_argument('--lr_decay', default=config['train']['lr_decay'], type=eval)
    args.add_argument('--lr_decay_rate', default=config['train']['lr_decay_rate'], type=float)
    args.add_argument('--lr_decay_step', default=config['train']['lr_decay_step'], type=str)
    args.add_argument('--early_stop', default=config['train']['early_stop'], type=eval)
    args.add_argument('--early_stop_patience', default=config['train']['early_stop_patience'], type=int)
    args.add_argument('--grad_norm', default=config['train']['grad_norm'], type=eval)
    args.add_argument('--max_grad_norm', default=config['train']['max_grad_norm'], type=int)
    args.add_argument('--real_value', default=config['train']['real_value'], type=eval, help = 'use real value for loss calculation')
    #test
    args.add_argument('--mae_thresh', default=config['test']['mae_thresh'], type=eval)
    args.add_argument('--mape_thresh', default=config['test']['mape_thresh'], type=float)
    #log
    args.add_argument('--log_dir', default='./', type=str)
    args.add_argument('--log_step', default=config['log']['log_step'], type=int)
    args.add_argument('--plot', default=config['log']['plot'], type=eval)
    #static
    args.add_argument('--mode', default='train', type=str)
    args.add_argument('--device', default=DEVICE, type=str, help='indices of GPUs')
    args.add_argument('--debug', default=DEBUG, type=eval)
    args.add_argument('--cuda', default=True, type=bool)

    # args.add_argument('--opt_name', default=config['train']['grad_norm'], type=str)
    args.add_argument('--pt_lr', default=config['train']['pt_lr'], type=float)
    args.add_argument('--pt_wd', default=config['train']['pt_wd'], type=int)
    args.add_argument('--train_epoch', default=config['train']['train_epoch'], type=int)
    args.add_argument('--pt_sched_policy', default=config['train']['pt_sched_policy'], type=str)
    args.add_argument('--pt_num_epoch_fix_lr', default=config['train']['pt_num_epoch_fix_lr'], type=int)
    args.add_argument('--pt_decay_step', default=config['train']['pt_decay_step'], type=int)
    args.add_argument('--pt_gamma', default=config['train']['pt_gamma'], type=int)
    args.add_argument('--pt_milestones', default=config['train']['pt_milestones'], type=str)
    args.add_argument('--pt_clip_grad', default=config['train']['pt_clip_grad'], type=str)

    args.add_argument('--de_mlp', default=config['train']['de_mlp'], type=bool)
    args.add_argument('--ft', default=config['train']['ft'], type=bool)
    args.add_argument('--lr_enc', default=config['train']['lr_enc'], type=float)
    args.add_argument('--lr_dec', default=config['train']['lr_dec'], type=float)
    args.add_argument('--wd_enc', default=config['train']['wd_enc'], type=int)
    args.add_argument('--wd_dec', default=config['train']['wd_dec'], type=int)
    args.add_argument('--ft_epoch', default=config['train']['ft_epoch'], type=int)
    args.add_argument('--ft_sched_policy', default=config['train']['ft_sched_policy'], type=str)
    args.add_argument('--ft_num_epoch_fix_lr', default=config['train']['ft_num_epoch_fix_lr'], type=int)
    args.add_argument('--ft_decay_step', default=config['train']['ft_decay_step'], type=int)
    args.add_argument('--ft_gamma', default=config['train']['ft_gamma'], type=int)
    args.add_argument('--ft_milestones', default=config['train']['ft_milestones'], type=str)
    args.add_argument('--ft_clip_grad', default=config['train']['ft_clip_grad'], type=str)
    args.add_argument('--patience', default=config['train']['patience'], type=int)
    args.add_argument('--opt_name', default=config['train']['opt_name'], type=str)
    args.add_argument('--eps_enc', default=config['train']['eps_enc'], type=float)
    args.add_argument('--eps_dec', default=config['train']['eps_dec'], type=float)
    args.add_argument('--pt_eps', default=config['train']['pt_eps'], type=float)

    args = args.parse_args()

    args.socket = ClientSocket(int(args.cid), int(args.server_port), int(args.self_port), server_ip=args.server_ip)

    init_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.set_device(int(args.device[5]))
    else:
        args.device = 'cpu'


    args.nodes_per = eval(f"{DATASET}_{args.num_clients}p_{args.divide}")
    args.nodes = args.nodes_per[args.cid-1]
    args.num_nodes = len(args.nodes)


    #config log path
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    current_dir = os.path.dirname(os.path.realpath(__file__))

    args.log_dir = os.path.join(current_dir, 'log', f"in{args.lag}_out{args.horizon}")

    args.logger = get_logger(args, args.log_dir, debug=args.debug)
    args.logger.info('Experiment log path in: {}'.format(args.log_dir))


    for _ in range(args.num_runs):
        main(args)
    # sys.exit()

