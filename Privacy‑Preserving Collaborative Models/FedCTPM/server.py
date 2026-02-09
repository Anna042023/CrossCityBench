from lib.server_socket import ServerSocket
import argparse
import time
import copy
import torch
import collections
# TODO: FedAvg聚合算法
def FedAvg(w):
    w_avg = copy.deepcopy(w[0])
    for k in w_avg.keys():
        for i in range(1, len(w)):
            w_avg[k] += w[i][k]
        w_avg[k] = torch.div(w_avg[k], len(w))
    return w_avg
# TODO: 服务器类
class Server():
    def __init__(self, n_clients, port, ip):
        self.socket = ServerSocket(n_clients, port, ip)
        while True:
            # 接收来自客户端的消息列表,每个消息是一个字典  
            rcvd_msgs = self.socket.recv()
            # 如果消息列表不为空
            if rcvd_msgs:
                # 如果消息列表中的第一个元素是字典,则使用FedAvg算法进行聚合
                if type(rcvd_msgs[0])==collections.OrderedDict or type(rcvd_msgs[0])==dict:
                    self.socket.send(FedAvg(rcvd_msgs))
                # 如果是其他类型（如数值或张量），则直接求和
                else:
                    self.socket.send(sum(rcvd_msgs))
            else:
                print("[SERVER RECVED NONE]")
                self.socket.close()
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', dest='n',default=8)
    parser.add_argument('-p', dest='port',default=50019)
    parser.add_argument('-i', dest='ip',default='127.0.0.1')
    args = parser.parse_args()

    server = Server(n_clients=int(args.n), port=int(args.port), ip=args.ip)