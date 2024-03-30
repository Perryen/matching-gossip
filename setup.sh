# 使用手册：
#  1. 修改setup.sh:替换MASTER为第一个IP地址，SLAVES为剩下15个IP地址，用：分开
#  2. 将该setup.sh拷贝到服务器上
#  3. 执行bash setup.sh
#  4. 输入gitee账号密码
#  5. tmux new-session -t mgossip
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
#git clone https://gitee.com/Perryen/matching-gossip.git
git clone https://github.com/Perryen/matching-gossip

# 设置环境变量
echo 'export PATH="/usr/local/go/bin:${PATH}"' >> /etc/profile
echo 'export MASTER=47.113.100.235' >> /etc/profile
echo 'export SLAVES=119.23.145.67:120.78.7.58:120.78.1.214:47.88.22.6:47.254.15.117:47.251.52.90:47.251.45.171:8.208.24.105:8.208.53.106:8.208.112.155:8.208.21.77:47.74.84.115:47.74.91.104:47.74.89.146:47.74.87.139' >> /etc/profile
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

# 下载go第三方包
cd mgossip
go install
cd -
cd gossip
go install


# git config --global user.email "2470145197@qq.com" && git config --global user.name "123" && git stash && git pull origin master && python3 slave.py
# cd $WORKDIR && rm -rf config && rm -rf gossip/config && rm -rf mgossip/config && mkdir config && python3 topology.py && cp -r config mgossip && cp -r config gossip