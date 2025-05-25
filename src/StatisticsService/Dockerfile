FROM python:3.10

WORKDIR /StatisticsService/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p proto

RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/statistics.proto

CMD ["python", "server.py"]
