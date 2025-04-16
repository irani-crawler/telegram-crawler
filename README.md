# Telegram Crawler

A resilient and modular Telegram crawler that retrieves channel posts, reactions, and threaded comments based on keyword and date-range filters. This crawler is designed to handle rate limits, save progress, and resume from the last processed state after interruptions.

---

## Features

- **Keyword-Based Search:** Searches public channels for posts matching given keywords.
- **Date Filtering:** Filters posts within a specified Jalali (Shamsi) date range (converted to Gregorian).
- **Comment Fetching:** Retrieves threaded comments (when a discussion group is linked).
- **Reactions Extraction:** Extracts emojis and counts from post reactions.
- **State Persistence:** Saves progress (last processed message) to resume crawling after interruptions.
- **Rate-Limit Handling:** Gracefully manages Telegram's `FloodWaitError`.
- **Structured Storage:** Organizes posts and comments in separate JSON files.
- **Modular Codebase:** Clean and easily extensible design for further development.

---

## Project Structure

```
telegram-crawler/
├── main.py                   # Main entry point with CLI support
├── config.py                 # API credentials and default channel configuration
├── channels.json             # JSON file with list of channel URLs
├── keywords.json             # JSON file with list of keywords to filter posts
├── fetch/
│   ├── posts.py              # Module for crawling posts and filtering them by keywords/date
│   └── comments.py           # Module for fetching threaded comments on posts
├── utils/
│   ├── file_manager.py       # Functions for saving/loading JSON data and crawler state
│   └── date_converter.py     # Utility to convert Jalali dates to Gregorian
├── db/
│   ├── db.py                 # Database connection & initialization (if using DB output)
│   └── models.py             # SQLAlchemy models (posts and comments)
├── data/
│   ├── posts/                # Directory for saved post JSON files (one per post)
│   └── comments/             # Directory for saved comment JSON files (one per post)
├── session/                  # Directory for Telethon session files (auto-generated)
└── state.json                # File that stores the crawler's progress state
```

---

## Setup Instructions

1. **Clone the Repository**

    ```bash
    git clone https://github.com/parvvaresh/telegram-crawler.git
    cd telegram-crawler
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    If the `requirements.txt` file is missing, install:
    
    ```bash
    pip install telethon jdatetime sqlalchemy mysql-connector-python
    ```

3. **Configure API Credentials**

    Edit `config.py` with your Telegram API credentials:

    ```python
    api_id = 123456              # Your API ID from my.telegram.org
    api_hash = 'your_api_hash'   # Your API hash
    ```

4. **Prepare Input Files**

    - **channels.json:** Contains a JSON object with a `"channels"` array of public channel URLs.
      
      Example:
      ```json
      {
        "channels": [
          "https://t.me/example_channel1",
          "https://t.me/example_channel2"
        ]
      }
      ```

    - **keywords.json:** Contains a JSON object with a `"keywords"` array of keywords to search for.
      
      Example:
      ```json
      {
        "keywords": [
          "keyword1",
          "keyword2",
          "keyword3"
        ]
      }
      ```

5. **Initialize the Database (Optional)**

    If you want to save data to a MySQL database, update the database configuration in `db/db.py` and run:

    ```python
    from db.db import init_db
    init_db()
    ```

---

## Usage

Run the crawler from the command line with your desired parameters. For example:

```bash
python main.py --start 1402-01-01 --end 1402-12-29 --channels channels.json --keywords keywords.json --limit 10
```

This command will:

- Convert the Jalali dates to Gregorian.
- Load channels and keywords from the provided JSON files.
- Search and filter messages by the specified keywords and date range.
- Save post data (with reactions) to `data/posts/` and comments to `data/comments/`.
- Handle graceful shutdown on `CTRL+C`.

---

## Output Formats

### Post (data/posts/{post_id}.json)

```json
{
  "post_id": 123456,
  "date": "2025-04-01T12:34:56",
  "author": 987654321,
  "text": "Example post content...",
  "reactions": [
    { "emoji": "🔥", "count": 15 },
    { "emoji": "❤️", "count": 10 }
  ]
}
```

### Comments (data/comments/{post_id}.json)

```json
[
  {
    "message_id": 78910,
    "from": 456789123,
    "date": "2025-04-01T13:00:00",
    "text": "This is a reply comment.",
    "reactions": []
  },
  ...
]
```

---

## Graceful Shutdown

- Press `CTRL+C` while the script is running.
- The crawler will finish the current operation and then exit.
- Progress is saved in `state.json` for resuming later.

---

## License

This project is licensed under the MIT License. Feel free to use, modify, or contribute to the project.

---

## Contributing

Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request for major changes.

```