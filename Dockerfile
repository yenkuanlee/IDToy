# iServStor
FROM ubuntu:18.04
MAINTAINER Docker Newbee yenkuanlee@gmail.com

RUN apt-get -qq update

RUN apt-get -qqy install sudo
RUN apt-get -qqy install python python-dev
RUN apt-get -qqy install wget
RUN apt-get -qqy install vim
RUN apt-get -qqy install net-tools # ifconfig
RUN apt-get -qqy install git

RUN apt-get -qqy install python3.6-dev
RUN apt -qqy install python3-setuptools
RUN apt-get -qqy install python3-pip
RUN apt -qqy install software-properties-common
RUN add-apt-repository ppa:ethereum/ethereum
RUN apt-get update
RUN apt-get -qqy install solc
RUN pip3 install web3
RUN pip3 install py-solc
RUN pip3 install ipfsapi
RUN apt-get -qqy install geth
RUN apt-get install -y locales
RUN locale-gen zh_TW zh_TW.UTF-8 zh_CN.UTF-8 en_US.UTF-8

# python-Ethereum
RUN apt-get -qqy install libssl-dev build-essential automake pkg-config libtool libffi-dev libgmp-dev libyaml-cpp-dev
RUN cd /tmp && \
git clone https://github.com/ethereum/pyethereum && \
cd /tmp/pyethereum && \
python3 setup.py install

# ipfs
RUN cd /tmp && \
wget https://dist.ipfs.io/go-ipfs/v0.4.17/go-ipfs_v0.4.17_linux-amd64.tar.gz && \
tar xvfz go-ipfs_*.tar.gz && \
mv go-ipfs/ipfs /usr/local/bin/ipfs


RUN useradd -m localadmin && echo "localadmin:openstack" | chpasswd && adduser localadmin sudo
USER localadmin
RUN cd && \
git clone http://github.com/yenkuanlee/IDToy && \
cd IDToy/demo && \
geth --datadir ./kevin/ init genesis.json && \
ipfs init
RUN echo 'export LC_ALL=zh_TW.utf8' >> /home/localadmin/.bashrc


