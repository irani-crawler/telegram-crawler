import os
import json

DATA_DIR = 'data'
POST_DIR = os.path.join(DATA_DIR, 'posts')
COMMENT_DIR = os.path.join(DATA_DIR, 'comments')

os.makedirs(POST_DIR, exist_ok=True)
os.makedirs(COMMENT_DIR, exist_ok=True)

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_post(post):
    post_id = post['post_id']
    save_json(post, os.path.join(POST_DIR, f"{post_id}.json"))

def save_comments(post_id, comments):
    save_json(comments, os.path.join(COMMENT_DIR, f"{post_id}.json"))
