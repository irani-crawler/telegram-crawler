import logging
import asyncio
from datetime import datetime
from telethon.errors import FloodWaitError, MsgIdInvalidError
from jdatetime import date as jdate
import jdatetime
from salnama import taghvim
from datetime import datetime
from db.models import Comment
from utils.db_helpers import commit_ignore_duplicates
from utils.ch_logger import log_fetch_event

logger = logging.getLogger(__name__)
# Initialize Jalali calendar for holiday checks
jalali_calendar = taghvim.Jalali()

def check_holiday_in_iran(gregorian_date):
    """
    Convert a Gregorian date to Jalali and check if it is a holiday using salnama.
    Returns True if holiday, False otherwise.
    """
    # Convert to Jalali datetime
    jdt = jdatetime.datetime.fromgregorian(date=gregorian_date)
    # Format as YYYY-M-D (remove leading zeros)
    shdate = jdt.strftime("%Y-%m-%d").replace("-0", "-")
    # Check holiday status
    return jalali_calendar.holiday(shdate) == 'تعطیل'


def get_media_type(msg):
    """
    Determine the type of media in the message.
    """
    if msg.photo and msg.message:
        return "photo + text"
    elif msg.photo:
        return "photo"
    elif msg.video and msg.message:
        return "video + text"
    elif msg.video:
        return "video"
    elif msg.document:
        return "document"
    elif msg.sticker:
        return "sticker"
    else:
        return "text"

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
        if isinstance(post_id, str) and post_id.startswith("https://t.me/"):
            try:
                post_id = int(post_id.split("/")[-1])
            except ValueError:
                raise ValueError(f"Invalid post_id: {post_id}. Unable to extract integer ID.")

        if not isinstance(post_id, int):
            raise ValueError(f"Invalid post_id: {post_id}. It must be an integer.")

        async for msg in client.iter_messages(channel, reply_to=post_id, limit=limit):
            from_user_id = getattr(msg.from_id, 'user_id', None) if msg.from_id else None
            reply_to_message_id = msg.reply_to_msg_id if msg.reply_to_msg_id else None
            post_url = f"https://t.me/{channel}/{post_id}"  #  post channel URL
            jalali_date = jdate.fromgregorian(date=msg.date)
            jalali_fetch_time = jdate.fromgregorian(date=datetime.now())
            is_holiday = check_holiday_in_iran(msg.date)
            message_type = get_media_type(msg)

            # Ensure message_id is an integer
            if not isinstance(msg.id, int):
                raise ValueError(f"Invalid message_id: {msg.id}. It must be an integer.")

            # Safely parse reactions
            try:
                reactions_count = sum(r['count'] for r in msg.reactions.to_dict().values() if isinstance(r, dict) and 'count' in r) if msg.reactions else 0
            except Exception as e:
                logger.error(f"Error parsing reactions for message {msg.id}: {e}", exc_info=True)
                reactions_count = 0

            # Construct comment URL
            comment_url = f"https://t.me/{channel}/{post_id}?comment={msg.id}"

            comment = Comment(
                post_url=post_url,
                comment_url=comment_url,
                from_user=from_user_id,
                date_gregorian=msg.date,
                date_jalali=str(jalali_date),
                fetch_time_gregorian=datetime.now(),
                fetch_time_jalali=str(jalali_fetch_time),
                text=msg.message,
                reactions_count=reactions_count,
                reply_to_message_id=reply_to_message_id,
                message_type=message_type,
                is_holiday=is_holiday
            )

            # Debugging: Log the comment object to ensure it is being created correctly
            logger.debug(f"Comment object: {comment}")

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
