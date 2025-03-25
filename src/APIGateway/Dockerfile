FROM python:3.12

WORKDIR /APIGateway/

COPY requirements.txt /APIGateway/

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./wait-for-it.sh

ENTRYPOINT ["./wait-for-it.sh", "userservice:5001", "--", "python", "gateway.py"]
