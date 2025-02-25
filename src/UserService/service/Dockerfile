FROM python:3.12

WORKDIR /practice-security/auth

COPY auth_service.py /practice-security/auth/
COPY requirements.txt /practice-security/auth/

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "auth_service.py"]
