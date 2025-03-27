from sqlalchemy.orm import Session
from db.models import Post, Tag
from sqlalchemy import or_
from datetime import datetime
from typing import List, Optional

class PostService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_post(self, title: str, description: str, username: str, is_private: bool, tags: List[str]):
        tag_objects = []
        for tag_name in tags:
            tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.db.add(tag)
            tag_objects.append(tag)
        
        post = Post(
            title=title,
            description=description,
            username=username,
            is_private=is_private
        )
        
        post.tags = tag_objects
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def get_post(self, post_id: int, username: Optional[str] = None):
        post = self.db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            return None
        
        if post.is_private and post.username != username:
            return None
            
        return post
    
    def update_post(self, post_id: int, username: str, title: Optional[str] = None, 
                    description: Optional[str] = None, is_private: Optional[bool] = None, 
                    tags: Optional[List[str]] = None):
        post = self.db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            return None
        
        if post.username != username:
            return None
        
        if title is not None:
            post.title = title
        if description is not None:
            post.description = description
        if is_private is not None:
            post.is_private = is_private
        
        if tags is not None:
            tag_objects = []
            for tag_name in tags:
                tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                tag_objects.append(tag)
            post.tags = tag_objects
        
        post.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def delete_post(self, post_id: int, username: str):
        post = self.db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            return False, "Post not found"
        
        if post.username != username:
            return False, "You don't have permission to delete this post"
        
        self.db.delete(post)
        self.db.commit()
        return True, "Post deleted successfully"
    
    def list_posts(self, page: int, page_size: int, username: Optional[str] = None, tag: Optional[str] = None):
        query = self.db.query(Post)
        
        if username:
            query = query.filter(or_(Post.is_private == False, Post.username == username))
        else:
            query = query.filter(Post.is_private == False)
        
        if tag:
            query = query.join(Post.tags).filter(Tag.name == tag)
        
        total = query.count()
        
        posts = query.order_by(Post.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "posts": posts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
