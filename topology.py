"""topology.py构造大量节点的超立方体拓扑、总线拓扑、环形拓扑
"""
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-topology", help="please choose from hybercube, bus and ring", default="hybercube", type=str)
parser.add_argument("-dim", help="mainly refer to hybercube topology, will produce a config file contains 2^dim nodes", default=2, type=int)
args = parser.parse_args()
masterAddr = os.environ.get("MASTER")
slaveAddr = os.environ.get("SLAVE")


class Node:
    def __init__(self, nodeName, bindAddr, bindPort, memberlistAddr, memberlistPort, port, neighbors):
        self.nodeName = nodeName
        self.bindAddr = bindAddr
        self.bindPort = bindPort
        self.memberlistAddr = memberlistAddr
        self.memberlistPort = memberlistPort
        self.port = port
        self.neighbors = neighbors
        
    def __str__(self):
        # 输出配置文件的内容
        return f'[{self.nodeName}]\nbindAddr={self.bindAddr}\nbindPort={self.bindPort}\nmemberlistAddr={self.memberlistAddr}\nmemberlistPort={self.memberlistPort}\nneighbors="{",".join(self.neighbors)}"\nport={self.port}\n\n'
    
    def set_neighbors(self, neighbors):
        self.neighbors = neighbors
        
    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        
    def address(self) -> str:
        return f"{self.bindAddr}:{self.bindPort}"
    
    def str(self) -> str:
        return self.__str__()
    
    
# 递归构造超立方体拓扑，单一IP地址  
def construct_hybercube_cluster(ip: str, port1: int, port2: int, no: int, dim: int):
    if dim == 0: # 偶数维度超立方体拓扑递归终点
        return [Node(f'Node{no}', ip, port1, masterAddr, '30000', port2, [])]
    if dim == 1:  # 奇数维度超立方体拓扑递归终点
        node1 = Node(f'Node{no}', ip, port1, masterAddr, '30000', port2, [])
        node2 = Node(f'Node{no + 1}', ip, port1 + 1, 'masterAddr', '30000', port2 + 1, [])
        node1.add_neighbor(node2.address())
        node2.add_neighbor(node1.address())
        return [node1, node2]
    # 递归构造，相当与一个正方形拓扑，每一个端点都是dim-2维度的超立方体拓扑
    nodes = []
    cluster_nums = 2 ** (dim - 2)
    node_nums = 2 ** dim
    for i in range(4):  # 正方形递归
        nodes.extend(construct_hybercube_cluster(ip, port1 + cluster_nums * i, port2 + cluster_nums * i, no + cluster_nums * i, dim - 2))
    for i, node in enumerate(nodes):  # 设置各个节点相应的邻居节点
        node.add_neighbor(nodes[(i + cluster_nums) % node_nums].address())
        node.add_neighbor(nodes[(i - cluster_nums + node_nums) % node_nums].address())
    return nodes
    
# 与上一个函数类似，只不过因为要在两个主机上构造拓扑     
def construct_hybercube(addrs: str, dim: int):
    addrs = addrs.split(",")
    ip1, port1, port2 = addrs[0].split(':')
    ip2, port3, port4 = addrs[1].split(':')
    port1, port2, port3, port4 = int(port1), int(port2), int(port3), int(port4)
    node_nums = 2 ** dim
    cluster_nums = 2 ** (dim - 2)
    nodes = []
    for i in range(4):
        if i < 2:
            nodes.extend(construct_hybercube_cluster(ip1, port1 + cluster_nums * i, port2 + cluster_nums * i, 1 + cluster_nums * i, dim - 2))
        else:
            nodes.extend(construct_hybercube_cluster(ip2, port3 + cluster_nums * (i // 3), port4 + cluster_nums * (i // 3), 1 + cluster_nums * i, dim - 2))
    for i, node in enumerate(nodes):
        node.add_neighbor(nodes[(i + cluster_nums) % node_nums].address())
        node.add_neighbor(nodes[(i - cluster_nums + node_nums) % node_nums].address())
    return nodes

           
# 构造总线拓扑      
def construct_bus_cluster(ip: str, port1: int, port2: int, no: int, dim: int):
    nodes = []
    node_nums = 2 ** dim
    before_node = None
    for i in range(node_nums):
        node = Node(f'Node{no + i}', ip, port1 + i, masterAddr, '30000', [])
        if before_node:
            node.add_neighbor(before_node.address())
            before_node.add_neighbor(node.address())
        before_node = node
        nodes.append(node)
    return nodes


# 构造总线拓扑
def construct_bus(addrs: str, dim: int):
    addrs = addrs.split(",")
    ip1, port1, port2 = addrs[0].split(':')
    ip2, port3, port4 = addrs[1].split(':')
    port1, port2, port3, port4 = int(port1), int(port2), int(port3), int(port4)
    node_nums = 2 ** dim
    nodes = []
    nodes.extend(construct_bus_cluster(ip1, port1, port2, 1, dim - 1))
    nodes.extend(construct_bus_cluster(ip2, port3, port4, 1 + node_nums // 2, dim - 1))
    nodes[node_nums // 2].add_neighbor(nodes[node_nums // 2 + 1].address())
    nodes[node_nums // 2 + 1].add_neighbor(nodes[node_nums // 2].address())
    return nodes


# 构造环形拓扑
def construct_ring(addrs: str, dim: int):
    addrs = addrs.split(",")
    ip1, port1, port2 = addrs[0].split(':')
    ip2, port3, port4 = addrs[1].split(':')
    port1, port2, port3, port4 = int(port1), int(port2), int(port3), int(port4)
    node_nums = 2 ** dim
    nodes = []
    nodes.extend(construct_bus_cluster(ip1, port1, port2, 1, dim - 1))
    nodes.extend(construct_bus_cluster(ip2, port3, port4, 1 + node_nums // 2, dim - 1))
    nodes[node_nums // 2].add_neighbor(nodes[node_nums // 2 + 1].address())
    nodes[node_nums // 2 + 1].add_neighbor(nodes[node_nums // 2].address())
    nodes[0].add_neighbor(nodes[-1].address())
    nodes[-1].add_neighbor(nodes[0].address())
    return nodes
    
def create_topology(topology: str, dim: int):
    # 输入数据检查
    assert topology in ['hybercube', 'ring', 'bus']
    assert dim > 1 and type(args.dim) == int
    addr = f"{masterAddr}:30000:30500,{slaveAddr}:30000:30500"
    if args.topology == 'hybercube':
        nodes = construct_hybercube(addr, args.dim)
    elif args.topology == 'bus':
        nodes = construct_bus(addr, args.dim)
    else:
        nodes = construct_ring(addr, args.dim)
    with open(f'config/{args.topology}-{args.dim}.ini', 'w') as f:
        for node in nodes:
            f.write(node.str())
            
            
def main():
    create_topology('bus', 4)
    create_topology('ring', 4)
    for i in range(2, 10):
        create_topology('hybercube', i)
            
    
if __name__ == '__main__':
    main()