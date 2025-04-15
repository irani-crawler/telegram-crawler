from telethon.tl.functions.messages import GetRepliesRequest
from utils.file_manager import save_comments
from fetch.posts import parse_reactions

async def get_comments(client, channel, post_id, limit=20):
    try:
        replies = await client(GetRepliesRequest(
            peer=channel,
            msg_id=post_id,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        comments = []
        for msg in replies.messages:
            comments.append({
                'message_id': msg.id,
                'date': msg.date.isoformat(),
                'author': msg.from_id.user_id if msg.from_id else 'unknown',
                'text': msg.message,
                'reactions': parse_reactions(msg.reactions)
            })

        save_comments(post_id, comments)
        return comments

    except Exception as e:
        print(f"[ERROR] Could not fetch comments for post {post_id}: {e}")
        return []
