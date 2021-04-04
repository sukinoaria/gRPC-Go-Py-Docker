package main

import (
	"fmt"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"log"
	"main/sa_rpc"
)

func main() {
	// 连接服务端接口
	conn, err := grpc.Dial("127.0.0.1:8089", grpc.WithInsecure())
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	// 通过编译rpc.pb.go得到的函数来处理连接
	client := sa_protoc.NewSentimentAnalysisClient(conn)
	// 通过编译rpc.pb.go得到的服务来发送数据类型为[]String的数据
	test_data := []string{"test1", "test1", "test1"}

	//task1
	reply, err := client.SentiCLS(context.Background(), &sa_protoc.InTextArray{Texts: test_data})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(reply.Labels)

	//task2
	reply2, err2 := client.TripExtract(context.Background(), &sa_protoc.InTextArray{Texts: test_data})
	if err2 != nil {
		log.Fatal(err2)
	}
	fmt.Println(reply2.Triplets[0].Aspect)
	//task3
	reply3, err3 := client.Cluster(context.Background(), &sa_protoc.InTextArray{Texts: test_data})
	if err3 != nil {
		log.Fatal(err3)
	}
	fmt.Println(reply3.Labels)
}
