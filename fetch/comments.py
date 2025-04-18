import logging
import asyncio
from telethon.errors import FloodWaitError, MsgIdInvalidError

from db.models import Comment
from utils.db_helpers import commit_ignore_duplicates
from utils.ch_logger import log_fetch_event

logger = logging.getLogger(__name__)

async def get_comments(client, session, channel, post_id, limit=10):
    """
    Fetch replies to a post and save them into the database.

    Args:
        client: Telethon client instance.
        session: SQLAlchemy session.
        channel: Telegram channel (username or ID).
        post_id: ID of the post to fetch replies for.
        limit: Max number of replies to fetch.

    Returns:
        List of saved comment message IDs.
    """
    saved = []

    try:
        async for msg in client.iter_messages(channel, reply_to=post_id, limit=limit):
            from_user_id = getattr(msg.from_id, 'user_id', None) if msg.from_id else None

            comment = Comment(
                post_id=post_id,
                message_id=msg.id,
                from_user=from_user_id,
                date=msg.date,
                text=msg.message,
                reactions=msg.reactions.to_dict() if msg.reactions else {}
            )

            try:
                commit_ignore_duplicates(session, comment)
                saved.append(msg.id)
                log_fetch_event("COMMENTS_SAVED", channel, f"post_id={post_id}, comment_id={msg.id}")
                logger.info(f"Saved comment {msg.id} for post {post_id}")
            except Exception as e:
                log_fetch_event("COMMENTS_SAVE_ERROR", channel, f"post_id={post_id}, comment_id={msg.id}, error={e}")
                logger.error(f"Failed to save comment {msg.id}: {e}", exc_info=True)

    except FloodWaitError as e:
        logger.warning(f"FloodWait fetching comments for post {post_id}: sleeping {e.seconds}s")
        await asyncio.sleep(e.seconds + 1)

    except MsgIdInvalidError:
        log_fetch_event("COMMENTS_INVALID_ID", channel, f"Invalid message ID for post {post_id}")
        logger.warning(f"Invalid message ID used in GetRepliesRequest for post {post_id}")

    except Exception as ex:
        log_fetch_event("COMMENTS_FETCH_ERROR", channel, f"post_id={post_id}, error={ex}")
        logger.error(f"Error fetching comments for post {post_id}: {ex}", exc_info=True)

    return saved
