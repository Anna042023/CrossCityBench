import numpy as np

def Add_Window_Horizon(data, window=3, horizon=1, single=False):
    '''
        此函数用于将输入的时间序列数据转换为具有特定窗口长度和预测步长的输入输出对。
        常用于时间序列预测任务中，将原始数据转换为适合模型训练的格式。

        :param data: 输入的时间序列数据，形状为 [B, ...]，其中 B 表示时间步的数量。
        :param window: 窗口长度，即用于预测的历史时间步的数量，默认值为 3。
        :param horizon: 预测步长，即需要预测的未来时间步的数量，默认值为 1。
        :param single: 一个布尔值，用于指定预测方式。
                    如果为 True,则每次只预测一个未来时间步；
                    如果为 False,则预测 horizon 个未来时间步，默认值为 False。
        :return: X 是形状为 [B, W, ...] 的输入数据，其中 W 是窗口长度；
                Y 是形状为 [B, H, ...] 的目标数据，其中 H 是预测步长。
    '''
    # 获取输入数据的时间步数量
    length = len(data)
    # 计算循环的结束索引，确保在提取窗口和预测步长时不会超出数据的范围
    end_index = length - horizon - window + 1
    # 初始化用于存储窗口数据的列表
    X = []      
    # 初始化用于存储预测步长数据的列表
    Y = []      
    # 初始化用于遍历数据的索引，初始值为 0
    index = 0
    # 如果 single 为 True，则每次只预测一个未来时间步
    if single:
        # 当索引小于结束索引时，继续循环
        while index < end_index:
            # 将长度为 window 的历史数据添加到 X 列表中
            X.append(data[index:index+window])
            # 将 index+window+horizon-1 时刻的数据添加到 Y 列表中
            Y.append(data[index+window+horizon-1:index+window+horizon])
            # 索引加 1
            index = index + 1
    # 如果 single 为 False，则预测 horizon 个未来时间步
    else:
        # 当索引小于结束索引时，继续循环
        while index < end_index:
            # 将长度为 window 的历史数据添加到 X 列表中
            X.append(data[index:index+window])
            # 将从 index+window 到 index+window+horizon 时刻的数据添加到 Y 列表中
            Y.append(data[index+window:index+window+horizon])
            # 索引加 1
            index = index + 1
    # 将存储窗口数据的列表 X 转换为 NumPy 数组
    X = np.array(X)
    # 将存储预测步长数据的列表 Y 转换为 NumPy 数组
    Y = np.array(Y)
    # 返回转换后的输入输出对 X 和 Y
    return X, Y