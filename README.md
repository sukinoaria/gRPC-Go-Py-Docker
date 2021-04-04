# gPRC-Go-Py-Docker

### 需求：
    - Python端为服务端，结合Pytorch等框架实现对文本的情感分析
    - Golang为后端，完成用户的数据管理、数据分析以及服务端算法调用等
    - 为方便部署，两端均在Docker容器中完成
### 系统抽象
    - Golang后端将List<String>类型的数据传入Python
    - Python对数据进行一定的处理并返回(为简化demo代码，仅简单模拟该操作)
    - 通信通过Docker完成


### Step 1 两端交互部分proto定义
proto3版的数据结构可以参考[官方文档](https://developers.google.com/protocol-buffers/docs/proto3)

proto3中文介绍[ProtoBuf v3 语法简介](https://www.jianshu.com/p/e9d6af587cf6)

在本demo中，后端对算法端的请求为三种：

    - Task1: 输入多条变长的文本(List<String>)，进行文本情感极性的分类，返回List<int>型变量.
    - Task2: 输入多条变长的文本(List<String>)，进行文本意见信息抽取，返回List<<String,String,int>>型变量.
    - Task3: 输入多个评价方面(List<String>)，进行文本意见信息抽取，返回List<int>型变量.
在proto3中，使用的数据类型即int和string两种，另外使用repeated构造变长数组，SA.proto具体内容如下：
```shell
syntax = "proto3"; //protobuf版本

package sa_protoc; //在go中要使用的报名

// 输入数据格式定义，List<String>
message InTextArray {
    repeated string texts = 1; //多条文本输入
}

// Task1、task3输出 List<int>
message OutLabelArray {
    repeated int32 labels = 1;
}

// Task2输出 List<<String,String,int>>
message Triplet {
    string aspect = 1;
    string opinion = 2;
    int32 label = 3;
}
message OutTripletArray {
    repeated Triplet triplets = 1;
}

//服务定义
service SentimentAnalysis {
    //task1 情感极性预测
    rpc SentiCLS (InTextArray) returns (OutLabelArray);

    //task2 意见三元组抽取
    rpc TripExtract (InTextArray) returns (OutTripletArray);

    //task3 评价方面聚类
    rpc Cluster (InTextArray) returns (OutLabelArray);
}
```
需要注意的点：
- repeated为变长数组，最后面的数字为占位符
- 在编译完proto文件后，go和python的数据格式定义有些许区别，以OutTripletArray为例：
python
```python
# 构造返回结果
triplet = SA_pb2.Triplet(aspect="asp",opinion="opi",label=1)
SA_pb2.OutTripletArray(triplets=[triplet])
```
Go
```go
//调用rpc服务
reply, _ := client.TripExtract(context.Background(), &sa_protoc.InTextArray{Texts:test_data})
fmt.Println(reply.Triplets[0].Aspect) //获取返回结果数组中第一个三元组的aspect
```

### Step 2 Python服务端
#### proto编译
需要的依赖包：grpcio grpcio-tools

参考链接[python与golang通过grpc进行通信](https://my.oschina.net/daba0007/blog/3189858)
编译过程：
```shell
python3 -m grpc_tools.protoc --python_out=. --grpc_python_out=. --proto_path .. -I. SA.proto
```
生成后的server端目录：
```shell
server-Py/
    Dockerfile          //之后用于写docker镜像构建命令
    requirements.txt  //grpcio grpcio-tools以及其他依赖
    SA_pb2.py         //protoc生成的文件
    SA_pb2_grpc.py    //protoc生成的文件
    server.py         //用于启动rpc的服务端
```
#### 本地启动rpc server
在前面生成了SA_pb2.py以及SA_pb2_grpc.py两个文件后，可以编写server.py，实现服务对应的接口
```python
from concurrent import futures
import time
import grpc

import SA_pb2
import SA_pb2_grpc

# 实现proto文件中定义的接口
class SAServicer(SA_pb2_grpc.SentimentAnalysisServicer):
    # 实现 proto 文件中定义的 rpc 调用
    def SentiCLS(self, request, context):
        print("[Task] run sentiment classification ...")
        text_data = request.texts
        print(text_data)
        return_labels = [0 for _ in range(len(text_data))]
        return SA_pb2.OutLabelArray(labels=return_labels)

    def TripExtract(self,request,context):
        print("[Task] run triplets extraction ...")
        text_data = request.texts
        print(text_data)
        return_value = [SA_pb2.Triplet(aspect="asp",opinion="opi",label=1) for _ in range(len(text_data))]
        print(return_value)
        return SA_pb2.OutTripletArray(triplets=return_value)

    def Cluster(self,request,context):
        print("[Task] run Cluster ...")
        text_data = request.texts
        print(text_data)
        return_labels = [2 for _ in range(len(text_data))]
        return SA_pb2.OutLabelArray(labels=return_labels)

# 定义开启4个线程处理接收到的请求
server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
# 将编译出来的SA_pb2_grpc的add_SentimentAnalysisServicer_to_server函数添加到server中
SA_pb2_grpc.add_SentimentAnalysisServicer_to_server(SAServicer(), server)

# 定义服务端端口8089
server.add_insecure_port('127.0.0.1:8089')
print("Python server started on :[8089]")
server.start()

# 长期监听
try:
    while True:
        time.sleep(60 * 60 * 24)
except KeyboardInterrupt:
    server.stop(0)
```
启动服务：
```shell
python3 server.py
```

#### Docker版 rpc server
基于docker可以便捷地将应用迁移到其他环境下，方便环境的配置。

Dockerfile
```dockerfile
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
```
使用bash脚本执行build过程：
```shell
cp ../SA.proto ./
sudo docker build . -t grpc-server
rm -f SA.proto
sudo docker run -d -p 8089:8089 grpc-server
```

### Step 3 Go客户端
#### proto编译