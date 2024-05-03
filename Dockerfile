FROM ubuntu:18.04

# 拷贝文件
RUN mkdir /Gossip
ADD gossip /Gossip/gossip
ADD mgossip /Gossip/mgossip
ADD calculate.py /Gossip
ADD clean_data.py /Gossip
ADD go.work /Gossip
ADD go.work.sum /Gossip
ADD master.py /Gossip
ADD run.sh /Gossip
ADD slave.py /Gossip
ADD topology.py /Gossip

# 安装各种工具
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install wget && wget https://golang.google.cn/dl/go1.21.3.linux-arm64.tar.gz && tar -C /usr/local -xzf go1.21.3.linux-arm64.tar.gz && apt-get -y install net-tools && apt-get -y install iputils-ping && apt-get -y install vim && apt-get -y  install openssh-server openssh-client && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && service ssh restart && apt-get -y install passwd && echo 'root:mgossipBetter' | chpasswd && apt-get -y install expect && apt-get -y install curl && apt-get -y install python3-pip 
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple markupsafe==1.1.1 && pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple flask

# 设置环境变量
ENV MASTER=172.17.0.2
ENV SLAVE=172.17.0.3
ENV WORKDIR=/Gossip
ENV USER=root
ENV PASSWD=mgossipBetter
ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPROXY=https://goproxy.io


RUN cd Gossip && mkdir config && rm -rf mgossip/config && rm -rf gossip/config && python3 topology.py && cp -r config mgossip && cp -r config gossip
RUN cd $WORKDIR && cd mgossip && go install && cd ../gossip && go install