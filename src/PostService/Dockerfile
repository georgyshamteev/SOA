FROM python:3.9-slim

WORKDIR /PostService/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/post.proto

EXPOSE 50051

ENTRYPOINT ["python", "-m", "service.app"]
