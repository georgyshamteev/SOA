FROM python:3.12

WORKDIR /UserService/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY ../Broker/kafka_producer.py .

RUN chmod +x utils/wait-for-it.sh

ENTRYPOINT ["utils/wait-for-it.sh", "postgresql:5432", "--", "python", "-m", "service.auth_service", "--private", "keys/signature.pem", "--public", "keys/signature.pub"]