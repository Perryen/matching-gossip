'''master.py 运行在主服务器上，用于批量运行实验
'''
import requests
import time
import os
import threading


slaveAddr = os.environ.get('SLAVE')

def main():
    configFiles = [
        'hybercube-2', 'hybercube-3', 'hybercube-4', 'hybercube-5','bus-4', 'ring-4'
    ]
    # 所有主服务器和从服务器需要运行的命令
    commands = [
                [
                    'bash run.sh mgossip config/{}.ini 1 2 1 30000 30500 {} {} 1000000000 2',
                    'bash run.sh mgossip config/{}.ini 3 4 0 30000 30500 {} {} 1000000000 2',
                    'bash run.sh gossip config/{}.ini 1 2 1 30000 30500 {} {} 1000000000 2',
                    'bash run.sh gossip config/{}.ini 3 4 0 30000 30500 {} {} 1000000000 2'
                ],
                [
                    'bash run.sh mgossip config/{}.ini 1 4 1 30000 30500 {} {} 1000000000 4',
                    'bash run.sh mgossip config/{}.ini 5 8 0 30000 30500 {} {} 1000000000 4',
                    'bash run.sh gossip config/{}.ini 1 4 1 30000 30500 {} {} 1000000000 4',
                    'bash run.sh gossip config/{}.ini 5 8 0 30000 30500 {} {} 1000000000 4'
                ],
                [
                    'bash run.sh mgossip config/{}.ini 1 8 1 30000 30500 {} {} 1000000000 8',
                    'bash run.sh mgossip config/{}.ini 9 16 0 30000 30500 {} {} 1000000000 8',
                    'bash run.sh gossip config/{}.ini 1 8 1 30000 30500 {} {} 1000000000 8',
                    'bash run.sh gossip config/{}.ini 9 16 0 30000 30500 {} {} 1000000000 8'
                ],
                [
                    'bash run.sh mgossip config/{}.ini 1 16 1 30000 30500 {} {} 2000000000 16',
                    'bash run.sh mgossip config/{}.ini 17 32 0 30000 30500 {} {} 2000000000 16',
                    'bash run.sh gossip config/{}.ini 1 16 1 30000 30500 {} {} 2000000000 16',
                    'bash run.sh gossip config/{}.ini 17 32 0 30000 30500 {} {} 2000000000 16'
                ],
                                [
                    'bash run.sh mgossip config/{}.ini 1 8 1 30000 30500 {} {} 1000000000 8',
                    'bash run.sh mgossip config/{}.ini 9 16 0 30000 30500 {} {} 1000000000 8',
                    'bash run.sh gossip config/{}.ini 1 8 1 30000 30500 {} {} 1000000000 8',
                    'bash run.sh gossip config/{}.ini 9 16 0 30000 30500 {} 1000000000 8'
                ],
                [
                    'bash run.sh mgossip config/{}.ini 1 8 1 30000 30500 {} {} 1000000000 8',
                    'bash run.sh mgossip config/{}.ini 9 16 0 30000 30500 {} {} 1000000000 8',
                    'bash run.sh gossip config/{}.ini 1 8 1 30000 30500 {} {} 1000000000 8',
                    'bash run.sh gossip config/{}.ini 9 16 0 30000 30500 {} {} 1000000000 8'
                ]
            ]
    gossipNodes = 2
    os.system(f'rm -rf data-{gossipNodes}')
    os.system(f'mkdir data-{gossipNodes}')
    for idx, config in enumerate(configFiles):
        retranMult = 3
        master_command = commands[idx][0].format(config, gossipNodes, retranMult)
        slave_command = commands[idx][1].format(config, gossipNodes, retranMult)
        for i in range(20):
            # 这里另开一个线程的原因是为了快速同步从服务器，使从服务器几乎同步运行对应的命令
            threading.Thread(target=lambda c: os.system(c), args=(master_command,)).start()
            requests.get(f'http://{slaveAddr}:30200/execute?command={slave_command}')
            time.sleep(20)
            
        retranMult = 1
        master_command = commands[idx][2].format(config, gossipNodes, retranMult)
        slave_command = commands[idx][3].format(config, gossipNodes, retranMult)
        for i in range(20):
            threading.Thread(target=lambda c: os.system(c), args=(master_command,)).start()
            requests.get(f'http://{slaveAddr}:30200/execute?command={slave_command}')
            time.sleep(20)
        os.system(f'mv mgossip.txt data-{gossipNodes}/mgossip-{config}.txt')
        os.system(f'mv gossip.txt data-{gossipNodes}/gossip-{config}.txt')
        
        
    
if __name__ == '__main__':
    main()