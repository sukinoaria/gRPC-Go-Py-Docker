cp ../SA.proto ./
sudo docker build . -t grpc-server
rm -f SA.proto
sudo docker run -d -p 8089:8089 grpc-server