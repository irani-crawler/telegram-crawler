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
- **Database Integration:** Stores posts and comments in a MySQL database.
- **ClickHouse Logging:** Logs events and errors to a ClickHouse database for monitoring.
- **View Data:** Includes a script to view stored posts and comments.
- **Modular Codebase:** Clean and easily extensible design for further development.

---

## Project Structure

```
telegram-crawler/
├── main.py                   # Main entry point with CLI support
├── config.py                 # API credentials and default channel configuration
├── view_data.py              # Script to view stored posts and comments
├── requirements.txt          # Python dependencies
├── input/
│   ├── channels.json         # JSON file with list of channel URLs
│   └── keywords.json         # JSON file with list of keywords to filter posts
├── fetch/
│   ├── posts.py              # Module for crawling posts and filtering them by keywords/date
│   └── comments.py           # Module for fetching threaded comments on posts
├── utils/
│   ├── ch_logger.py          # ClickHouse logging utility
│   ├── date_converter.py     # Utility to convert Jalali dates to Gregorian
│   └── db_helpers.py         # Helper functions for database operations
├── db/
│   ├── db.py                 # Database connection & initialization
│   └── models.py             # SQLAlchemy models (posts and comments)
├── session/                  # Directory for Telethon session files (auto-generated)
└── README.md                 # Project documentation
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
              "https://t.me/mypersia24",
              "https://t.me/SaberinFa",
              "https://t.me/isna94",
              "https://t.me/bbcpersian",
              "https://t.me/khabarevijh",
              "https://t.me/ageofreform",
              "https://t.me/thezoomit"
          ]
        }
  
      ```

    - **keywords.json:** Contains a JSON object with a `"keywords"` array of keywords to search for.
      
      Example:
      ```json
        {
            "keywords": [
                "تست"
            ]
        }
          
      ```

5. **Initialize the Database**

    Update the database configuration in `db/db.py` and run:

    ```python
    from db.db import init_db
    init_db()
    ```

6. **View Stored Data**

    Use `view_data.py` to view stored posts and comments:

    ```bash
    python view_data.py
    ```

---

## Database Configuration

### MySQL Setup

1. Install MySQL on your system if not already installed.

    ```bash
    sudo apt update
    sudo apt install mysql-server
    ```

2. Log in to the MySQL server and create a database for the crawler:

    ```bash
    mysql -u root -p
    CREATE DATABASE telegram_db;
    CREATE USER 'reza'@'localhost' IDENTIFIED BY '1234';
    GRANT ALL PRIVILEGES ON telegram_db.* TO 'reza'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
    ```

3. Update the `DB_URL` in `db/db.py` to match your MySQL configuration:

    ```python
    DB_URL = "mysql+pymysql://reza:1234@localhost/telegram_db"
    ```

### ClickHouse Setup

1. Install ClickHouse on your system if not already installed:

    ```bash
    sudo apt update
    sudo apt install clickhouse-server clickhouse-client
    ```

2. Start the ClickHouse server:

    ```bash
    sudo service clickhouse-server start
    ```

3. Log in to the ClickHouse client and create a database for logging:

    ```bash
    clickhouse-client
    CREATE DATABASE crawler_logs_db;
    USE crawler_logs_db;
    CREATE TABLE telegram_fetch_logs (
        timestamp DateTime,
        event String,
        channel String,
        details String
    ) ENGINE = MergeTree()
    ORDER BY timestamp;
    EXIT;
    ```

4. Update the ClickHouse configuration in `utils/ch_logger.py`:

    ```python
    CH_HOST = "localhost"
    CH_PORT = 9000
    CH_DATABASE = "crawler_logs_db"
    CH_USER = "default"
    CH_PASSWORD = ""
    ```

---

## Usage

Run the crawler from the command line with your desired parameters. For example:

```bash
python main.py --start 1402-01-01 --end 1402-12-29 --channels input/channels.json --keywords input/keywords.json --limit 10
```

This command will:

- Convert the Jalali dates to Gregorian.
- Load channels and keywords from the provided JSON files.
- Search and filter messages by the specified keywords and date range.
- Save post data (with reactions) to the database.
- Handle graceful shutdown on `CTRL+C`.

---

## Command-Line Arguments

The `main.py` script accepts the following arguments:

- `--start`: Start date in Jalali format (YYYY-MM-DD). **Required**.
- `--end`: End date in Jalali format (YYYY-MM-DD). **Required**.
- `--channels`: Path to the JSON file containing the list of channels. Default: `input/channels.json`.
- `--keywords`: Path to the JSON file containing the list of keywords. Default: `input/keywords.json`.
- `--limit`: Maximum number of comments to fetch per post. Default: `10`.

### Example Usage

```bash
python main.py --start 1402-01-01 --end 1402-12-29 --channels input/channels.json --keywords input/keywords.json --limit 10
```

This command will:

- Crawl posts from the specified channels.
- Filter posts by the given keywords and date range.
- Fetch up to 10 comments per post.
- Save the data to the MySQL database and log events to ClickHouse.

---

## Output Formats

### Post (Database Record)

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

### Comments (Database Record)

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
- Progress is saved in the database for resuming later.

---

## License

This project is licensed under the MIT License. Feel free to use, modify, or contribute to the project.

---

## Contributing

Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request for major changes.
