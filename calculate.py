"""calculate.py是一个用来读取日志文件计算实验指标的脚本，使用到的技术主要是正则表达式
"""
import os
import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument("-logs_dir", help="your logs dirctory", default="MGossip/logs", type=str)
parser.add_argument("-gossip_interval", help="your gossip interval", default=100000000, type=int)
parser.add_argument("-limit_time", help="your limitTime to test the total packet sent", default=500000000, type=int)
parser.add_argument("-result_file", help="the file results store in, if none, it will output in the terminal", type=str)
args = parser.parse_args()


create_packet_pattern = r'.*I create a message called (\d+), now time (\d+).*'
receive_packet_pattern = r'.*I receive a message called (\d+), now time is (\d+).*'
send_packet_pattern = r'.*I send a packet to ([\d,.]+):(\d+), now time (\d+).*'



def analyze_logs(mode, begin_node, end_node, limit_time):
    flag = True 
    receive_times = []
    send_packet_count = 0
    for i in range(begin_node, end_node + 1):
        log_file = os.path.join(mode, 'logs', f'Node{i}.log')
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                # 计算种子节点创造测试消息的起始时间
                m = re.match(create_packet_pattern, line)
                if m:
                    receive_times.append(int(m.group(2)))
                    limit_time += receive_times[-1]
                    flag = False
                # 计算每个节点被感染的时间
                m = re.match(receive_packet_pattern, line)
                if m and flag:
                    receive_times.append(int(m.group(2)))
                    flag = False
                # 计算每个节点在限制时间内发送的总数据包 
                m = re.match(send_packet_pattern, line)
                if m:
                    now_time = m.group(3)
                    if int(now_time) >= limit_time:
                        break
                    send_packet_count += 1
    return receive_times, send_packet_count


def calculate(gossip_interval, result_file, receive_times, send_packet_count, node_count):
    
    infected_nodes_every_epoch = []

    # 以下计算各个周期内被感染的节点数
    receive_times.sort()
    count = 0
    interval = gossip_interval
    time_limit = receive_times[0] + interval
    for each_time in receive_times:
        if each_time >= time_limit:
            infected_nodes_every_epoch.append(count)
            count = 1
            time_limit += interval
        else:
            count += 1
    infected_nodes_every_epoch.append(count)
    convergence_rate_every_epoch = [0] * len(infected_nodes_every_epoch) 
    nodes_sum = 0
    for i, count in enumerate(infected_nodes_every_epoch):
        nodes_sum += count
        convergence_rate_every_epoch[i] = round(nodes_sum / node_count, 2)
    convergence_time = receive_times[-1] - receive_times[0]
    try:
        with open(result_file, 'a') as f:
            f.write(f"node convergence rate: {(len(receive_times)) / node_count:.2f}\nconvergence time: {convergence_time} ns\ntotal packet the network send: {send_packet_count}\ninfected nodes every gossip epoch: {infected_nodes_every_epoch}\nconvergence_rate_every_epoch: {convergence_rate_every_epoch}\n")
    except Exception as e:
        print(e)
        print(f"node convergence rate: {(len(receive_times)) / node_count:.2f}")
        print(f"convergence time: {convergence_time} ns")
        print(f"total packet the network send: {send_packet_count}")
        print(f"infected nodes every gossip epoch: {infected_nodes_every_epoch}")
        print(f"convergence_rate_every_epoch: {convergence_rate_every_epoch}")
    
if __name__ == '__main__':
    calculate(args.logs_dir, args.gossip_interval, args.limit_time, args.result_file)  