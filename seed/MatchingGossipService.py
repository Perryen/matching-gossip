from seedemu.core import Node, Service, Server

import os

class MatchingGossipServer(Server):
    
    def __init__(self):
        super().__init__()
    
    
    def install(self, node: Node):
        node.addSoftware("python3-pip")
        node.addBuildCommand("pip3 install flask")
        with open("work.py", "r", encoding="utf8") as f:
            node.setFile("/root/work.py", f.read())
        node.appendStartCommand("python3 /root/work.py")
            

class MatchingGossipService(Service):
    def __init__(self):
        pass
    
    
    def _createServer(self) -> Server:
        return MatchingGossipServer()
    
    