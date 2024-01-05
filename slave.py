"""slave.py 为从服务器运行的网络程序，接受并且执行来自主服务器的同步运行命令
"""
from flask import Flask, request, send_file
import os


app = Flask(__name__)


# 测试接口
@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'

@app.route('/execute', methods=['GET'])
def execute():
    command = request.args.get('command', type=str)
    print(command)
    os.system(command)  # 执行主服务器传送过来的运行run.sh脚本的相关命令
    return 'I have execute the command'

# 以下两个为获取日志端口
@app.route('/mgossip/logs/<logname>', methods=['GET'])
def mgossip_logs(logname):
    return send_file(f"mgossip/logs/{logname}")

@app.route('/gossip/logs/<logname>', methods=['GET'])
def gossip_logs(logname):
    return send_file(f"gossip/logs/{logname}")

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30600)