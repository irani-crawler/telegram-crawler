import logging
from telethon.errors import FloodWaitError
from asyncio import sleep
import jdatetime
from salnama import taghvim
from datetime import datetime

from db.models import Post, Reaction
from utils.db_helpers import commit_ignore_duplicates
from utils.ch_logger import log_fetch_event

logger = logging.getLogger(__name__)

# Initialize Jalali calendar for holiday checks
jalali_calendar = taghvim.Jalali()

def parse_reactions(reactions):
    """
    Parse reaction objects into a list of emoji/count dicts.
    """
    if not reactions or not hasattr(reactions, 'results'):
        return []
    return [
        {
            'emoji': r.reaction.emoticon if hasattr(r.reaction, 'emoticon') else str(r.reaction),
            'count': r.count
        }
        for r in reactions.results
    ]

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

async def get_filtered_posts(client, session, channel, keywords, start_date, end_date, shutdown_flag):
    """
    Fetch messages matching keywords in a date range.
    Save each matching post to the database and log events.
    Returns a list of saved post URLs.
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

                post_date = msg.date.date()
                if post_date > end_date:
                    continue
                if post_date < start_date:
                    break

                # Build URLs and dates
                channel_url = f"https://t.me/{channel}"
                post_url = f"https://t.me/{channel}/{msg.id}"
                jalali_message_date = jdatetime.date.fromgregorian(date=msg.date)
                jalali_fetch_time = jdatetime.date.fromgregorian(date=datetime.now())

                # Determine if post date is a holiday in Iran
                is_holiday = check_holiday_in_iran(msg.date)

                # Forward properties
                is_forwarded = msg.fwd_from is not None
                forwarded_from = msg.fwd_from.from_name if is_forwarded else None

                # Reactions
                reactions_list = parse_reactions(msg.reactions)
                print(f"Reactions: {reactions_list}")
                reactions_count = sum(item['count'] for item in reactions_list)

                # Media info
                message_type = get_media_type(msg)
                media_url = None
                if msg.media and hasattr(msg.media, 'document') and hasattr(msg.media.document, 'attributes'):
                    try:
                        media_url = msg.media.document.attributes[0].url
                    except Exception:
                        media_url = None

                # Save reactions to the Reaction table
                for reaction in reactions_list:
                    reaction_entry = Reaction(
                        post_url=post_url,
                        emoji=reaction['emoji'],
                        count=reaction['count']
                    )
                    try:
                        commit_ignore_duplicates(session, reaction_entry)
                        log_fetch_event("REACTION_SAVED", channel, f"post_url={post_url}, emoji={reaction['emoji']}")
                    except Exception as e:
                        log_fetch_event("REACTION_SAVE_ERROR", channel, f"post_url={post_url}, emoji={reaction['emoji']}, error={e}")
                        logger.error(f"Failed to save reaction {reaction['emoji']} for post {post_url}: {e}", exc_info=True)
                        print(e)

                # Remove reactions from the Post object
                post = Post(
                    channel_url=channel_url,
                    post_url=post_url,
                    message_date_gregorian=msg.date,
                    message_date_jalali=str(jalali_message_date),
                    fetch_time_gregorian=datetime.now(),
                    fetch_time_jalali=str(jalali_fetch_time),
                    author=getattr(msg.from_id, 'user_id', 'unknown'),
                    text=msg.message,
                    views=msg.views,
                    is_holiday=is_holiday,
                    is_forwarded=is_forwarded,
                    forwarded_from=forwarded_from,
                    total_reactions=reactions_count,
                    message_type=message_type,
                    media_url=media_url
                )
                try:
                    commit_ignore_duplicates(session, post)
                    matched.append(post_url)
                    log_fetch_event("POST_SAVED", channel, f"post_url={post_url}")
                    logger.info(f"Saved post {post_url}")
                except Exception as e:
                    log_fetch_event("POST_SAVE_ERROR", channel, f"post_url={post_url}, error={e}")
                    logger.error(f"Failed to save post {post_url}: {e}", exc_info=True)

                await sleep(0.5)

        except FloodWaitError as e:
            logger.warning(f"FloodWait fetching posts in {channel}: sleeping {e.seconds}s")
            await sleep(e.seconds + 1)
        except Exception as ex:
            log_fetch_event("POST_FETCH_ERROR", channel, f"keyword={keyword}, error={ex}")
            logger.error(f"Error fetching posts for '{keyword}' in {channel}: {ex}", exc_info=True)

    return matched
