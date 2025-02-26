import argparse
from flask import Flask, request, jsonify, make_response
from werkzeug.security import check_password_hash
import jwt
import datetime
from models import User, db
from flask_sqlalchemy import SQLAlchemy

auth_service = Flask("auth_service")
auth_service.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://userservice:userservicepass@userservice_db:5432/userservicedb'
auth_service.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(auth_service)

private_key = None
public_key = None

def get_user_from_token(request):
    token = request.cookies.get("jwt")
    if not token:
        return jsonify({"message": "Unauthorized: Missing token"}), 401
    try:
        data = jwt.decode(token, public_key, algorithms=["RS256"])
        current_user = User.query.filter_by(username=data["username"]).first()
        if not current_user:
            return jsonify({"message": "No such user"}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 400
    return current_user.username, 200

@auth_service.route("/user/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 403

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode(
        {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        private_key,
        algorithm="RS256"
    )
    response = make_response(jsonify({"message": "User registered successfully"}), 200)
    response.set_cookie("jwt", token)
    return response

@auth_service.route("/user/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 403

    token = jwt.encode(
        {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        private_key,
        algorithm="RS256"
    )
    response = make_response(jsonify({"message": "Login successful"}), 200)
    response.set_cookie("jwt", token)
    return response

@auth_service.route("/user/whoami", methods=["GET"])
def whoami():
    current_user_or_error, code = get_user_from_token(request)

    if code != 200:
        return current_user_or_error, code

    current_user = current_user_or_error

    return f"Hello, {current_user}", 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сервис авторизации")

    parser.add_argument("--private", required=True, help="Путь до приватного ключа")
    parser.add_argument("--public", required=True, help="Путь до публичного ключа")
    parser.add_argument("--port", type=int, default=5001, help="Порт для запуска HTTP сервера (по умолчанию 5001)")

    args = parser.parse_args()

    try:
        with open(args.private, "r") as private_file:
            private_key = private_file.read()
        with open(args.public, "r") as public_file:
            public_key = public_file.read()
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        exit(0)

    with auth_service.app_context():
        db.create_all()

    print(f"Сервер запущен на порту: {args.port}")

    auth_service.run(debug=True, host='0.0.0.0', port=args.port)
