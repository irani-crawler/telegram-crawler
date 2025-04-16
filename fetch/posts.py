import re
from datetime import datetime
from telethon.errors import FloodWaitError
from asyncio import sleep
from db.models import Post
from utils.db_helpers import commit_ignore_duplicates

def parse_reactions(reactions):
    if not reactions or not hasattr(reactions, 'results'):
        return []
    return [
        {
            'emoji': r.reaction.emoticon if hasattr(r.reaction, 'emoticon') else str(r.reaction),
            'count': r.count
        } for r in reactions.results
    ]

async def get_filtered_posts(client, session, channel, keywords, start_date, end_date, shutdown_flag):
    total = 0

    for keyword in keywords:
        print(f"🔍 Searching in {channel}: {keyword}")
        try:
            async for msg in client.iter_messages(channel, search=keyword):
                if shutdown_flag:
                    break
                if not msg.message or not msg.date:
                    continue

                msg_date = msg.date.date()
                if msg_date > end_date:
                    continue
                if msg_date < start_date:
                    print(f"🛑 Out of range: {msg.id}")
                    break

                post = Post(
                    post_id=msg.id,
                    channel=channel,
                    date=msg.date,
                    author=getattr(msg.from_id, 'user_id', 'unknown'),
                    text=msg.message,
                    reactions=parse_reactions(msg.reactions)
                )
                commit_ignore_duplicates(session, post)
                total += 1
                print(f"✅ Saved post {msg.id}")
                await sleep(0.5)

        except FloodWaitError as e:
            print(f"⏳ Flood wait: sleeping {e.seconds} sec...")
            await sleep(e.seconds + 1)

    print(f"📦 Total collected for {channel}: {total}")
