# root权限执行
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
echo 'export MASTER=120.78.10.33' >> /etc/profile
echo 'export SLAVES=47.88.46.87:47.74.90.214:8.208.101.180' >> /etc/profile
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

# tmux new-session -t mgossip
# cd matching-gossip