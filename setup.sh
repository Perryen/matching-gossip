# 使用手册：
#  1. 将该setup.sh拷贝到服务器上
#  2. 执行bash setup.sh
#  3. 输入gitee账号密码
# 安装必要工具
apt-get update
apt-get upgrade
apt-get -y  install wget
apt-get -y install git
wget https://golang.google.cn/dl/go1.21.3.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz
apt-get -y install python3-pip
pip3 install flask
apt-get install -y tmux

# 拉去代码
cd /root
git clone https://gitee.com/Perryen/matching-gossip.git


# 设置环境变量
echo 'export PATH="/usr/local/go/bin:${PATH}"' >> /etc/profile
echo 'export MASTER=47.106.233.248' >> /etc/profile
echo 'export SLAVES=120.79.67.101:120.79.32.161:47.106.228.23:47.254.15.35:47.251.57.68:47.251.78.77:47.251.73.191:8.208.83.221:8.208.102.21:8.208.96.27:8.208.47.241:47.74.89.10:47.74.92.146:47.74.88.198:47.74.89.16' >> /etc/profile
echo 'export WORKDIR=/root/matching-gossip' >> /etc/profile
echo 'export GOPROXY=https://goproxy.io' >> /etc/profile
source /etc/profile

# 生成拓扑文件
cd $WORKDIR
rm -rf config
rm -rf gossip/config
rm -rf mgossip/config
mkdir config
python3 topology.py
cp -r config mgossip
cp -r config gossip

