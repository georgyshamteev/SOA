import grpc
import logging
from concurrent import futures
from db import get_clickhouse_client, wait_for_clickhouse
from consumer import start_kafka_consumers

import statistics_pb2 as pb2
import statistics_pb2_grpc as pb2_grpc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server')

GRPC_PORT = 50052

class StatisticsServicer(pb2_grpc.StatisticsServiceServicer):

    def __init__(self):
        self.clickhouse = get_clickhouse_client()

    def GetPostStats(self, request, context):
        post_id = int(request.post_id)
        try:
            logger.info("getting info")
            views = self._get_event_count('view', post_id)
            logger.info("got views")
            likes = self._get_event_count('like', post_id)
            logger.info("got likes")
            comments = self._get_event_count('comment', post_id)
            logger.info("got comments")

            return pb2.PostStatsResponse(
                views=views,
                likes=likes,
                comments=comments
            )
        except Exception as e:
            logger.error(f"Error getting post stats for {post_id}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {e}")
            return pb2.PostStatsResponse()

    def GetViewDynamics(self, request, context):
        return self._get_dynamics(request, 'view', context)

    def GetLikeDynamics(self, request, context):
        return self._get_dynamics(request, 'like', context)

    def GetCommentDynamics(self, request, context):
        return self._get_dynamics(request, 'comment', context)

    def _get_dynamics(self, request, event_type, context):
        post_id = request.post_id
        try:
            query = """
                SELECT toDate(timestamp) as day, COUNT(*) as count
                FROM events
                WHERE event_type = %(event_type)s AND post_id = %(post_id)s
                GROUP BY day
                ORDER BY day
            """
            rows = self.clickhouse.execute(query, {
                'event_type': event_type,
                'post_id': post_id
            })

            day_counts = []
            for day, count in rows:
                day_counts.append(pb2.DayCount(
                    date=day.strftime("%Y-%m-%d"),
                    count=count
                ))

            return pb2.DynamicsResponse(data=day_counts)
        except Exception as e:
            logger.error(f"Error getting {event_type} dynamics for post {post_id}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {e}")
            return pb2.DynamicsResponse()

    def GetTopPosts(self, request, context):
        metric = self._get_metric_name(request.metric)
        if not metric:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid metric type")
            return pb2.TopPostsResponse()

        try:
            query = """
                SELECT post_id, COUNT(*) as count
                FROM events
                WHERE event_type = %(metric)s
                GROUP BY post_id
                ORDER BY count DESC
                LIMIT 10
            """
            rows = self.clickhouse.execute(query, {'metric': metric})

            top_posts = []
            for post_id, count in rows:
                top_posts.append(pb2.TopPost(post_id=post_id, count=count))

            return pb2.TopPostsResponse(top_posts=top_posts)
        except Exception as e:
            logger.error(f"Error getting top posts for metric {metric}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {e}")
            return pb2.TopPostsResponse()

    def GetTopUsers(self, request, context):
        metric = self._get_metric_name(request.metric)
        if not metric:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid metric type")
            return pb2.TopUsersResponse()

        try:
            query = """
                SELECT client_id, COUNT(*) as count
                FROM events
                WHERE event_type = %(metric)s
                GROUP BY client_id
                ORDER BY count DESC
                LIMIT 10
            """
            rows = self.clickhouse.execute(query, {'metric': metric})

            top_users = []
            for user_id, count in rows:
                top_users.append(pb2.TopUser(user_id=user_id, count=count))

            return pb2.TopUsersResponse(top_users=top_users)
        except Exception as e:
            logger.error(f"Error getting top users for metric {metric}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {e}")
            return pb2.TopUsersResponse()

    def _get_event_count(self, event_type, post_id):
        query = """
            SELECT COUNT(*)
            FROM events
            WHERE event_type = %(event_type)s AND post_id = %(post_id)s
        """
        result = self.clickhouse.execute(query, {
            'event_type': event_type,
            'post_id': post_id
        })
        return result[0][0] if result else 0

    def _get_metric_name(self, metric_enum):
        metric_map = {
            pb2.TopRequest.MetricType.LIKE: 'like',
            pb2.TopRequest.MetricType.VIEW: 'view',
            pb2.TopRequest.MetricType.COMMENT: 'comment'
        }
        return metric_map.get(metric_enum)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_StatisticsServiceServicer_to_server(StatisticsServicer(), server)
    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    server.start()
    logger.info(f"gRPC server started on port {GRPC_PORT}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    if wait_for_clickhouse():
        start_kafka_consumers()
        serve()
    else:
        logger.error("Cannot start service without ClickHouse connection")
