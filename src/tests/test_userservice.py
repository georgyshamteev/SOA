import requests
import pytest
import warnings
import sys
import json
import random
import string

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

def test_login_update_and_get_profile():
    signup_response = requests.post(f"{BASE_URL}/user/signup", json={"username": "gooduser", "password": "pass", "email": "good@ya.ru"})
    assert signup_response.status_code == 200

    login_response = requests.post(f"{BASE_URL}/user/login", json={"username": "gooduser", "password": "pass"})
    assert login_response.status_code == 200

    cookies = login_response.cookies
    update_response = requests.put(f"{BASE_URL}/user/change_profile", json={
        "name" : "John",
        "surname" : "Green",
        "birthdate" : "27.09.2004",
        "phone" : "88005553535",
        "bio" : "Проще позвонить чем у кого-то занимать"
    }, cookies=cookies)
    assert update_response.status_code == 200

    profile_response = requests.get(f"{BASE_URL}/user/myprofile", cookies=cookies)
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["name"] == "John"
    assert profile["surname"] == "Green"
    assert profile["phone"] == "88005553535"
    assert profile["bio"] == "Проще позвонить чем у кого-то занимать"
    assert profile["birthdate"] == "27.09.2004"

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def get_cookie(user):
    try:
        signup_response = requests.post(f"{BASE_URL}/user/signup", json={"username": user, "password": "accesspass", "email": user + "@ya.ru"})
    except:
        print("user already exists")
    login_response = requests.post(f"{BASE_URL}/user/login", json={"username": user, "password": "accesspass"})

    return login_response.cookies

def test_create_post():
    post_data = {
        "title": f"Test Post {random_string()}",
        "description": "This is a test post description",
        "is_private": False,
        "tags": ["test", "pytest"]
    }
    
    response = requests.post(f"{BASE_URL}/posts", json=post_data, cookies=get_cookie("user1"))
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == post_data["title"]
    assert data["description"] == post_data["description"]
    assert set(data["tags"]) == set(post_data["tags"])
    return data["id"]

def test_get_post():
    post_id = test_create_post()
    response = requests.get(f"{BASE_URL}/posts/{post_id}", cookies=get_cookie("user1"))
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "description" in data
    assert "tags" in data

def test_update_post():
    post_id = test_create_post()
    update_data = {
        "title": f"Updated Post {random_string()}",
        "description": "This post has been updated",
        "is_private": True,
        "tags": ["updated", "test"]
    }
    
    response = requests.put(f"{BASE_URL}/posts/{post_id}", json=update_data, cookies=get_cookie("user1"))
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert set(data["tags"]) == set(update_data["tags"])

def test_delete_post():
    post_id = test_create_post()
    response = requests.delete(f"{BASE_URL}/posts/{post_id}", cookies=get_cookie("user1"))
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    
    response = requests.get(f"{BASE_URL}/posts/{post_id}", cookies=get_cookie("user1"))
    assert response.status_code != 200

def test_list_posts():
    for _ in range(3):
        test_create_post()
    
    response = requests.get(f"{BASE_URL}/posts?page=1&page_size=10", cookies=get_cookie("user1"))
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert len(data["posts"]) > 0

def test_private_post_visibility():
    post_data = {
        "title": f"Private Post {random_string()}",
        "description": "This is a private post",
        "is_private": True,
        "tags": ["private", "test"]
    }
    
    response = requests.post(f"{BASE_URL}/posts", json=post_data, cookies=get_cookie("user1"))
    post_id = response.json()["id"]
    
    response = requests.get(f"{BASE_URL}/posts/{post_id}", cookies=get_cookie("user1"))
    assert response.status_code == 200
    
    response = requests.get(f"{BASE_URL}/posts/{post_id}", cookies=get_cookie("user2"))
    assert response.status_code != 200

def test_filter_by_tag():
    tag = f"unique_tag_{random_string()}"
    post_data = {
        "title": f"Tagged Post {random_string()}",
        "description": "This post has a unique tag",
        "tags": [tag]
    }
    
    requests.post(f"{BASE_URL}/posts", json=post_data, cookies=get_cookie("user1"))
    
    response = requests.get(f"{BASE_URL}/posts?tag={tag}", cookies=get_cookie("user1"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["posts"]) >= 1
    assert any(tag in post["tags"] for post in data["posts"])

