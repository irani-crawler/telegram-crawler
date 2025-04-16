import asyncio
import signal
import json
import argparse
from datetime import datetime
from telethon import TelegramClient
from config import api_id, api_hash
from utils.date_converter import jalali_to_gregorian
from fetch.posts import get_filtered_posts
from fetch.comments import get_comments
from db.db import SessionLocal, init_db

shutdown_flag = False

def ask_exit(signame):
    global shutdown_flag
    print(f"\n[INFO] {signame} received. Shutting down gracefully...")
    shutdown_flag = True

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_jalali(date_str):
    try:
        y, m, d = map(int, date_str.split("-"))
        return (y, m, d)
    except Exception:
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY-MM-DD (e.g., 1402-01-01)")

async def run(start_jalali, end_jalali, channels_file, keywords_file, comment_limit=10):
    global shutdown_flag

    start_date = jalali_to_gregorian(*start_jalali).date()
    end_date = jalali_to_gregorian(*end_jalali).date()
    print(f"[🗓] Filtering posts between {start_date} and {end_date}")

    channels = load_json(channels_file).get("channels", [])
    keywords = load_json(keywords_file).get("keywords", [])

    print(f"[📂] Channels to crawl: {channels}")
    print(f"[🔍] Keywords to search: {keywords}")

    init_db()
    session = SessionLocal()

    async with TelegramClient('session/session', api_id, api_hash) as client:
        loop = asyncio.get_running_loop()
        for sig in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, sig), lambda s=sig: ask_exit(s))

        for channel in channels:
            if shutdown_flag:
                print("[⏹] Shutdown requested. Stopping channel crawl.")
                break

            print(f"\n[🚀] Crawling channel: {channel}")
            try:
                posts = await get_filtered_posts(
                    client, session, channel, keywords, start_date, end_date, shutdown_flag
                )

                for post in posts:
                    if shutdown_flag:
                        print("[⏹] Shutdown requested. Stopping post comments.")
                        break
                    await get_comments(client, session, channel, post.post_id, limit=comment_limit)

            except Exception as e:
                print(f"[⚠️] Error processing {channel}: {e}")

        print("\n[✅] Crawling completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Channel Crawler")
    parser.add_argument('--start', type=parse_jalali, required=True, help='Start date in Jalali format (e.g., 1402-01-01)')
    parser.add_argument('--end', type=parse_jalali, required=True, help='End date in Jalali format (e.g., 1402-12-29)')
    parser.add_argument('--channels', type=str, default='channels.json', help='Path to channels JSON file')
    parser.add_argument('--keywords', type=str, default='keywords.json', help='Path to keywords JSON file')
    parser.add_argument('--limit', type=int, default=10, help='Number of comments per post')

    args = parser.parse_args()

    asyncio.run(run(args.start, args.end, args.channels, args.keywords, args.limit))
