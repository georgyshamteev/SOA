from flask import Flask, request, jsonify, make_response
import requests

app = Flask("proxy_service")

SERVICES = {
    "user": "http://localhost:5001",
    "posts": "http://localhost:5002",
    "stats": "http://localhost:5003"
}

def get_user_from_token(request):
    token = request.cookies.get("jwt")
    if not token:
        return jsonify({"message": "Unauthorized: Missing token"}), 401
    try:
        data = jwt.decode(token, public_key, algorithms=["RS256"])
        current_user = data["username"]
        if current_user not in users:
            return jsonify({"message": "No such user"}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 400
    return current_user, 200

def proxy_request(service_prefix):
    service_url = SERVICES.get(service_prefix)
    if not service_url:
        return jsonify({"error": "Service not found"}), 404

    if service_prefix != "user":
        current_user_or_error, code = get_user_from_token(request)

        if code != 200:
            return make_response(current_user_or_error, code)
        
        current_user = current_user_or_error

    url = f"{service_url}{request.path}"
    response = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    
    resp = jsonify(response.json() if response.content else {})
    resp.status_code = response.status_code
    return resp

########################## User service routes ##########################
@app.route('/user/signup', methods=['POST'])
@app.route('/user/login', methods=['POST'])
@app.route('/user/whoami', methods=['GET'])
def handle_user_request():
    return proxy_request("user")

########################## Posts service routes #########################
@app.route('posts/...', methods=['...'])
def handle_posts_request():
    return proxy_request("posts")

########################## Stats service routes #########################
@app.route('/stats/...', methods=['...'])
def handle_stats_request(user_id=None):
    return proxy_request("stats")


if __name__ == '__main__':
    app.run(port=5000)