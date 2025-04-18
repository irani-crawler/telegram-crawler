import argparse
import asyncio
import signal
import json

from telethon import TelegramClient

from config import api_id, api_hash
from utils.date_converter import jalali_to_gregorian
from utils.ch_logger import log_fetch_event
from fetch.posts import get_filtered_posts
from fetch.comments import get_comments
from db.db import SessionLocal, init_db

shutdown_flag = False

def ask_exit(signame):
    global shutdown_flag
    log_fetch_event("SHUTDOWN_SIGNAL", "", f"signal={signame}")
    shutdown_flag = True

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_jalali(s):
    y, m, d = map(int, s.split('-'))
    return (y, m, d)

async def run(start_jalali, end_jalali, channels_file, keywords_file, comment_limit):
    global shutdown_flag

    start_date = jalali_to_gregorian(*start_jalali)
    end_date   = jalali_to_gregorian(*end_jalali)
    log_fetch_event("DATE_RANGE", "", f"{start_date} to {end_date}")

    channels = load_json(channels_file).get("channels", [])
    keywords = load_json(keywords_file).get("keywords", [])
    log_fetch_event("CONFIG_LOADED", "", f"channels={len(channels)}, keywords={len(keywords)}")

    init_db()
    session = SessionLocal()

    async with TelegramClient('session/session', api_id, api_hash) as client:
        loop = asyncio.get_running_loop()
        for sig in ('SIGINT','SIGTERM'):
            loop.add_signal_handler(getattr(signal, sig), lambda s=sig: ask_exit(s))

        for channel in channels:
            if shutdown_flag:
                break

            log_fetch_event("CRAWL_START", channel, "")
            posts = await get_filtered_posts(client, session, channel, keywords, start_date, end_date, shutdown_flag)
            log_fetch_event("FETCH_POSTS", channel, f"count={len(posts)}")

            for post_id in posts:
                if shutdown_flag:
                    break
                await get_comments(client, session, channel, post_id, limit=comment_limit)

        log_fetch_event("CRAWL_COMPLETE", "", "")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Crawler with ClickHouse logs")
    parser.add_argument('--start',    type=parse_jalali, required=True, help='Start Jalali YYYY-MM-DD')
    parser.add_argument('--end',      type=parse_jalali, required=True, help='End Jalali YYYY-MM-DD')
    parser.add_argument('--channels', type=str,            default='channels.json')
    parser.add_argument('--keywords', type=str,            default='keywords.json')
    parser.add_argument('--limit',    type=int,            default=10)

    args = parser.parse_args()
    asyncio.run(run(args.start, args.end, args.channels, args.keywords, args.limit))
