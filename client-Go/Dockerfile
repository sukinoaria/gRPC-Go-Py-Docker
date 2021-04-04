FROM golang:latest

# Install grpc
RUN go env -w GO111MODULE=on && \
    go env -w GOPROXY=https://goproxy.cn,https://mirrors.aliyun.com/goproxy/,direct && \
    go get -u google.golang.org/grpc && \
    go get -u github.com/gogo/protobuf/protoc-gen-gofast

# Copy the grpc proto file
RUN mkdir -p /client/
COPY SA.proto client.go go.mod protoc-3.15.6-linux-x86_64.zip  /client/
COPY sources.list /etc/apt/

# install protoc
RUN apt-get clean && \
    apt-get update && apt-get install -y zip && \
    mkdir /opt/protoc && cd /opt/protoc && cp /client/protoc-3.15.6-linux-x86_64.zip ./ && \
    unzip protoc-3.15.6-linux-x86_64.zip

ENV PATH=$PATH:$GOPATH/bin:/opt/protoc/bin

# build run file rpc-client
RUN cd /client && go mod tidy && go mod download && mkdir sa_rpc/ && \
    protoc -I. SA.proto --gofast_out=plugins=grpc:sa_rpc && go build -o rpc-client client.go