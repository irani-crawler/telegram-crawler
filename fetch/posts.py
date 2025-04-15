import re
from telethon.tl.types import MessageReactions
from utils.file_manager import save_post

def parse_reactions(reactions):
    if not reactions or not isinstance(reactions, MessageReactions):
        return []
    return [
        {
            'emoji': r.reaction.emoticon if hasattr(r.reaction, 'emoticon') else str(r.reaction),
            'count': r.count
        }
        for r in reactions.results
    ]

async def get_filtered_posts(client, channel, keywords, start_date, end_date):
    """
    Search for posts using server-side search for each keyword.
    If a post is newer than end_date, it's skipped.
    If a post is older than start_date, the iteration for that keyword is stopped.
    Posts matching the criteria are saved and returned.
    """
    posts_dict = {}  # To avoid duplicates
    total_checked = 0

    for keyword in keywords:
        print(f"🔍 Searching for keyword: '{keyword}'")
        async for msg in client.iter_messages(channel, search=keyword):
            total_checked += 1

            if not msg.date:
                continue

            # Convert message datetime to date for safe comparison
            msg_date = msg.date.date()

            if msg_date > end_date:
                # Message is too new, skip it.
                continue

            if msg_date < start_date:
                # Reached messages that are too old—stop the search for this keyword.
                print(f"   🛑 Message {msg.id} on {msg_date} is older than the start date. Stop searching '{keyword}'.")
                break

            # Check for keyword in message text (double-check)
            if msg.message:
                if msg.id in posts_dict:
                    continue  # Avoid duplicates if another keyword already caught this post

                post = {
                    'post_id': msg.id,
                    'date': msg.date.isoformat(),
                    'author': msg.from_id.user_id if msg.from_id else 'unknown',
                    'text': msg.message,
                    'reactions': parse_reactions(msg.reactions)
                }
                posts_dict[msg.id] = post
                save_post(post)
                print(f"✅ Matched post {msg.id} on {msg_date} for keyword: '{keyword}'")

    print(f"🏁 Completed searches. Total messages checked: {total_checked}, total matched posts: {len(posts_dict)}")
    return list(posts_dict.values())
