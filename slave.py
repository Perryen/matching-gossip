"""slave.py 为从服务器运行的网络程序，接受并且执行来自主服务器的同步运行命令
"""
from flask import Flask, request, send_file
import os
import requests
import re


app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'

@app.route('/execute', methods=['GET'])
def execute():
    command = request.args.get('command', type=str)
    print(command)
    os.system(command)  # 执行主服务器传送过来的运行run.sh脚本的相关命令
    return 'I have execute the command'

@app.route('/mgossip/logs/<logname>', methods=['GET'])
def mgossip_logs(logname):
    return send_file(f"mgossip/logs/{logname}")


@app.route('/gossip/logs/<logname>', methods=['GET'])
def gossip_logs(logname):
    return send_file(f"gossip/logs/{logname}")



def get_self_ip() -> str:
    response = requests.get('http://myip.ipip.net')
    res = response.content.decode('utf-8')
    m = re.match(r'.*当前 IP：([\d,.]+)  来自于.*')
    if m:
        return m.group(1)
    
    
if __name__ == '__main__':
    app.run(host=get_self_ip(), port=30200)