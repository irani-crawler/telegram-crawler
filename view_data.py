from db.db import SessionLocal, init_db
from db.models import Post, Comment

# Initialize the database (creates tables if they don't exist)
init_db()

# Create a database session
session = SessionLocal()

print("=== Posts ===")
posts = session.query(Post).all()
for post in posts:
    print(f"Post ID: {post.post_id}")
    print(f"Date: {post.date}")
    print(f"Author: {post.author}")
    print(f"Text: {post.text}")
    print(f"Reactions: {post.reactions}")
    print(f"channel: {post.channel}")

    print("-----")

print("\n=== Comments ===")
comments = session.query(Comment).all()
for comment in comments:
    print(f"Comment Message ID: {comment.message_id}")
    print(f"For Post ID: {comment.post_id}")
    print(f"From User: {comment.from_user}")
    print(f"Date: {comment.date}")
    print(f"Text: {comment.text}")
    print(f"Reactions: {comment.reactions}")
    print("-----")

# Close the session
session.close()
