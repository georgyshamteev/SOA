FROM python:3.10

WORKDIR /UserService/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x utils/wait-for-it.sh

ENTRYPOINT ["utils/wait-for-it.sh", "postgresql:5432", "--", "python", "-m", "service.auth_service", "--private", "keys/signature.pem", "--public", "keys/signature.pub"]