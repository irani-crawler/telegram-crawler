from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    channel_url             = Column(String(255), nullable=False)
    post_url                = Column(String(255), unique=True, nullable=False)
    message_date_gregorian  = Column(DateTime)
    message_date_jalali     = Column(String(255))
    fetch_time_gregorian    = Column(DateTime)
    fetch_time_jalali       = Column(String(255))
    author                  = Column(String(255))
    text                    = Column(Text)
    views                   = Column(Integer)
    is_holiday              = Column(Boolean, default=False)
    is_forwarded            = Column(Boolean)
    forwarded_from          = Column(String(255))
    total_reactions         = Column(Integer)
    message_type            = Column(String(50))
    media_url               = Column(String(255))

    # Relationships
    comments                = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    reactions               = relationship("Reaction", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id                     = Column(Integer, primary_key=True, autoincrement=True)
    post_url               = Column(String(255), ForeignKey("posts.post_url", ondelete="CASCADE"), nullable=False)
    comment_url            = Column(String(255), unique=True, nullable=False)
    from_user              = Column(String(255))
    date_gregorian         = Column(DateTime)
    date_jalali            = Column(String(255))
    fetch_time_gregorian   = Column(DateTime)
    fetch_time_jalali      = Column(String(255))
    text                   = Column(Text)
    reactions_count        = Column(Integer)
    reply_to_message_id    = Column(Integer)
    message_type           = Column(String(50))
    is_holiday             = Column(Boolean, default=False)

    post                   = relationship("Post", back_populates="comments")


class Reaction(Base):
    __tablename__ = 'reactions'

    id = Column(Integer, primary_key=True, index=True)
    post_url = Column(String(255), ForeignKey("posts.post_url", ondelete="CASCADE"), nullable=False)
    emoji = Column(String)
    count = Column(Integer)

    post       = relationship("Post", back_populates="reactions")
