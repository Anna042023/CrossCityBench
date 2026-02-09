import pickle, struct, socket
import argparse, time

# TODO:  定义客户端套接字类，用于与服务器进行通信
class ClientSocket():
    def __init__(self, client_id, server_port, self_port, server_ip='127.0.0.1', self_ip='127.0.0.1'):
        # 初始化客户端的相关信息
        self.client_id = client_id
        self.server_port = server_port
        self.self_port = self_port
        self.server_ip = server_ip
        self.self_ip = self_ip

        # 创建一个 TCP 套接字对象
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 以下几行代码被注释掉，可根据需求启用
        # self.socket.settimeout(9999)  # 设置套接字超时时间
        # self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # 设置 TCP 选项
        # self.socket.bind((self.self_ip, self.self_port))  # 绑定本地地址和端口

        # 记录开始连接服务器的信息
        self.log_info(f"start connect")
        # 连接到服务器
        self.socket.connect((self.server_ip, self.server_port))
        # 记录发送消息的信息
        self.log_info(f"send msg")
        # 向服务器发送客户端 ID
        self.send(client_id)
        # 接收服务器的响应并记录信息
        self.log_info(self.recv())
    
    def send(self, msg):
        # 使用 pickle 将消息对象序列化为字节流
        msg = pickle.dumps(msg)
        # 获取消息的长度
        data_len = len(msg)
        # 使用 struct 模块将消息长度打包为 4 字节的整数
        header = struct.pack('i', data_len)
        # 先发送消息长度
        self.socket.send(header)
        # 再发送消息内容
        self.socket.send(msg)
        # 返回消息的长度
        return data_len

    def recv(self):
        while True:
            # 接收 4 字节的消息长度信息，使用 MSG_WAITALL 确保接收到完整的 4 字节
            data_len = self.socket.recv(4, socket.MSG_WAITALL)
            # 以下代码被注释掉，可根据需求启用
            # data_len = self.socket.recv(4)
            # 当接收到的长度信息不为空且长度为 4 字节时，跳出循环
            if data_len != None and len(data_len)==4:
                # 记录接收到的消息长度信息
                self.log_info(f"data_len: {data_len}")
                break
            else:
                # 若未接收到完整的长度信息，等待 0.01 秒后继续尝试接收
                time.sleep(0.01)
        # 使用 struct 模块将接收到的长度信息解包为整数
        data_len = struct.unpack('i', data_len)[0]
        # 记录解包后的消息长度信息
        self.log_info(f"data_len: {data_len}")
        # 接收指定长度的消息内容，使用 MSG_WAITALL 确保接收到完整的消息
        recv_data = self.socket.recv(data_len, socket.MSG_WAITALL)
        # 以下代码被注释掉，可根据需求启用
        # recv_data = self.socket.recv(data_len)
        # 使用 pickle 将接收到的字节流反序列化为对象
        recv_data = pickle.loads(recv_data)
        # 返回反序列化后的对象
        return recv_data
    
    def log_info(self, info, on=False):
        # 若 on 为 True，则打印带有客户端 ID 的日志信息
        if on:
            print(f"[CLIENT_{self.client_id}] {info}")
    
    def close(self):
        # 关闭客户端套接字
        self.socket.close()
    

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser()
    # 添加客户端 ID 参数
    parser.add_argument('-c', dest='cid')
    # 添加服务器端口参数
    parser.add_argument('-sp', dest='server_port')
    # 添加客户端自身端口参数
    parser.add_argument('-cp', dest='self_port')
    # 解析命令行参数
    args = parser.parse_args()

    # 创建客户端套接字对象
    client = ClientSocket(int(args.cid), int(args.server_port), int(args.self_port))