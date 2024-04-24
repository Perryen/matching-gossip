#!/bin/sh
# 用于seed平台设置延时，运行示例：bash tc.sh 0(1,2,3)


# 删除指定网卡接口上的根队列规则
# seed平台似乎会设置一些默认规则，避免出现Error: Exclusivity flag on, cannot modify
tc qdisc del dev net$1 root


# 创建了一个优先级队列规则，并在队列1:1中应用50ms的延迟，在队列1:2中应用500ms的延迟
tc qdisc add dev net$1 root handle 1: prio
tc qdisc add dev net$1 parent 1:1 handle 10: netem delay 50ms
tc qdisc add dev net$1 parent 1:2 handle 20: netem delay 500ms

# 创建分类规则以区分不同的网段
# 如果同属于一个网段，则数据包转发到队列1:1，否则转发到队列1:2
tc filter add dev net$1 protocol ip parent 1: prio 1 u32 match ip dst 10.15$1.0.0/16 flowid 1:1
tc filter add dev net$1 protocol ip parent 1: prio 2 u32 match ip dst 10.0.0.0/8 flowid 1:2



