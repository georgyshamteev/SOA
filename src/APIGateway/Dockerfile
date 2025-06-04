FROM python:3.10

WORKDIR /APIGateway/

COPY requirements.txt /APIGateway/

RUN pip install -r requirements.txt

COPY . .

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/post.proto
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/statistics.proto

RUN chmod +x ./wait-for-it.sh

ENTRYPOINT ["./wait-for-it.sh", "userservice:5001", "--", "python", "gateway.py"]
