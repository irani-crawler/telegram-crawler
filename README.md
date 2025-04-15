# 📡 Telegram Crawler

A modular, reliable, and resumable Telegram crawler for fetching channel posts, reactions, and threaded comments based on keyword and date range filters.

---

## 🚀 Features

- 🔍 Search by keyword in a public channel
- 📅 Filter posts by Jalali (Shamsi) date range
- 💬 Fetch comments on posts (if discussion group is linked)
- ❤️ Extract reactions (emoji counts)
- 🧠 Saves progress and resumes after crash or stop
- 🗃️ Structured file saving (JSON format)
- 🧯 Handles Telegram rate limits (`FloodWaitError`)
- 🧼 Clean, modular codebase for maintenance and extension

---

## 🧱 Project Structure

```
telegram-crawler/
├── main.py                   # Entry point
├── config.py                 # Your API credentials + target channel
├── fetch/
│   ├── posts.py              # Crawls posts with filtering
│   └── comments.py           # Fetches replies to a post
├── utils/
│   ├── file_manager.py       # Save/load JSON files & crawler state
│   └── date_converter.py     # Convert Jalali to Gregorian
├── data/
│   ├── posts/                # Saved posts in JSON (post_id.json)
│   └── comments/             # Saved comments (post_id.json)
├── session/                  # Telethon session files (auto-generated)
├── state.json                # Stores last post ID crawled per channel
└── README.md                 # Documentation
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/parvvaresh/telegram-crawler.git
cd telegram-crawler
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is missing, run:
```bash
pip install telethon jdatetime
```

---

## 🔐 Configuration

### `config.py`

Edit this file with your Telegram API credentials and target channel:

```python
api_id = 123456               # From my.telegram.org
api_hash = 'your_api_hash'
channel = 'https://t.me/target_channel'
```

---

## 🚦 Usage

Run the crawler:

```bash
python main.py
```

This will:

1. Convert Jalali dates to Gregorian.
2. Search messages by keywords.
3. Filter by date range.
4. Save post info + reactions to `data/posts/`.
5. Save replies/comments to `data/comments/`.

---

## ✋ Graceful Stop

To safely stop the crawler:

- Press `CTRL+C`
- It will finish the current operation and exit.
- It resumes later from the last saved message.

---

## 💾 Output Format

### Post JSON (data/posts/{post_id}.json)

```json
{
  "post_id": 123456,
  "date": "2025-04-01T12:34:56",
  "author": 987654321,
  "text": "Example content",
  "reactions": [
    {"emoji": "🔥", "count": 15},
    {"emoji": "❤️", "count": 10}
  ]
}
```

### Comments JSON (data/comments/{post_id}.json)

```json
[
  {
    "message_id": 78910,
    "from": 456789123,
    "date": "2025-04-01T13:00:00",
    "text": "This is a reply",
    "reactions": []
  },
  ...
]
```

---

## 📌 Notes

- ✅ This only works with **public channels** (or ones you have access to).
- ❌ Cannot fetch data anonymously (API credentials are required).
- ⚠️ Avoid excessive crawling to prevent rate-limiting (`FloodWaitError`).

---

## 📜 License

MIT — feel free to use, modify, or contribute.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to change.

