import requests
import pytest
import warnings
import sys

warnings.filterwarnings('ignore')

BASE_URL = "http://proxyservice:5000"

def test_signup_user_already_exists():
    requests.post(f"{BASE_URL}/user/signup", json={"username": "existinguser", "password": "password", "email": "1@ya.ru"})
    response = requests.post(f"{BASE_URL}/user/signup", json={"username": "existinguser", "password": "password", "email": "1@ya.ru"})
    assert response.status_code == 403
    assert "User already exists" in response.json().get("message", "")

def test_login_wrong_username():
    response = requests.post(f"{BASE_URL}/user/login", json={"username": "wronguser", "password": "password"})
    assert response.status_code == 403
    assert "Invalid username or password" in response.json().get("message", "")

def test_login_wrong_password():
    requests.post(f"{BASE_URL}/user/signup", json={"username": "testuser", "password": "correctpass", "email": "2@ya.ru"})

    response = requests.post(f"{BASE_URL}/user/login", json={"username": "testuser", "password": "wrongpass"})
    assert response.status_code == 403
    assert "Invalid username or password" in response.json().get("message", "")

def test_whoami_no_token():
    response = requests.get(f"{BASE_URL}/user/whoami")
    assert response.status_code == 401
    assert "Unauthorized: Missing token" in response.json().get("message", "")

def test_whoami_invalid_token():
    response = requests.get(f"{BASE_URL}/user/whoami", cookies={'jwt': 'fake.token.jwt'})
    assert response.status_code == 400
    assert "Invalid token" in response.json().get("message", "")

def test_login_and_access_resource():
    signup_response = requests.post(f"{BASE_URL}/user/signup", json={"username": "accessuser", "password": "accesspass", "email": "3@ya.ru"})
    assert signup_response.status_code == 200

    login_response = requests.post(f"{BASE_URL}/user/login", json={"username": "accessuser", "password": "accesspass"})
    assert login_response.status_code == 200

    cookies = login_response.cookies
    whoami_response = requests.get(f"{BASE_URL}/user/whoami", cookies=cookies)
    assert whoami_response.status_code == 200
    assert "Hello, accessuser" in whoami_response.text
