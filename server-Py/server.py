from concurrent import futures
import time
import grpc

import SA_pb2
import SA_pb2_grpc

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

# 定义服务端端口1234
server.add_insecure_port('[::]:8089')
print("Python server started on :[8089]")
server.start()

# 长期监听
try:
    while True:
        time.sleep(60 * 60 * 24)
except KeyboardInterrupt:
    server.stop(0)
