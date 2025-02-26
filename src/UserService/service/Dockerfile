FROM python:3.12

WORKDIR /UserService/service/

COPY requirements.txt /UserService/service/

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./wait-for-it.sh

ENTRYPOINT ["./wait-for-it.sh", "postgresql:5432", "--", "python", "auth_service.py", "--private", "./signature.pem", "--public", "signature.pub"]