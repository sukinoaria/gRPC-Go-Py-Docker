cp ../SA.proto ./
sudo docker build . -t grpc-client
rm -f SA.proto
sudo docker run --network="host" -it grpc-client /bin/bash