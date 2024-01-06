"""topology.py构造大量节点的超立方体拓扑、总线拓扑、环形拓扑
"""
import os


masterAddr = os.environ.get("MASTER")
slaveAddrs = os.environ.get("SLAVES")


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
        # 不允许绑定公网IP
        self.bindAddr = '0.0.0.0'
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
def construct_hybercube_cluster(addrs, dim: int, no: int, port1: int, port2: int):
    if dim == 0: # 偶数维度超立方体拓扑递归终点
        return [Node(f'Node{no}', addrs[0], port1, masterAddr, '30000', port2, [])]
    if dim == 1:  # 奇数维度超立方体拓扑递归终点
        node1 = Node(f'Node{no}', addrs[0], port1, masterAddr, '30000', port2, [])
        if len(addrs) == 1:
            node2 = Node(f'Node{no + 1}', addrs[0], port1 + 1, masterAddr, '30000', port2 + 1, [])
        else:
            node2 = Node(f'Node{no + 1}', addrs[1], port1, masterAddr, '30000', port2, [])
        node1.add_neighbor(node2.address())
        node2.add_neighbor(node1.address())
        return [node1, node2]
    # 递归构造，相当与一个正方形拓扑，每一个端点都是dim-2维度的超立方体拓扑
    nodes = []
    cluster_nums = 2 ** (dim - 2)
    node_nums = 2 ** dim
    if len(addrs) >= 4:
        for i in range(4):
            nodes.extend(construct_hybercube_cluster(addrs[i * len(addrs) // 4: (i + 1) * len(addrs) // 4], dim - 2, no + i * cluster_nums, port1, port2)) 
    else:
        for i in range(4):
            bias = i % (4 // len(addrs))
            nodes.extend(construct_hybercube_cluster([addrs[i // (4 // len(addrs))]], dim - 2, no + i * cluster_nums, port1 + bias * cluster_nums, port2 + bias * cluster_nums)) 
    for i, node in enumerate(nodes):  # 设置各个节点相应的邻居节点
        node.add_neighbor(nodes[(i + cluster_nums) % node_nums].address())
        node.add_neighbor(nodes[(i - cluster_nums + node_nums) % node_nums].address())
    return nodes
    
# 与上一个函数类似，只不过因为要在两个主机上构造拓扑     
def construct_hybercube(addrs, dim: int):
    node_nums = 2 ** dim
    if len(addrs) >= node_nums:
        return construct_hybercube_cluster(addrs[: node_nums], dim, 1, 30000, 30200)
    else:
        return construct_hybercube_cluster(addrs, dim, 1, 30000, 30200)     
    

# 构造总线拓扑      
def construct_bus_cluster(addrs, dim: int, no: int, port1: int, port2: int):
    nodes = []
    node_nums = 2 ** dim
    cluster_nums = node_nums // len(addrs)
    before_node = None
    for i in range(node_nums):
        node = Node(f'Node{no + i}', addrs[i // cluster_nums], port1 + i % cluster_nums, masterAddr, '30000', port2 + i % cluster_nums, [])
        if before_node:
            node.add_neighbor(before_node.address())
            before_node.add_neighbor(node.address())
        before_node = node
        nodes.append(node)
    return nodes

# 构造总线拓扑
def construct_bus(addrs, dim: int):
    node_nums = 2 ** dim
    if len(addrs) >= node_nums:
        nodes = construct_bus_cluster(addrs[: node_nums], dim, 1, 30000, 30200)
    else:
        nodes = construct_bus_cluster(addrs, dim, 1, 30000, 30200)
    return nodes


# 构造环形拓扑
def construct_ring(addrs, dim: int):
    node_nums = 2 ** dim
    if len(addrs) >= node_nums:
        nodes = construct_bus_cluster(addrs[: node_nums], dim, 1, 30000, 30200)
    else:
        nodes = construct_bus_cluster(addrs, dim, 1, 30000, 30200)
    nodes[0].add_neighbor(nodes[-1].address())
    nodes[-1].add_neighbor(nodes[0].address())
    return nodes
    
    
def create_topology(topology: str, dim: int, addrs):
    # 输入数据检查
    assert topology in ['hybercube', 'ring', 'bus']
    assert dim > 1 and type(dim) == int
    if topology == 'hybercube':
        nodes = construct_hybercube(addrs, dim)
    elif topology == 'bus':
        nodes = construct_bus(addrs, dim)
    else:
        nodes = construct_ring(addrs, dim)
    with open(f'config/{topology}-{dim}.ini', 'w') as f:
        for node in nodes:
            f.write(node.str())
            
            
def main():
    slave_addrs = slaveAddrs.split(":")
    nodes = [str(masterAddr)]
    nodes.extend(slave_addrs)
    for i in range(2, 11):
        create_topology('hybercube', i, nodes)
        create_topology('bus', i, nodes)
        create_topology('ring', i, nodes)
            
    
if __name__ == '__main__':
    main()