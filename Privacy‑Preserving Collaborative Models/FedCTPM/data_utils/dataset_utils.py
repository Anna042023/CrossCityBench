import os
import sys 
import torch
import pickle
import numpy as np
import scipy.sparse as sp
from scipy.sparse import linalg
'''
    计算对称邻接矩阵的相关函数
'''
#! 计算对称邻接矩阵
def sym_adj(adj):
    # 将输入的邻接矩阵转换为COO格式的稀疏矩阵
    adj = sp.coo_matrix(adj)
    # 计算每一行的元素之和
    rowsum = np.array(adj.sum(1))
    # 计算每一行元素之和的负0.5次方，并将结果展平为一维数组
    d_inv_sqrt = np.power(rowsum, -0.5).flatten()
    # 将无穷大的值替换为0
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    # 创建一个对角矩阵，对角元素为d_inv_sqrt
    d_mat_inv_sqrt = sp.diags(d_inv_sqrt)
    # 计算对称邻接矩阵，将结果转换为浮点32位的密集矩阵
    return adj.dot(d_mat_inv_sqrt).transpose().dot(d_mat_inv_sqrt).astype(np.float32).todense()

#! 计算非对称邻接矩阵
def asym_adj(adj):
    # 将输入的邻接矩阵转换为COO格式的稀疏矩阵
    adj = sp.coo_matrix(adj)
    # 计算每一行的元素之和，并将结果展平为一维数组
    rowsum = np.array(adj.sum(1)).flatten()
    # 计算每一行元素之和的负1次方，并将结果展平为一维数组
    d_inv = np.power(rowsum, -1).flatten()
    # 将无穷大的值替换为0
    d_inv[np.isinf(d_inv)] = 0.
    # 创建一个对角矩阵，对角元素为d_inv
    d_mat= sp.diags(d_inv)
    # 计算非对称邻接矩阵，将结果转换为浮点32位的密集矩阵
    return d_mat.dot(adj).astype(np.float32).todense()

#! 计算归一化拉普拉斯矩阵
def calculate_normalized_laplacian(adj):
    # 将输入的邻接矩阵转换为COO格式的稀疏矩阵
    adj = sp.coo_matrix(adj)
    # 计算每一行的元素之和
    d = np.array(adj.sum(1))
    # 计算每一行元素之和的负0.5次方，并将结果展平为一维数组
    d_inv_sqrt = np.power(d, -0.5).flatten()
    # 将无穷大的值替换为0
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    # 创建一个对角矩阵，对角元素为d_inv_sqrt
    d_mat_inv_sqrt = sp.diags(d_inv_sqrt)
    # 计算归一化拉普拉斯矩阵，并将结果转换为COO格式的稀疏矩阵
    normalized_laplacian = sp.eye(adj.shape[0]) - adj.dot(d_mat_inv_sqrt).transpose().dot(d_mat_inv_sqrt).tocoo()
    return normalized_laplacian

#! 计算缩放后的拉普拉斯矩阵
def calculate_scaled_laplacian(adj_mx, lambda_max=2, undirected=True):
    # 如果图是无向图，取邻接矩阵和其转置的逐元素最大值
    if undirected:
        adj_mx = np.maximum.reduce([adj_mx, adj_mx.T])
    # 计算归一化拉普拉斯矩阵
    L = calculate_normalized_laplacian(adj_mx)
    # 如果没有指定最大特征值，则计算最大特征值
    if lambda_max is None:
        lambda_max, _ = linalg.eigsh(L, 1, which='LM')
        lambda_max = lambda_max[0]
    # 将归一化拉普拉斯矩阵转换为CSR格式的稀疏矩阵
    L = sp.csr_matrix(L)
    # 获取矩阵的行数
    M, _ = L.shape
    # 创建一个单位矩阵，格式为CSR，数据类型与L相同
    I = sp.identity(M, format='csr', dtype=L.dtype)
    # 计算缩放后的拉普拉斯矩阵
    L = (2 / lambda_max * L) - I
    # 将结果转换为浮点32位的密集矩阵
    return L.astype(np.float32).todense()

#! 加载pickle文件
def load_pickle(pickle_file):
    try:
        # 以二进制只读模式打开pickle文件
        with open(pickle_file, 'rb') as f:
            # 加载pickle文件中的数据
            pickle_data = pickle.load(f)
    except UnicodeDecodeError as e:
        # 如果出现Unicode解码错误，以指定编码重新加载文件
        with open(pickle_file, 'rb') as f:
            pickle_data = pickle.load(f, encoding='latin1')
    except Exception as e:
        # 如果出现其他异常，打印错误信息并抛出异常
        print('Unable to load data ', pickle_file, ':', e)
        raise
    return pickle_data

#! 加载邻接矩阵，并根据指定的类型进行处理
def load_adj(data_name, adjtype=None):
    """
    load adj, then process it according to adjtype
    """
    # 根据数据集名称确定邻接矩阵文件的路径
    if data_name == 'pems_03':
        data_path = './data/pems_03/adj_mx_03.pkl'
    elif data_name == 'pems_04':
        data_path = './data/pems_04/adj_mx_04.pkl'
    elif data_name == 'pems_07':
        data_path = './data/pems_07/adj_mx_07.pkl'
    elif data_name == 'pems_08':
        data_path = './data/pems_08/adj_mx_08.pkl'
    else:
        # 如果数据集名称不匹配，抛出未实现错误
        raise NotImplementedError
    # 加载pickle文件中的传感器ID、传感器ID到索引的映射和邻接矩阵
    sensor_ids, sensor_id_to_ind, adj_mx = load_pickle(data_path)
    # 根据指定的邻接矩阵类型进行处理
    if adjtype == "scalap":
        # 计算缩放后的拉普拉斯矩阵
        adj = [calculate_scaled_laplacian(adj_mx)]
    elif adjtype == "normlap":
        # 计算归一化拉普拉斯矩阵，并转换为浮点32位的密集矩阵
        adj = [calculate_normalized_laplacian(adj_mx).astype(np.float32).todense()]
    elif adjtype == "symnadj":
        # 计算对称邻接矩阵
        adj = [sym_adj(adj_mx)]
    elif adjtype == "transition":
        # 计算非对称邻接矩阵
        adj = [asym_adj(adj_mx)]
    elif adjtype == "doubletransition":
        # 计算非对称邻接矩阵和其转置的非对称邻接矩阵
        adj = [asym_adj(adj_mx), asym_adj(np.transpose(adj_mx))]
    elif adjtype == "identity":
        # 创建一个单位矩阵
        adj = [np.diag(np.ones(adj_mx.shape[0])).astype(np.float32)]
    else:
        # 如果未指定类型，直接使用原始邻接矩阵
        adj = adj_mx
    return sensor_ids, sensor_id_to_ind, adj