'''clean_data.py用于基于初步的实验结果进一步计算平均值、去首尾平均值等衡量指标
'''
import os
import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument("-data_dir", help="your data dirctory", default="data-2", type=str)
args = parser.parse_args()


def main():
    convergence_time_pattern = r'convergence time: (\d+) ns'
    send_packet_pattern = r'total packet the network send: (\d+)'
    for file in os.listdir(args.data_dir):
        file_path = os.path.join(args.data_dir, file)
        if not os.path.isdir(file_path) and file.split(".")[-1] == 'txt': # 判断是数据文件
            convergence_times = []
            send_packet_counts = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    m = re.match(convergence_time_pattern, line)
                    if m:
                        convergence_time = float(m.group(1))
                        result = round(convergence_time / 1000000, 2)  # 保留两位小数，四舍五入
                        convergence_times.append(result)
                    m = re.match(send_packet_pattern, line)
                    if m:
                        if int(m.group(1)) > 0:
                            send_packet_counts.append(int(m.group(1)))
                        # 下面是为了丢弃故障异常的实验数据
                        if len(convergence_times) > len(send_packet_counts):
                            convergence_times.pop()
                        elif len(convergence_times) < len(send_packet_counts):
                            send_packet_counts.pop()
                        
            convergence_times.sort()
            send_packet_counts.sort()
            n = len(convergence_times)
            drop = n // 10
            mean_convergence_time = round(sum(convergence_times) / n, 2)
            drop_mean_convergence_time = round(sum(convergence_times[drop: -drop]) / (n - 2 * drop), 2) 
            mean_send_packet_count = round(sum(send_packet_counts) / n, 2)
            drop_mean_send_packet_count = round(sum(send_packet_counts[drop: -drop]) / (n - 2 * drop), 2)
            min25_mean_convergence_time = round(sum(convergence_times[: n // 4]) / (n // 4), 2)
            print(file)
            print(f"total test cases: {n}")
            print(f"mean convergence time: {mean_convergence_time}")
            print(f"drop max 10% and min 10% mean convergence time: {drop_mean_convergence_time}")
            print(f"min 25 % mean convergence time: {min25_mean_convergence_time}")
            print(f"var and std of convergence time: {calculate_square_error(convergence_time, mean_convergence_time)}")
            print(f"mean send packet count: {mean_send_packet_count}")
            print(f"drop max 10% and min 10% mean send packet count: {drop_mean_send_packet_count}")
            print(f"var and std of send packet count: {calculate_square_error(send_packet_counts, mean_send_packet_count)}")
            


def calculate_square_error(data, mean):
    error = 0
    n = len(data)
    for num in data:
        error += (num - mean) * (num - mean)
    square_error = round(error / n, 2)
    return square_error, round(square_error ** 0.5, 2)
        

if __name__ == '__main__':
    main()
                    
    