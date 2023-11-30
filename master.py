'''master.py 运行在主服务器上，用于批量运行实验
'''
import requests
import time
import os
import threading


slaveAddr = os.environ.get('SLAVE')

def main():
    configFiles = [
        'bus', 'ring', 'hybercube-2', 'hybercube-3', 'hybercube-4', 'hybercube-5',          
        'hybercube-6', 'hybercube-7', 'hybercube-8', 'hybercube-9'
    ]
    # 所有主服务器和从服务器需要运行的命令
    commands = [
                [
                    'bash run.sh mgossip config/bus.ini 1 8 1 30000 30500 {} 1000000000 8',
                    'bash run.sh mgossip config/bus.ini 9 16 0 30000 30500 {} 1000000000 8',
                    'bash run.sh gossip config/bus.ini 1 8 1 30000 30500 {} 1000000000 8',
                    'bash run.sh gossip config/bus.ini 9 16 0 30000 30500 {} 1000000000 8'
                ],
                [
                    'bash run.sh mgossip config/ring.ini 1 8 1 30000 30500 {} 1000000000 8',
                    'bash run.sh mgossip config/ring.ini 9 16 0 30000 30500 {} 1000000000 8',
                    'bash run.sh gossip config/ring.ini 1 8 1 30000 30500 {} 1000000000 8',
                    'bash run.sh gossip config/ring.ini 9 16 0 30000 30500 {} 1000000000 8'
                ],
                [
                    'bash run.sh mgossip config/hybercube-2.ini 1 2 1 30000 30500 {} 1000000000 2',
                    'bash run.sh mgossip config/hybercube-2.ini 3 4 0 30000 30500 {} 1000000000 2',
                    'bash run.sh gossip config/hybercube-2.ini 1 2 1 30000 30500 {} 1000000000 2',
                    'bash run.sh gossip config/hybercube-2.ini 3 4 0 30000 30500 {} 1000000000 2'
                ],
                [
                    'bash run.sh mgossip config/hybercube-3.ini 1 4 1 30000 30500 {} 1000000000 4',
                    'bash run.sh mgossip config/hybercube-3.ini 5 8 0 30000 30500 {} 1000000000 4',
                    'bash run.sh gossip config/hybercube-3.ini 1 4 1 30000 30500 {} 1000000000 4',
                    'bash run.sh gossip config/hybercube-3.ini 5 8 0 30000 30500 {} 1000000000 4'
                ],
                [
                    'bash run.sh mgossip config/hybercube-4.ini 1 8 1 30000 30500 {} 1000000000 8',
                    'bash run.sh mgossip config/hybercube-4.ini 9 16 0 30000 30500 {} 1000000000 8',
                    'bash run.sh gossip config/hybercube-4.ini 1 8 1 30000 30500 {} 1000000000 8',
                    'bash run.sh gossip config/hybercube-4.ini 9 16 0 30000 30500 {} 1000000000 8'
                ],
                [
                    'bash run.sh mgossip config/hybercube-5.ini 1 16 1 30000 30500 {} 2000000000 16',
                    'bash run.sh mgossip config/hybercube-5.ini 17 32 0 30000 30500 {} 2000000000 16',
                    'bash run.sh gossip config/hybercube-5.ini 1 16 1 30000 30500 {} 2000000000 16',
                    'bash run.sh gossip config/hybercube-5.ini 17 32 0 30000 30500 {} 2000000000 16'
                ],
                [
                    'bash run.sh mgossip config/hybercube-6.ini 1 32 1 30000 30500 {} 3000000000 32',
                    'bash run.sh mgossip config/hybercube-6.ini 33 64 0 30000 30500 {} 3000000000 32',
                    'bash run.sh gossip config/hybercube-6.ini 1 32 1 30000 30500 {} 3000000000 32',
                    'bash run.sh gossip config/hybercube-6.ini 33 64 0 30000 30500 {} 3000000000 32'
                ] ,
                [
                    'bash run.sh mgossip config/hybercube-7.ini 1 64 1 30000 30500 {} 4000000000 64',
                    'bash run.sh mgossip config/hybercube-7.ini 65 128 0 30000 30500 {} 4000000000 64',
                    'bash run.sh gossip config/hybercube-7.ini 1 64 1 30000 30500 {} 4000000000 64',
                    'bash run.sh gossip config/hybercube-7.ini 65 128 0 30000 30500 {} 4000000000 64'
                ] ,
                [
                    'bash run.sh mgossip config/hybercube-8.ini 1 128 1 30000 30500 {} 8000000000 128',
                    'bash run.sh mgossip config/hybercube-8.ini 129 256 0 30000 30500 {} 8000000000 128',
                    'bash run.sh gossip config/hybercube-8.ini 1 128 1 30000 30500 {} 8000000000 128',
                    'bash run.sh gossip config/hybercube-8.ini 129 256 0 30000 30500 {} 8000000000 128'
                ],
                [
                    'bash run.sh mgossip config/hybercube-9.ini 1 256 1 30000 30500 {} 10000000000 256',
                    'bash run.sh mgossip config/hybercube-9.ini 257 512 0 30000 30500 {} 10000000000 256',
                    'bash run.sh gossip config/hybercube-9.ini 1 256 1 30000 30500 {} 10000000000 256',
                    'bash run.sh gossip config/hybercube-9.ini 257 512 0 30000 30500 {} 10000000000 256'
                ]    
            ]
    for gossipNodes in [2]:
        os.system(f'rm -rf data-{gossipNodes}')
        os.system(f'mkdir data-{gossipNodes}')
        for idx, config in enumerate(configFiles):
            master_command = commands[idx][0].format(gossipNodes)
            slave_command = commands[idx][1].format(gossipNodes)
            for i in range(20):
                # 这里另开一个线程的原因是为了快速同步从服务器，使从服务器几乎同步运行对应的命令
                threading.Thread(target=lambda c: os.system(c), args=(master_command,)).start()
                requests.get(f'http://{slaveAddr}:30200/execute?command={slave_command}')
                time.sleep(20)
                
            master_command = commands[idx][2].format(gossipNodes)
            slave_command = commands[idx][3].format(gossipNodes)
            for i in range(20):
                threading.Thread(target=lambda c: os.system(c), args=(master_command,)).start()
                requests.get(f'http://{slaveAddr}:30200/execute?command={slave_command}')
                time.sleep(20)
            os.system(f'mv mgossip.txt data-{gossipNodes}/mgossip-{config}.txt')
            os.system(f'mv gossip.txt data-{gossipNodes}/gossip-{config}.txt')
        
        
    
if __name__ == '__main__':
    main()