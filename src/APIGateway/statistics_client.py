import grpc
from proto import statistics_pb2 as pb2
from proto import statistics_pb2_grpc as pb2_grpc

def get_statistics_client():
    channel = grpc.insecure_channel('statistics_service:50052')
    return pb2_grpc.StatisticsServiceStub(channel)

def get_post_stats(post_id):
    client = get_statistics_client()
    try:
        response = client.GetPostStats(pb2.PostIdRequest(post_id=int(post_id)))
        return {
            'views': response.views,
            'likes': response.likes,
            'comments': response.comments
        }
    except grpc.RpcError as e:
        print(f"Error getting post stats: {e}")
        return {'views': 0, 'likes': 0, 'comments': 0}

def get_view_dynamics(post_id):
    client = get_statistics_client()
    try:
        response = client.GetViewDynamics(pb2.PostIdRequest(post_id=int(post_id)))
        return [{'date': day.date, 'count': day.count} for day in response.data]
    except grpc.RpcError as e:
        print(f"Error getting view dynamics: {e}")
        return []

def get_like_dynamics(post_id):
    client = get_statistics_client()
    try:
        response = client.GetLikeDynamics(pb2.PostIdRequest(post_id=int(post_id)))
        return [{'date': day.date, 'count': day.count} for day in response.data]
    except grpc.RpcError as e:
        print(f"Error getting like dynamics: {e}")
        return []

def get_comment_dynamics(post_id):
    client = get_statistics_client()
    try:
        response = client.GetCommentDynamics(pb2.PostIdRequest(post_id=int(post_id)))
        return [{'date': day.date, 'count': day.count} for day in response.data]
    except grpc.RpcError as e:
        print(f"Error getting comment dynamics: {e}")
        return []

def get_top_posts(metric_type):
    client = get_statistics_client()
    try:
        metric_map = {
            'view': pb2.TopRequest.MetricType.VIEW,
            'like': pb2.TopRequest.MetricType.LIKE,
            'comment': pb2.TopRequest.MetricType.COMMENT
        }
        metric = metric_map.get(metric_type.lower(), pb2.TopRequest.MetricType.VIEW)
        response = client.GetTopPosts(pb2.TopRequest(metric=metric))
        return [{'post_id': int(post.post_id), 'count': post.count} for post in response.top_posts]
    except grpc.RpcError as e:
        print(f"Error getting top posts: {e}")
        return []

def get_top_users(metric_type):
    client = get_statistics_client()
    try:
        metric_map = {
            'view': pb2.TopRequest.MetricType.VIEW,
            'like': pb2.TopRequest.MetricType.LIKE,
            'comment': pb2.TopRequest.MetricType.COMMENT
        }
        metric = metric_map.get(metric_type.lower(), pb2.TopRequest.MetricType.VIEW)
        response = client.GetTopUsers(pb2.TopRequest(metric=metric))
        return [{'user_id': user.user_id, 'count': user.count} for user in response.top_users]
    except grpc.RpcError as e:
        print(f"Error getting top users: {e}")
        return []
