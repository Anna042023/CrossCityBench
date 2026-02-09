import os
import numpy as np
import pandas as pd

import torch
import pickle
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
'''
    input:mean, std
    output:StandardScaler to transform and inverse_transform data
'''
#! 这个类用于对数据进行标准化处理，即把数据转换为均值为 0，标准差为 1 的分布。
class StandardScaler():
    def __init__(self, mean, std):
        # 初始化类的实例，接收均值 mean 和标准差 std 作为参数
        # 并将它们存储为实例的属性
        self.mean = mean
        self.std = std

    def transform(self, data):
        # 对输入的数据 data 进行标准化处理
        # 标准化公式为 (数据 - 均值) / 标准差
        return (data - self.mean) / self.std

    def inverse_transform(self, data):
        # 对标准化后的数据 data 进行逆标准化处理
        # 逆标准化公式为 (数据 * 标准差) + 均值
        return (data * self.std) + self.mean

#! 这个类用于创建自定义的数据加载器，它可以将数据分成批量，并支持数据洗牌操作。
class CustomDataLoader(object):
    def __init__(self, xs, ys, batch_size, pad_with_last_sample=True, device=None, dtype=None):
        # 初始化类的实例，接收输入数据 xs、目标数据 ys、批量大小 batch_size
        # pad_with_last_sample 表示是否用最后一个样本填充数据，使其能被批量大小整除
        # device 表示数据要移动到的设备（如 'cuda' 或 'cpu'）
        # dtype 表示数据的类型
        self.batch_size = batch_size
        self.current_ind = 0
        if pad_with_last_sample:
            # 计算需要填充的样本数量(len(xs):100,batch_size=64)
            # num_padding = (64-100%64)%64=28
            num_padding = (batch_size - (len(xs) % batch_size)) % batch_size
            # 复制最后一个样本进行填充
            x_padding = np.repeat(xs[-1:], num_padding, axis=0)
            y_padding = np.repeat(ys[-1:], num_padding, axis=0)
            # 将填充后的数据与原数据拼接
            xs = np.concatenate([xs, x_padding], axis=0)
            ys = np.concatenate([ys, y_padding], axis=0)
        # 数据的总样本数
        self.size = len(xs)
        # 总批量数
        self.num_batch = int(self.size // self.batch_size)
        # 将数据转换为 PyTorch 张量，并移动到指定设备和类型
        self.xs = torch.from_numpy(xs).to(device).to(dtype)
        self.ys = torch.from_numpy(ys).to(device).to(dtype)

    def shuffle(self):
        # 对数据进行洗牌操作，打乱数据的顺序
        # 生成一个随机排列的索引数组
        permutation = np.random.permutation(self.size)
        # 根据随机排列的索引重新排列数据
        xs, ys = self.xs[permutation], self.ys[permutation]
        self.xs = xs
        self.ys = ys

    def get_iterator(self):
        # 返回一个迭代器，用于按批量迭代数据
        self.current_ind = 0

        def _wrapper():
            # 内部函数，用于生成批量数据
            while self.current_ind < self.num_batch:
                # 计算当前批量的起始索引
                start_ind = self.batch_size * self.current_ind
                # 计算当前批量的结束索引
                end_ind = min(self.size, self.batch_size * (self.current_ind + 1))
                # 提取当前批量的输入数据和目标数据
                x_i = self.xs[start_ind: end_ind, ...]
                y_i = self.ys[start_ind: end_ind, ...]
                # 生成当前批量的数据
                yield (x_i, y_i)
                # 移动到下一个批量
                self.current_ind += 1

        return _wrapper()

#! 这个类用于创建预训练阶段的自定义数据加载器，与 CustomDataLoader 类似，但只处理输入数据。
class CustomPretrainDataLoader(object):
    def __init__(self, xs, batch_size, pad_with_last_sample=True):
        # 初始化类的实例，接收输入数据 xs、批量大小 batch_size
        # pad_with_last_sample 表示是否用最后一个样本填充数据，使其能被批量大小整除
        self.batch_size = batch_size
        self.current_ind = 0
        if pad_with_last_sample:
            # 计算需要填充的样本数量
            num_padding = (batch_size - (len(xs) % batch_size)) % batch_size
            # 复制最后一个样本进行填充
            x_padding = np.repeat(xs[-1:], num_padding, axis=0)
            # 将填充后的数据与原数据拼接
            xs = np.concatenate([xs, x_padding], axis=0)
        # 数据的总样本数
        self.size = len(xs)
        # 总批量数
        self.num_batch = int(self.size // self.batch_size)
        # 存储输入数据
        self.xs = xs

    def shuffle(self):
        # 对数据进行洗牌操作，打乱数据的顺序
        # 生成一个随机排列的索引数组
        permutation = np.random.permutation(self.size)
        # 根据随机排列的索引重新排列数据
        xs = self.xs[permutation]
        self.xs = xs

    def get_iterator(self):
        # 返回一个迭代器，用于按批量迭代数据
        self.current_ind = 0

        def _wrapper():
            # 内部函数，用于生成批量数据
            while self.current_ind < self.num_batch:
                # 计算当前批量的起始索引
                start_ind = self.batch_size * self.current_ind
                # 计算当前批量的结束索引
                end_ind = min(self.size, self.batch_size * (self.current_ind + 1))
                # 提取当前批量的输入数据
                x_i = self.xs[start_ind: end_ind, ...]
                # 生成当前批量的数据
                yield x_i
                # 移动到下一个批量
                self.current_ind += 1

        return _wrapper()

#! 这个类继承自 torch.utils.data.Dataset，用于创建预训练数据集。
class PretrainDataset(Dataset):
    def __init__(
        self, dataset_name, traj_len, dtype='float32', *args, **kwargs
    ):
        # 初始化类的实例，接收数据集名称 dataset_name、轨迹长度 traj_len
        # dtype 表示数据的类型
        self.dataset_name = dataset_name
        self.traj_len = traj_len
        # 根据输入的 dtype 确定数据类型
        self.dtype = np.float64 if dtype.lower() == 'float64' else np.float32
        # 准备数据
        self.data = self._prepare_data()
        # 生成数据段
        self.segments = self._generate_segments()

    def _prepare_data(self):
        #? 从文件中加载数据
        data = np.load(os.path.join('./data/', self.dataset_name, 'traj.npz'))['x']
        return data

    def _generate_segments(self):
        # 生成数据段的起始和结束索引
        segments = [(init, init + self.traj_len) for init in range(0, self.data.shape[0] - self.traj_len + 1)]
        return segments

    def _get_segments(self, init, end):
        # 根据起始和结束索引提取数据段
        traj = self.data[init:end,...]
        return traj

    def __getitem__(self, index):
        # 根据索引获取数据段
        (init, end) = self.segments[index]
        traj = self._get_segments(init, end)
        return traj

    def __len__(self):
        # 返回数据集的长度
        return len(self.segments)

#! 这个函数用于生成预训练数据。
def generate_pretrain_data(dataset_name, traj_len):
    """
    return: [all, traj_len, N, C]
    """
    #? 从文件中加载原始数据
    raw_data = np.load(os.path.join('./data/', dataset_name, 'traj.npz'))['x']
    # 生成数据段的起始和结束索引
    segments = np.array([(init, init + traj_len) for init in range(0, raw_data.shape[0] - traj_len + 1)])
    # 提取起始索引
    start_indices = segments[:, 0]
    # 提取结束索引
    end_indices = segments[:, 1]
    # 数据段的总数量
    all_length = len(start_indices)
    # 数据段的最大长度
    T = np.max(end_indices - start_indices)
    # 生成数据段的索引数组
    segment_indices = np.arange(T)[None, :] + start_indices[:, None]
    # 根据索引数组提取数据段
    new_data = raw_data[segment_indices]
    return new_data

#! 这个函数用于加载数据集，包括训练集、验证集和测试集，并对数据进行标准化处理。
def load_dataset(dataset_dir, batch_size, valid_batch_size=None, test_batch_size=None, device=None, dtype=None):
    data = {}
    for category in ['train', 'val', 'test']:
        # 从文件中加载不同类别的数据
        cat_data = np.load(os.path.join(dataset_dir, category + '.npz'))
        data['x_' + category] = cat_data['x']
        data['y_' + category] = cat_data['y']
    # 创建标准化器，使用训练数据的均值和标准差
    scaler = StandardScaler(mean=data['x_train'][..., 0].mean(), std=data['x_train'][..., 0].std())
    # 对不同类别的数据进行标准化处理
    for category in ['train', 'val', 'test']:
        data['x_' + category][..., 0] = scaler.transform(data['x_' + category][..., 0])
    # 创建训练数据加载器
    data['train_loader'] = CustomDataLoader(data['x_train'], data['y_train'], batch_size, device=device, dtype=dtype)
    # 创建验证数据加载器
    data['val_loader'] = CustomDataLoader(data['x_val'], data['y_val'], valid_batch_size, device=device, dtype=dtype)
    # 创建测试数据加载器
    data['test_loader'] = CustomDataLoader(data['x_test'], data['y_test'], test_batch_size, device=device, dtype=dtype)
    # 存储标准化器
    data['scaler'] = scaler
    return data

#! 这个函数用于加载预训练数据集，并对数据进行标准化处理。
def load_pretrain_dataset(dataset_name, traj_len, batch_size, valid_batch_size=None, test_batch_size=None):
    data = {}
    # 生成预训练数据
    data['x_train'] = generate_pretrain_data(dataset_name, traj_len)
    # 创建标准化器，使用训练数据的均值和标准差
    scaler = StandardScaler(mean=data['x_train'][..., 0].mean(), std=data['x_train'][..., 0].std())
    # 对训练数据进行标准化处理
    for category in ['train']:
        data['x_' + category][..., 0] = scaler.transform(data['x_' + category][..., 0])
    # 创建预训练数据加载器
    data['train_loader'] = CustomPretrainDataLoader(data['x_train'], batch_size)
    # 存储标准化器
    data['scaler'] = scaler
    return data
