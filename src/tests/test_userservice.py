import requests
import pytest

BASE_URL = "http://proxyservice:5000"

def test_signup_user_already_exists():
    requests.post(f"{BASE_URL}/user/signup", json={"username": "existinguser", "password": "password"})
    response = requests.post(f"{BASE_URL}/user/signup", json={"username": "existinguser", "password": "password"})
    assert response.status_code == 403
    assert "User already exists" in response.json().get("message", "")

def test_login_wrong_username():
    response = requests.post(f"{BASE_URL}/user/login", json={"username": "wronguser", "password": "password"})
    assert response.status_code == 403
    assert "Invalid username or password" in response.json().get("message", "")

def test_login_wrong_password():
    # Ensure user exists
    requests.post(f"{BASE_URL}/user/signup", json={"username": "testuser", "password": "correctpass"})

    response = requests.post(f"{BASE_URL}/user/login", json={"username": "testuser", "password": "wrongpass"})
    assert response.status_code == 403
    assert "Invalid username or password" in response.json().get("message", "")

def test_whoami_no_token():
    response = requests.get(f"{BASE_URL}/user/whoami")
    assert response.status_code == 401
    assert "Unauthorized: Missing token" in response.json().get("message", "")

def test_whoami_invalid_token():
    # Simulate a request with an invalid token
    response = requests.get(f"{BASE_URL}/user/whoami", cookies={'jwt': 'fake.token.jwt'})
    assert response.status_code == 400
    assert "Invalid token" in response.json().get("message", "")

def test_whoami_expired_token():
    # Предполагается, что вы каким-то образом можете создать тестовый случай с действительно истекшим JWT
    # Здесь мы не знаем, как сервер генерирует истекшие токены, но в реальном платье можем использовать мокирование
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEwMDAwMDAwMDB9.fake_signature"
    response = requests.get(f"{BASE_URL}/user/whoami", cookies={'jwt': expired_token})
    assert response.status_code == 401
    assert "Token has expired" in response.json().get("message", "")

def test_login_and_access_resource():
    requests.post(f"{BASE_URL}/user/signup", json={"username": "accessuser", "password": "accesspass"})
    login_response = requests.post(f"{BASE_URL}/user/login", json={"username": "accessuser", "password": "accesspass"})
    assert login_response.status_code == 200

    cookies = login_response.cookies
    whoami_response = requests.get(f"{BASE_URL}/user/whoami", cookies=cookies)
    assert whoami_response.status_code == 200
    assert "Hello, accessuser" in whoami_response.text