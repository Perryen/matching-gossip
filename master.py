'''master.py 运行在主服务器上，用于批量运行实验
'''
import requests
import time
import os
import threading
import traceback
import datetime
import json
from concurrent.futures import ThreadPoolExecutor

from calculate import calculate, analyze_logs
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
    
    clusterInitTime = 30
    packetDiffuseTime = 20
    slaveWaitTime = 15
    masterWaitTime = 35
    UDP_buffer_size = 3500
    system_broadcast_mult = 1
    probe_interval = 10
    gossip_nodes = 3
    retran_mult = 10
    
    
    
    for topology in topologys:
        for dim in dims:
            configFile = f"{topology}-{dim}"
            if dim == 10:
                configFile = f"{topology}-{dim}-55"
            limit_time = int(1e9) * dim
            node = 2 ** dim
            nodes_num = node // (num_slaves + 1)  # 每台实体主机上运行的节点数
            nodes_num = max(1, nodes_num)
            nodes = []
            for i in range(4):
                nodes.extend(addrs[4 * i: 4 * i + min(node // 4, 4)])
            nodes.pop(0)
            
            for mode in ['mgossip', 'gossip']:
                master_command = f"bash run.sh {mode} config/{configFile}.ini 1 {nodes_num} 1 {gossip_nodes} {retran_mult} {clusterInitTime} {packetDiffuseTime} {slaveWaitTime} {UDP_buffer_size} {system_broadcast_mult} {probe_interval}"
                i = 0
                while i < 20:
                    # 这里另开一个线程的原因是为了快速同步从服务器，使从服务器几乎同步运行对应的命令
                    try:
                        threading.Thread(target=lambda c: os.system(c), args=(master_command,)).start()
                        for j, slave_addr in enumerate(nodes):
                            slave_command = f"bash run.sh {mode} config/{configFile}.ini {nodes_num * (j + 1) + 1} {nodes_num * (j + 2)} 0 {gossip_nodes} {retran_mult} {clusterInitTime} {packetDiffuseTime} {slaveWaitTime} {UDP_buffer_size} {system_broadcast_mult} {probe_interval}"
                            requests.get(f'http://{slave_addr}:30600/execute?command={slave_command}')
                        
                        sleep_time = clusterInitTime + packetDiffuseTime + masterWaitTime
                        time.sleep(sleep_time)
                        
                        # 开始收集各服务器数据
                        receive_times, send_packet_count = analyze_logs(mode, 1, nodes_num, limit_time)
                        node_count = nodes_num
                        for j, slave_addr in enumerate(nodes):
                            params = {
                                'beginNode': (j + 1) * nodes_num + 1,
                                'endNode': (j + 2) * nodes_num,
                                'mode': mode,
                                'limitTime': limit_time + receive_times[0],
                            }
                            res = requests.post(f'http://{slave_addr}:30600/logs', data=json.dumps(params))
                            data = json.loads(res.content)
                            receive_times.extend(data['receiveTimes'])
                            send_packet_count += data['sendPacketCount']
                            node_count += data['nodeCount']
                            
                        # 整合数据计算实验指标
                        calculate(5e8, os.path.join('data', f'{mode}-{topology}-{dim}.txt'), receive_times, send_packet_count, node_count)
                        i += 1
                    except:
                        with open("error.log", "a") as f:
                            f.write(datetime.datetime.now() + ", " + traceback.format_exc())
                        time.sleep(60)        
    clean_data('data')
        
        
if __name__ == '__main__':
    main()