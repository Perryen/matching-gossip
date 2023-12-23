## Matching-gossip: 对传统gossip在拓扑失配性上的改进

### 实验介绍

本实验是对第三章提出的改进gossip协议——Matching-gossip协议的实验。经典gossip和matching-gossip都基于memberlist实现。主要有三个实验，主要是测试包括总线拓扑、环形拓扑、不同维度超立方体拓扑的收敛时间和网络负载。
我们主要在两台主机之间进行实验，每台主机有整体集群一半的节点。同一台主机上的不同节点用不同端口号标识。每个节点运行一个进程，整个集群表示为类似于redis的KV键值对数据库，通过gossip协议来同步不同节点的信息。
我们通过在一些关键时刻记录相关信息和当前时间（精确到纳秒）到日志文件中，然后分析日志文件计算收敛时间和网络负载。具体来说，当一个节点（通常是种子节点）获得一条新信息，则其记录'I create a message called {messsageID}, now time {nowTime}, broadcast to others'，如果节点收到一条用户自定义信息，则其记录'I receive a message called {messageID}, now time is {nowTime}',如果一个节点要发送一条用户自定义信息，则其记录'I send a packet to {addr}, now time {nowTime}'。这样我们通过访问种子节点运行的KV键值对网络程序，即可给集群一个新信息，经过一段足够长的时间，收集所有节点的日志，读取日志文件，计算新信息的创造时间`begin_time`，然后记录其他节点收到该条信息的`receive_time`，取最晚的`receive_time`减去`begin_time`即为整个系统的收敛时间。当然，整个系统未必能百分百收敛，可以通过计算日志文件总数和收敛时间数加一计算收敛率。对于实验负载的计算，我们简单地用每个节点发送数据包来表示，并且因为经典gossip在小网络上的信息泛滥问题，我们人为地限定一个一定大于收敛时间的`limit_time`，计算在这个时间内日志文件中属于发送数据包行为的行数作为发送数据包。


### 目录文件介绍

 - `gossip`目录存放经典Gossip实验代码
    - `config`目录存放ini格式的配置文件
    - `Gossip`或者`MGossip`存放基于memberlist开发的经典Gossip或者matching-gossip的工具包
    - `logs`目录存放节点运行的日志
    - `vendor`存放程序运行所需要的第三方包
    - `go.mod`和`go.sum`是go项目关于依赖的一些文件
    - `main.go`是启动函数
 - `mgossip` 目录存放matching-gossip实验代码（下级目录同上）
 - `calculate.py` 是用来读取日志文件计算实验指标的脚本
 - `clean_data.py` 是用来进一步整理实验数据计算平均值、去头尾平均值等指标的脚本
 - `run.sh`是一键部署实验的脚本，注意，脚本中的路径、密码等需要根据实际条件设置
 - `master.py`和`slave.py`配对出现，分别用于主服务器和从服务器，是一个协调多主机批量重复实验的脚本
 - `topology.py`是一个快速构造指定维度指定拓扑的脚本，输出为config目录下的ini配置文件
 - `Dockerfile`是打包镜像的文件，可以参考本文件配置实验环境

### 实验环境搭建
如果你对linux系统比较熟悉，可以执行搭建实验环境。我们也提供了Docker容器（推荐），更容易地进行实验。
实验环境： ubuntu 18.04(最好有两台主机)
实验命令汇总：
```sh
git clone 待填写网站
cd matching-gossip
# 安转Go等
wget https://golang.google.cn/dl/go1.21.3.linux-amd64.tar.gz 
tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz

# 设置环境变量
sudo vim /etc/profile
# 按i进入编辑模式，在文件最后写入如下内容
PATH="/usr/local/go/bin:$PATH"
MASTER={需改为你的主服务器的ip地址}
SLAVE={需改为你的从服务器的ip地址}
WORKDIR={需改为run.sh所在的目录地址}
USER={需改为从服务器你拥有的用户名}
PASSWD={需改为以上用户民对应的密码}
GOPROXY=https://goproxy.io
# 按Esc键后，输入：wq保存退出

sudo source /etc/profile

sudo chmod 777 run.sh  # 授予run.sh可执行权限

# 以下是当次实验的命令，每四行为一组，前两行为mgossip实验，后两行是同等配置下gossip实验，第一行和第三行运行在主服务器上，第二、四行运行在从服务器上，可能需要现在一些工具请参考dockerfile文件。同时请确保从服务器运行了ssh服务
bash run.sh mgossip config/hybercube-2.ini 1 2 1 30000 30500 2 200000000 2
bash run.sh mgossip config/hybercube-2.ini 3 4 0 30000 30500 2 200000000 2

bash run.sh gossip config/hybercube-2.ini 1 2 1 30000 30500 2 200000000 2
bash run.sh gossip config/hybercube-2.ini 3 4 0 30000 30500 2 200000000 2


bash run.sh mgossip config/hybercube-3.ini 1 4 1 30000 30500 2 500000000 4
bash run.sh mgossip config/hybercube-3.ini 5 8 0 30000 30500 2 500000000 4

bash run.sh gossip config/hybercube-3.ini 1 4 1 30000 30500 2 500000000 4
bash run.sh gossip config/hybercube-3.ini 5 8 0 30000 30500 2 500000000 4

bash run.sh mgossip config/hybercube-4.ini 1 8 1 30000 30500 2 1000000000 8
bash run.sh mgossip config/hybercube-4.ini 9 16 0 30000 30500 2 1000000000 8

bash run.sh gossip config/hybercube-4.ini 1 8 1 30000 30500 2 1000000000 8
bash run.sh gossip config/hybercube-4.ini 9 16 0 30000 30500 2 1000000000 8

bash run.sh mgossip config/hybercube-5.ini 1 16 1 30000 30500 2 2000000000 16
bash run.sh mgossip config/hybercube-5.ini 17 32 0 30000 30500 2 2000000000 16

bash run.sh gossip config/hybercube-5.ini 1 16 1 30000 30500 2 2000000000 16
bash run.sh gossip config/hybercube-5.ini 17 32 0 30000 30500 2 2000000000 16

bash run.sh mgossip config/hybercube-6.ini 1 32 1 30000 30500 2 2000000000 32
bash run.sh mgossip config/hybercube-6.ini 33 64 0 30000 30500 2 2000000000 32

bash run.sh gossip config/hybercube-6.ini 1 32 1 30000 30500 2 2000000000 32
bash run.sh gossip config/hybercube-6.ini 33 64 0 30000 30500 2 2000000000 32

bash run.sh mgossip config/hybercube-7.ini 1 64 1 30000 30500 2 4000000000 64
bash run.sh mgossip config/hybercube-7.ini 65 128 0 30000 30500 2 4000000000 64

bash run.sh gossip config/hybercube-7.ini 1 64 1 30000 30500 2 4000000000 64
bash run.sh gossip config/hybercube-7.ini 65 128 0 30000 30500 2 4000000000 64

bash run.sh mgossip config/hybercube-8.ini 1 128 1 30000 30500 2 8000000000 128
bash run.sh mgossip config/hybercube-8.ini 129 256 0 30000 30500 2 8000000000 128

bash run.sh gossip config/hybercube-8.ini 1 128 1 30000 30500 2 8000000000 128
bash run.sh gossip config/hybercube-8.ini 129 256 0 30000 30500 2 8000000000 128

bash run.sh mgossip config/hybercube-9.ini 1 256 1 30000 30500 2 10000000000 256
bash run.sh mgossip config/hybercube-9.ini 257 512 0 30000 30500 2 10000000000 256

bash run.sh gossip config/hybercube-9.ini 1 256 1 30000 30500 2 2000000000 512
bash run.sh gossip config/hybercube-9.ini 257 512 0 30000 30500 2 2000000000 512

bash run.sh mgossip config/bus.ini 1 8 1 30000 30500 2 1000000000 8
bash run.sh mgossip config/bus.ini 9 16 0 30000 30500 2 1000000000 8

bash run.sh gossip config/bus.ini 1 8 1 30000 30500 2 1000000000 8
bash run.sh gossip config/bus.ini 9 16 0 30000 30500 2 1000000000 8


bash run.sh mgossip config/ring.ini 1 8 1 30000 30500 2 1000000000 8
bash run.sh mgossip config/ring.ini 9 16 0 30000 30500 2 1000000000 8

bash run.sh gossip config/ring.ini 1 8 1 30000 30500 2 1000000000 8
bash run.sh gossip config/ring.ini 9 16 0 30000 30500 2 1000000000 8
```


### Docker容器指南
```sh
sudo apt-get install docker.io  # 安装docker

# 以下是Docker 打包命令
sudo docker build -t mgossip:v1.0 .

sudo docker pull zhuohuashiyi/mgossip:v1.0
sudo docker run -it --name mgossip-master  zhuohuashiyi/mgossip:v1.0  # 运行主服务器容器
sudo docker run -it --name mgossip-slave zhuohuashiyi/mgossip:v1.0  # 运行从服务器容器

service ssh restart  # 从服务器上运行
cd $WORKDIR && scp root@172.17.0.3:/Gossip/slave.py slave.py  # 提示输入yes

# 接下来可以像上面一样单个单个进行实验，也可以如下进行批量实验
python3 slave.py  # 从服务器
python3 master.py  # 主服务器
```