from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    thumbnail_url = Column(String(500), nullable=True)
    slug = Column(String(250), unique=True, nullable=False)
    excerpt = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<Blog {self.title}>"

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blog_id = Column(Integer, ForeignKey("blogs.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_approved = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="comments")
    blog = relationship("Blog", back_populates="comments")
    replies = relationship("Comment", backref=relationship("parent", remote_side=[id]))
    
    def __repr__(self):
        return f"<Comment {self.id} by {self.author.username}>"