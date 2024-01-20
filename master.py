'''master.py 运行在主服务器上，用于批量运行实验
'''
import requests
import time
import os
import threading

from calculate import calculate 
from clean_data import clean_data


slaveAddrs = os.environ.get('SLAVES')
masterAddr = os.environ.get('MASTER')


def main():
    topologys = ['hybercube', 'bus', 'ring']
    dims = list(range(2, 11))
    slave_addrs = slaveAddrs.split(":")
    num_slaves = len(slave_addrs)
    addrs = [masterAddr]
    addrs.extend(slave_addrs)
    os.system(f'rm -rf data')
    os.system(f'mkdir data')
    for topology in topologys:
        for dim in dims:
            configFile = f"{topology}-{dim}"
            node = 2 ** dim
            limit_time = int(1e9) * (2 ** dim)
            nodes_num = node // (num_slaves + 1)
            nodes_num = max(1, nodes_num)
            nodes = []
            for i in range(4):
                nodes.extend(addrs[4 * i: 4 * i + node // 4])
            nodes.pop(0)
            for mode in ['mgossip', 'gossip']:
                master_command = f"bash run.sh {mode} config/{configFile}.ini 1 {nodes_num} 1 30000 30500 2 {limit_time}"
                for i in range(20):
                    # 这里另开一个线程的原因是为了快速同步从服务器，使从服务器几乎同步运行对应的命令
                    threading.Thread(target=lambda c: os.system(c), args=(master_command,)).start()
                    for j, slave_addr in enumerate(nodes):
                        slave_command = f"bash run.sh {mode} config/{configFile}.ini {nodes_num * (j + 1) + 1} {nodes_num * (j + 2)} 0 30000 30500 2 {limit_time}"
                        requests.get(f'http://{slave_addr}:30600/execute?command={slave_command}')
                    time.sleep(95)
                    # 开始收集日志
                    for j, slave_addr in enumerate(nodes):
                        for k in range(nodes_num * (j + 1) + 1, nodes_num * (j + 2) + 1):
                            with open(f"{mode}/logs/Node{k}.log", "a") as f:
                                res = requests.get(f'http://{slave_addr}:30600/{mode}/logs/Node{k}.log')
                                f.write(res.content.decode("utf-8"))
                    # 开始计算得到原始实验数据
                    calculate(f"{mode}/logs", 5e8, limit_time, os.path.join('data', f'{mode}-{topology}-{dim}.txt'))
    clean_data('data')
        
        
if __name__ == '__main__':
    main()