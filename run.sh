# 仅供参考，相关命令需要根据服务器路径进行修改,以及需要使用chmod命令修改该程序的执行权限

#!/bin/sh
# 以下是命令行参数的接收
mgossip=1  # 1表示运行改进Gossip实验，0表示运行经典Gossip实验
if [[ $1 -eq 'mgossip' ]]; then
    mgossip=1
else
    mgossip=0
fi
confFile=$2  # 配置文件地址
firstNode=$3  
endNode=$4
isMaster=$5
port1=$6  # 30000
port2=$7  # 30200
gossipNodes=$8
limitTime=$9
portNum=$4-$3+1
node='Node'

# 根据是运行经典Gossip还是改进Gossip实验进入不同的目录
if [[ $mgossip -eq 1 ]]; then
    cd $WORKDIR/mgossip
else
    cd $WORKDIR/gossip
fi

rm -rf logs
mkdir logs

# 以下是将可能占用本实验需要的端口的所有进程杀死，我们默认使用的是30000到30100的端口，
# 如果某些占用这些端口的进程很重要，请修改命令行参数和配置脚本
for ((i=$port1; i<$port1+$portNum; i++)); do
    kill -9 $(netstat -antp | grep :$i | awk '{print $7}' | awk -F'/' '{ print $1 }')
done

# 从服务器需要等待一段时间直到主服务器上的种子节点启动成功
if [[ $isMaster -eq 0 ]]; then
    sleep 3
fi

for ((i=firstNode; i<=endNode; i++)); do
    # 使用nohup在后台运行main.go程序，即运行一个网络节点
    nohup go run main.go -nodeName ${node}${i} -conf $confFile -gossipNodes $gossipNodes > /dev/null 2>&1 &
    if [[ $isMaster -eq 1 && i -ne firstNode ]]; then  # 种子节点默认是主服务器上的第一个节点
        sleep 3
    fi
done

# 剩下的工作与从服务器无关
if [[ $isMaster -eq 0 ]]; then
    sleep 75
    for ((i=$port1; i<$port1+$portNum; i++)); do
        kill -9 $(netstat -antp | grep :$i | awk '{print $7}' | awk -F'/' '{ print $1 }')
    done
    exit
fi

sleep 60    # 等待整个集群中的所有节点全部启动成功
cd ..

curl "http://"$MASTER":30200/add?key=mgossip&val=better"  # 给种子节点一个消息
sleep 10   # 等待直到上述消息已经在集群中得到了充分的传播

for ((i=$port1; i<$port1+$portNum; i++)); do
    kill -9 $(netstat -antp | grep :$i | awk '{print $7}' | awk -F'/' '{ print $1 }')
done