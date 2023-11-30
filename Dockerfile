FROM ubuntu:18.04

# 拷贝文件
RUN mkdir /Gossip
ADD gossip /Gossip/gossip
ADD MGossip /Gossip/MGossip
ADD calculate.py /Gossip
ADD clean_data.py /Gossip
ADD go.work /Gossip
ADD go.work.sum /Gossip
ADD master.py /Gossip
ADD run.sh /Gossip
ADD slave.py /Gossip
ADD topology.py /Gossip

# 安装各种工具
RUN echo "deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse" > /etc/apt/sources.list && echo "deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse" >> /etc/apt/sources.list && echo "deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse" >> /etc/apt/sources.list && apt-get update && apt-get upgrade && apt-get -y  install wget && wget https://golang.google.cn/dl/go1.21.3.linux-amd64.tar.gz && tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz && apt-get -y install net-tools && apt-get -y install iputils-ping && apt-get -y install vim && apt-get -y  install openssh-server openssh-client && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && service ssh restart && apt-get -y install passwd && echo 'root:mgossipBetter' | chpasswd && apt-get -y install expect && apt-get -y install curl && apt-get -y python3-pip && pip3 install flask

# 设置环境变量
ENV MASTER=172.17.0.2
ENV SLAVE=172.17.0.3
ENV WORKDIR=/Gossip
ENV USER=root
ENV PASSWD=mgossipBetter
ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPROXY=https://goproxy.io


RUN cd Gossip && mkdir config && rm -rf MGossip/config && rm -rf gossip/config && python3 topology.py && cp -r config MGossip && cp -r config gossip



#47.99.117.138







