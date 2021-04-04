FROM ubuntu:18.04
MAINTAINER lunarche "cpxnku@gmail.com"

# set update source for chinese user
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
    apt-get clean && \
    apt-get -y update

# cp required files
RUN mkdir -p /server/
COPY SA.proto server.py requirements.txt /server/

WORKDIR /server
RUN apt-get install -y python3.6 python3-pip bash python3-dev
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip && \
    pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple && \
    pip3 config set install.trusted-host mirrors.aliyun.com && \
    pip3 install --no-cache-dir -r requirements.txt

# build proto file
RUN python3 -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. SA.proto

CMD python3 server.py