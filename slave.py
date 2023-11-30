"""slave.py 为从服务器运行的网络程序，接受并且执行来自主服务器的同步运行命令
"""
from flask import Flask, request
import os


app = Flask(__name__)
slaveAddr = os.environ.get('SLAVE')

@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'

@app.route('/execute', methods=['GET'])
def execute():
    command = request.args.get('command', type=str)
    print(command)
    os.system(command)  # 执行主服务器传送过来的运行run.sh脚本的相关命令
    return 'I have execute the command'
    
    
if __name__ == '__main__':
    app.run(host=slaveAddr, port=30200)