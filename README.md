# Telegram Crawler

یک crawler مقاوم و ماژولار برای تلگرام که پست‌های کانال، واکنش‌ها و نظرات زنجیره‌ای را بر اساس فیلترهای کلیدواژه و بازه‌ی زمانی بازیابی می‌کند. این crawler برای مدیریت محدودیت‌های نرخ (rate limits)، ذخیره‌ی پیشرفت و ادامه از آخرین وضعیت پس از وقفه‌ها طراحی شده است.

---

## ویژگی‌ها

- **Keyword-Based Search:** جستجو در کانال‌های عمومی برای پست‌هایی که با کلیدواژه‌های مشخص مطابقت دارند.
- **Date Filtering:** فیلتر کردن پست‌ها در بازه‌ی زمانی تعیین‌شده (Jalali/Shamsi) و تبدیل آن به تاریخ‌های Gregorian.
- **Comment Fetching:** بازیابی نظرات زنجیره‌ای (اگر گروه بحث مرتبط باشد).
- **Reactions Extraction:** استخراج ایموجی‌ها و شمارش واکنش‌ها به پست.
- **State Persistence:** ذخیره‌ی پیشرفت (آخرین پیام پردازش شده) برای ادامه‌ی عملیات پس از وقفه.
- **Rate-Limit Handling:** مدیریت خطای FloodWaitError تلگرام به‌صورت gracefull.
- **Structured Storage:** سازمان‌دهی پست‌ها و نظرات در فایل‌های JSON جداگانه.
- **Database Integration:** ذخیره‌ی پست‌ها و نظرات در پایگاه‌داده MySQL.
- **ClickHouse Logging:** ثبت رویدادها و خطاها در ClickHouse برای مانیتورینگ.
- **View Data:** شامل اسکریپتی برای مشاهده‌ی پست‌ها و نظرات ذخیره‌شده.
- **Modular Codebase:** معماری تمیز و قابل توسعه برای اضافه کردن قابلیت‌های جدید.

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

## دستورالعمل راه‌اندازی

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

    در فایل `config.py` شناسه و هش API تلگرام خود را وارد کنید:

    ```python
    api_id = 123456              # Your API ID from my.telegram.org
    api_hash = 'your_api_hash'   # Your API hash
    ```

4. **Prepare Input Files**

    - **channels.json:** شامل آرایه‌ای از URL‌های کانال‌های عمومی.
    - **keywords.json:** شامل آرایه‌ای از کلیدواژه‌ها برای فیلتر کردن پست‌ها.

5. **Initialize the Database**

    تنظیمات پایگاه‌داده را در `db/db.py` به‌روز کنید و سپس:

    ```python
    from db.db import init_db
    init_db()
    ```

6. **View Stored Data**

    برای مشاهده‌ی پست‌ها و نظرات ذخیره‌شده از `view_data.py` استفاده کنید:

    ```bash
    python view_data.py
    ```

---

## Database Configuration

### MySQL Setup

1. نصب MySQL:

    ```bash
    sudo apt update
    sudo apt install mysql-server
    ```

2. ورود به MySQL و ایجاد پایگاه‌داده:

    ```bash
    mysql -u root -p
    CREATE DATABASE telegram_db;
    CREATE USER 'reza'@'localhost' IDENTIFIED BY '1234';
    GRANT ALL PRIVILEGES ON telegram_db.* TO 'reza'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;
    ```

3. به‌روز کردن `DB_URL` در `db/db.py`:

    ```python
    DB_URL = "mysql+pymysql://reza:1234@localhost/telegram_db"
    ```

### ClickHouse Setup

1. نصب ClickHouse:

    ```bash
    sudo apt update
    sudo apt install clickhouse-server clickhouse-client
    ```

2. راه‌اندازی سرویس ClickHouse:

    ```bash
    sudo service clickhouse-server start
    ```

3. ایجاد پایگاه‌داده برای لاگ‌ها در ClickHouse:

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

4. به‌روز کردن تنظیمات ClickHouse در `utils/ch_logger.py`:

    ```python
    CH_HOST = "localhost"
    CH_PORT = 9000
    CH_DATABASE = "crawler_logs_db"
    CH_USER = "default"
    CH_PASSWORD = ""
    ```

---

## Usage

```bash
python main.py --start 1402-01-01 --end 1402-12-29 --channels input/channels.json --keywords input/keywords.json --limit 10
```

این دستور:

- تاریخ‌های Jalali را به Gregorian تبدیل می‌کند.
- کانال‌ها و کلیدواژه‌ها را از فایل‌های JSON بارگذاری می‌کند.
- پیام‌ها را با توجه به کلیدواژه و بازه‌ی زمانی فیلتر می‌کند.
- داده‌ها را در MySQL ذخیره و رویدادها را در ClickHouse لاگ می‌کند.

---

## آرگومان‌های خط فرمان

- `--start`: تاریخ شروع به فرمت Jalali (YYYY-MM-DD). **الزامی**.
- `--end`: تاریخ پایان به فرمت Jalali (YYYY-MM-DD). **الزامی**.
- `--channels`: مسیر فایل JSON حاوی لیست کانال‌ها. پیش‌فرض: `input/channels.json`.
- `--keywords`: مسیر فایل JSON حاوی کلیدواژه‌ها. پیش‌فرض: `input/keywords.json`.
- `--limit`: حداکثر تعداد نظرات برای هر پست. پیش‌فرض: `10`.

---

## Example Usage

```bash
python main.py --start 1402-01-01 --end 1402-12-29 --channels input/channels.json --keywords input/keywords.json --limit 10
```

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

- برای متوقف کردن عملیات دکمه `CTRL+C` را فشار دهید.
- crawler عملیات جاری را تکمیل کرده و سپس خارج می‌شود.
- پیشرفت در پایگاه‌داده ذخیره می‌شود تا بعداً بتوانید ادامه دهید.

---

## License

این پروژه تحت مجوز MIT منتشر شده است. برای استفاده، اصلاح یا مشارکت آزاد هستید.

---

## Contributing

اشکال‌زدایی و درخواست ویژگی خوش‌آمدید! لطفاً issue باز کنید یا pull request ارسال نمایید.

