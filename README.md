# Product Price Tracker

An automated web scraping system that tracks product prices from breakthrubev.com, stores historical price data in SQLite, and provides a Flask web interface for viewing price trends.

## Features

- **Automated Web Scraping**: Uses Playwright for robust browser automation
- **Login Handling**: Manages authentication and session persistence
- **Price Tracking**: Stores complete price history with timestamps
- **Price Change Detection**: Identifies and reports price changes between scrapes
- **Web Dashboard**: Clean Flask interface to view products and price history
- **Docker Support**: Fully containerized for easy deployment
- **Scheduled Execution**: Designed to run daily via cron or task scheduler

## Project Structure

```
spider/
├── app.py                  # Flask web application
├── run_scraper.py          # CLI scraper script
├── database.py             # SQLite database operations
├── scraper.py              # Playwright web scraper
├── templates/              # Flask HTML templates
│   ├── base.html
│   ├── index.html
│   └── product_detail.html
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose orchestration
├── .env.example            # Environment variables template
└── data/                   # SQLite database storage (created on first run)
```

## Installation

### Option 1: Local Installation

1. **Clone or navigate to the project directory**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers**:
```bash
playwright install chromium
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env and add your credentials
```

### Option 2: Docker Installation

1. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env and add your credentials
```

2. **Build the Docker image**:
```bash
docker-compose build
```

## Configuration

Edit the `.env` file with your credentials:

```env
# Website Login Credentials
WEBSITE_USERNAME=your_username_here
WEBSITE_PASSWORD=your_password_here

# Database Configuration
DATABASE_PATH=data/products.db

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

## Usage

### Running the Scraper

**Local**:
```bash
python run_scraper.py
```

**Docker**:
```bash
docker-compose run --rm scraper
```

The scraper will:
1. Log into the website
2. Navigate to the search results page
3. Extract product names, prices, and URLs
4. Store data in the SQLite database
5. Detect and report price changes

### Running the Web Application

**Local**:
```bash
python app.py
```

Then visit `http://localhost:5000` in your browser.

**Docker**:
```bash
docker-compose up web
```

Then visit `http://localhost:5000` in your browser.

### Running Both (Docker)

```bash
# Start web application
docker-compose up -d web

# Run scraper manually when needed
docker-compose run --rm scraper
```

## Scheduling

### Linux/macOS (cron)

Add to your crontab (`crontab -e`):

```bash
# Run scraper daily at 2 AM
0 2 * * * cd /path/to/spider && /usr/bin/python3 run_scraper.py >> /path/to/spider/scraper.log 2>&1

# Or with Docker
0 2 * * * cd /path/to/spider && /usr/local/bin/docker-compose run --rm scraper >> /path/to/spider/scraper.log 2>&1
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.spider.scraper.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.spider.scraper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/spider/run_scraper.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>/path/to/spider</string>
    <key>StandardOutPath</key>
    <string>/path/to/spider/scraper.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/spider/scraper.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.spider.scraper.plist
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Daily" at your preferred time
4. Action: "Start a program"
   - Program: `python.exe`
   - Arguments: `run_scraper.py`
   - Start in: `C:\path\to\spider`

Or with Docker:
- Program: `docker-compose.exe`
- Arguments: `run --rm scraper`
- Start in: `C:\path\to\spider`

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, url)
);
```

### Price History Table
```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    price REAL NOT NULL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE(product_id, price, scraped_at)
);
```

## Troubleshooting

### Scraper Issues

1. **Login fails**:
   - Verify credentials in `.env`
   - Check `login_error.png` screenshot for debugging
   - Website selectors may have changed

2. **No products found**:
   - Website structure may have changed
   - Check network connectivity
   - Verify search URL is accessible

3. **Playwright errors**:
   - Ensure browsers are installed: `playwright install chromium`
   - Check system dependencies

### Database Issues

- Database is automatically created on first run
- Located at `data/products.db` by default
- Use SQLite browser to inspect data if needed

### Docker Issues

- Ensure Docker and Docker Compose are installed
- Check container logs: `docker-compose logs`
- Verify `.env` file exists and has correct values

## Development

### Running Tests

(Note: Test suite not yet implemented)

### Code Structure

- `scraper.py`: Contains `ProductScraper` class with login and extraction logic
- `database.py`: Contains `Database` class with all SQLite operations
- `run_scraper.py`: CLI entry point that orchestrates scraping and storage
- `app.py`: Flask application with routes and template filters

## License

This project is for educational and personal use only. Respect website terms of service and robots.txt when scraping.
