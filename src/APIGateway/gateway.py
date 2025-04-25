from flask import Flask, request, jsonify, make_response, Response
import requests
import jwt
import grpc
from proto import post_pb2, post_pb2_grpc
from kafka_producer import send_like_event, send_view_event, send_comment_event

app = Flask("proxy_service")

public_key = None

SERVICES = {
    "user": "http://userservice:5001",
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
        if not current_user:
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
    res = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    headers = [(name, value) for name, value in res.headers.items()]
    response = Response(res.content, res.status_code, headers)
    return response

########################## User service routes ##########################
@app.route('/user/change_profile', methods=['PUT'])
@app.route('/user/myprofile', methods=['GET'])
@app.route('/user/signup', methods=['POST'])
@app.route('/user/login', methods=['POST'])
@app.route('/user/whoami', methods=['GET'])
def handle_user_request():
    return proxy_request("user")

########################## Posts service routes #########################
def grpc_post_client():
    channel = grpc.insecure_channel('post_service:50051')
    return post_pb2_grpc.PostServiceStub(channel)

def post_to_dict(post):
    return {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'username': post.username,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'is_private': post.is_private,
        'tags': list(post.tags)
    }

@app.route('/posts', methods=['GET', 'POST'])
@app.route('/posts/<post_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_post_request(post_id=None):
    try:
        client = grpc_post_client()
        current_user_or_error, code = get_user_from_token(request)
        if code != 200:
            return make_response(current_user_or_error, code)
        username = current_user_or_error

        # GET list
        if request.method == 'GET' and not post_id:
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 10, type=int)
            tag = request.args.get('tag', '')
            response = client.ListPosts(post_pb2.ListPostsRequest(
                page=page, page_size=page_size, username=username, tag=tag
            ))
            for post in response.posts:
                send_view_event(username, post.id)
            return jsonify({
                'posts': [post_to_dict(post) for post in response.posts],
                'total': response.total,
                'page': response.page,
                'pages': response.pages
            })

        # GET one
        elif request.method == 'GET':
            response = client.GetPost(post_pb2.GetPostRequest(
                post_id=int(post_id), username=username
            ))
            return jsonify(post_to_dict(response.post))

        # POST - create
        elif request.method == 'POST':
            data = request.json
            response = client.CreatePost(post_pb2.CreatePostRequest(
                title=data.get('title', ''),
                description=data.get('description', ''),
                username=username,
                is_private=data.get('is_private', False),
                tags=data.get('tags', [])
            ))
            return jsonify(post_to_dict(response.post)), 201

        # PUT - update
        elif request.method == 'PUT':
            data = request.json
            response = client.UpdatePost(post_pb2.UpdatePostRequest(
                post_id=int(post_id),
                username=username,
                title=data.get('title', ''),
                description=data.get('description', ''),
                is_private=data.get('is_private', False),
                tags=data.get('tags', [])
            ))
            return jsonify(post_to_dict(response.post))

        # DELETE
        elif request.method == 'DELETE':
            response = client.DeletePost(post_pb2.DeletePostRequest(
                post_id=int(post_id), username=username
            ))
            return jsonify({'success': response.success, 'message': response.message})
    except:
        return jsonify({"message": "Error in rpc"}), 400


@app.route('/like/<post_id>', methods=['GET', 'POST'])
def handle_like_request(post_id=None):
    current_user_or_error, code = get_user_from_token(request)
    if code != 200:
        return make_response(current_user_or_error, code)
    username = current_user_or_error

    if request.method == 'POST':
        send_like_event(username, post_id)

    return jsonify({"message": "Success"}), 200

@app.route('/comment/<post_id>', methods=['GET', 'POST'])
def handle_comment_request(post_id=None):
    current_user_or_error, code = get_user_from_token(request)
    if code != 200:
        return make_response(current_user_or_error, code)
    username = current_user_or_error

    if request.method == 'POST':
        send_comment_event(username, post_id, "comment_id_placeholder")

    return jsonify({"message": "Success"}), 200


########################## Stats service routes #########################
@app.route('/stats/...', methods=['...'])
def handle_stats_request(username=None):
    return proxy_request("stats")


if __name__ == '__main__':
    try:
        with open("signature.pub", "r") as public_file:
            public_key = public_file.read()
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        exit(0)
    app.run(debug=True, host='0.0.0.0', port=5000)