FROM python:3.12

WORKDIR /tests/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./wait-for-it.sh

ENTRYPOINT ["./wait-for-it.sh", "proxyservice:5000", "--", "pytest", "-vs", "--log-level=INFO"]
