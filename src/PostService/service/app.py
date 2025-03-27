import logging
import time
import grpc
from concurrent import futures
from db.db import engine, Base
from proto import post_pb2, post_pb2_grpc
from service.post_service import PostService
from db.db import SessionLocal
from service.config import GRPC_HOST, GRPC_PORT
from sqlalchemy.exc import SQLAlchemyError

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('grpc').setLevel(logging.DEBUG)

logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


class PostServicer(post_pb2_grpc.PostServiceServicer):
    def CreatePost(self, request, context):
        db = SessionLocal()
        try:
            service = PostService(db)
            post = service.create_post(
                title=request.title,
                description=request.description,
                username=request.username,
                is_private=request.is_private,
                tags=list(request.tags)
            )
            
            return post_pb2.PostResponse(
                post=post_pb2.Post(
                    id=post.id,
                    title=post.title,
                    description=post.description,
                    username=post.username,
                    created_at=post.created_at.isoformat(),
                    updated_at=post.updated_at.isoformat(),
                    is_private=post.is_private,
                    tags=[tag.name for tag in post.tags]
                )
            )
        except SQLAlchemyError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return post_pb2.PostResponse()
        finally:
            db.close()
    
    def GetPost(self, request, context):
        db = SessionLocal()
        try:
            service = PostService(db)
            post = service.get_post(post_id=request.post_id, username=request.username)
            
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found or access denied")
                return post_pb2.PostResponse()
            
            return post_pb2.PostResponse(
                post=post_pb2.Post(
                    id=post.id,
                    title=post.title,
                    description=post.description,
                    username=post.username,
                    created_at=post.created_at.isoformat(),
                    updated_at=post.updated_at.isoformat(),
                    is_private=post.is_private,
                    tags=[tag.name for tag in post.tags]
                )
            )
        except SQLAlchemyError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return post_pb2.PostResponse()
        finally:
            db.close()
    
    def UpdatePost(self, request, context):
        db = SessionLocal()
        try:
            service = PostService(db)
            post = service.update_post(
                post_id=request.post_id,
                username=request.username,
                title=request.title if request.title else None,
                description=request.description if request.description else None,
                is_private=request.is_private,
                tags=list(request.tags) if request.tags else None
            )
            
            if not post:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found or permission denied")
                return post_pb2.PostResponse()
            
            return post_pb2.PostResponse(
                post=post_pb2.Post(
                    id=post.id,
                    title=post.title,
                    description=post.description,
                    username=post.username,
                    created_at=post.created_at.isoformat(),
                    updated_at=post.updated_at.isoformat(),
                    is_private=post.is_private,
                    tags=[tag.name for tag in post.tags]
                )
            )
        except SQLAlchemyError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return post_pb2.PostResponse()
        finally:
            db.close()
    
    def DeletePost(self, request, context):
        db = SessionLocal()
        try:
            service = PostService(db)
            success, message = service.delete_post(post_id=request.post_id, username=request.username)
            
            if not success:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED if "permission" in message.lower() else grpc.StatusCode.NOT_FOUND)
                context.set_details(message)
            
            return post_pb2.DeletePostResponse(success=success, message=message)
        except SQLAlchemyError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return post_pb2.DeletePostResponse(success=False, message=str(e))
        finally:
            db.close()
    
    def ListPosts(self, request, context):
        db = SessionLocal()
        try:
            service = PostService(db)
            result = service.list_posts(
                page=max(1, request.page),
                page_size=min(100, max(1, request.page_size)),
                username=request.username if request.username else None,
                tag=request.tag if request.tag else None
            )
            
            posts_proto = []
            for post in result["posts"]:
                posts_proto.append(post_pb2.Post(
                    id=post.id,
                    title=post.title,
                    description=post.description,
                    username=post.username,
                    created_at=post.created_at.isoformat(),
                    updated_at=post.updated_at.isoformat(),
                    is_private=post.is_private,
                    tags=[tag.name for tag in post.tags]
                ))
            
            return post_pb2.ListPostsResponse(
                posts=posts_proto,
                total=result["total"],
                page=result["page"],
                page_size=result["page_size"],
                pages=result["pages"]
            )
        except SQLAlchemyError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {str(e)}")
            return post_pb2.ListPostsResponse()
        finally:
            db.close()

def create_tables():
    logging.info("Creating database tables if they don't exist...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created.")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostServiceServicer_to_server(PostServicer(), server)
    server.add_insecure_port(f'{GRPC_HOST}:{GRPC_PORT}')
    server.start()
    logging.info(f"gRPC server started at {GRPC_HOST}:{GRPC_PORT}")
    
    try:
        while True:
            time.sleep(69420)
    except KeyboardInterrupt:
        server.stop(0)

def main():
    time.sleep(15)
    logging.info("Starting Post Service...")
    create_tables()
    serve()

if __name__ == "__main__":
    main()
