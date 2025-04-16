from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False)
    channel = Column(String, nullable=False)
    date = Column(DateTime)
    author = Column(String)
    text = Column(Text)
    reactions = Column(JSON)

    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"))
    message_id = Column(Integer)
    from_user = Column(String)
    date = Column(DateTime)
    text = Column(Text)
    reactions = Column(JSON)

    post = relationship("Post", back_populates="comments")
