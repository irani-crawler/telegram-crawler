# fetch/posts.py
import logging
from telethon.errors import FloodWaitError
from asyncio import sleep

from db.models import Post
from utils.db_helpers import commit_ignore_duplicates
from utils.ch_logger import log_fetch_event

logger = logging.getLogger(__name__)

def parse_reactions(reactions):
    if not reactions or not hasattr(reactions, 'results'):
        return []
    return [
        {
            'emoji': r.reaction.emoticon if hasattr(r.reaction, 'emoticon') else str(r.reaction),
            'count': r.count
        }
        for r in reactions.results
    ]

async def get_filtered_posts(client, session, channel, keywords, start_date, end_date, shutdown_flag):
    """
    Fetch messages matching keywords in a date range.
    Save to SQL and log to ClickHouse.
    """
    matched = []
    for keyword in keywords:
        logger.info(f"Searching '{keyword}' in {channel}")
        try:
            async for msg in client.iter_messages(channel, search=keyword):
                if shutdown_flag:
                    return matched
                if not msg.date or not msg.message:
                    continue

                d = msg.date.date()
                if d > end_date:
                    continue
                if d < start_date:
                    break

                # Prepare and save Post
                post = Post(
                    post_id=msg.id,
                    channel=channel,
                    date=msg.date,
                    author=getattr(msg.from_id, 'user_id', 'unknown'),
                    text=msg.message,
                    reactions=parse_reactions(msg.reactions)
                )
                try:
                    commit_ignore_duplicates(session, post)
                    matched.append(msg.id)
                    log_fetch_event("POST_SAVED", channel, f"post_id={msg.id}")
                    logger.info(f"Saved post {msg.id}")
                except Exception as e:
                    log_fetch_event("POST_SAVE_ERROR", channel, f"post_id={msg.id}, error={e}")
                    logger.error(f"Failed to save post {msg.id}: {e}", exc_info=True)

                await sleep(0.5)

        except FloodWaitError as e:
            logger.warning(f"FloodWait fetching posts in {channel}: sleeping {e.seconds}s")
            await sleep(e.seconds + 1)
        except Exception as ex:
            log_fetch_event("POST_FETCH_ERROR", channel, f"keyword={keyword}, error={ex}")
            logger.error(f"Error fetching posts for '{keyword}' in {channel}: {ex}", exc_info=True)

    return matched
