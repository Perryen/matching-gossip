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
echo 'export MASTER=112.74.97.164' >> /etc/profile
echo 'export SLAVES=47.106.233.248:47.251.71.56:47.251.78.77:8.208.83.221:8.208.96.27:47.74.84.187:47.74.89.74' >> /etc/profile
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

