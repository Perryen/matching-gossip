'''master.py 运行在主服务器上，用于批量运行实验
'''
import requests
import time
import os
import threading

from calculate.py import calculate 


slaveAddrs = os.environ.get('SLAVES')


def main():
    
    configFiles = [
        'bus', 'ring', 'hybercube-2', 'hybercube-3', 'hybercube-4', 'hybercube-5',          
        'hybercube-6', 'hybercube-7', 'hybercube-8', 'hybercube-9'
    ]
    nodes = [16, 16, 4, 8, 16, 32, 64, 128, 256, 512]
    slave_addrs = slaveAddrs.split(":")
    num_slaves = len(slave_addrs)
    os.system(f'rm -rf data-2')
    os.system(f'mkdir data-2')
    limit_times = [1e9, 1e9, 1e9, 1e9, 1e9, 2e9, 3e9, 4e9, 8e9, 1e10]
    for configFile, node, limit_time in zip(configFiles, nodes, limit_times):
        for mode in ['mgossip', 'gossip']:
            master_command = f"bash run.sh {mode} config/{configFile}.ini 1 {node // num_slaves} 1 30000 30500 2 {limit_time}"
            for i in range(20):
                # 这里另开一个线程的原因是为了快速同步从服务器，使从服务器几乎同步运行对应的命令
                threading.Thread(target=lambda c: os.system(c), args=(master_command,)).start()
                for slave_addr in slave_addrs:
                    slave_command = f"bash run.sh {mode} config/{configFile}.ini 1 {node // num_slaves} 1 30000 30500 2 {limit_time}"
                    requests.get(f'http://{slave_addr}:30200/execute?command={slave_command}')
                time.sleep(50)
                # 开始收集日志
                for i, slave_addr in enumerate(slave_addrs):
                    for j in range(node // num_slaves * (i + 1) + 1, node // num_slaves * (i + 2)):
                        with open(f"{mode}/logs/Node{j}.log", "w") as f:
                            res = requests.get(f'http://{slave_addr}:30200/{mode}/logs/Node{j}.log')
                            f.write(res.content.decode("utf-8"))
                # 开始计算得到原始实验数据
                calculate(f"{mode}/logs", 1e9, limit_time, f'{mode}.txt')
        
        
if __name__ == '__main__':
    main()