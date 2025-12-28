# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set up environment
cp .env.example .env
# Then edit .env with actual credentials

# Run the web scraper (requires valid credentials in .env)
python run_scraper.py

# Start Flask web application
python app.py
# Access at http://localhost:5000
```

### Docker

```bash
# Build containers
docker-compose build

# Run web application
docker-compose up web
docker-compose up -d web  # detached mode

# Run scraper once
docker-compose run --rm scraper

# View logs
docker-compose logs web
docker-compose logs -f web  # follow mode
```

### Database

```bash
# Database is auto-created at data/products.db on first run
# To inspect database:
sqlite3 data/products.db

# Common queries:
sqlite3 data/products.db "SELECT * FROM products LIMIT 10;"
sqlite3 data/products.db "SELECT * FROM price_history ORDER BY scraped_at DESC LIMIT 10;"
```

## Architecture Overview

This is a **web scraping and price tracking system** with three main components:

### 1. Web Scraper (`scraper.py`)
- Uses **Playwright** (headless Chromium) for browser automation
- Handles login flow with dynamic selector detection
- Scrapes product search results from breakthrubev.com
- Implements retry logic and error handling
- Returns structured product data (name, price, URL, timestamp)

**Key Design Decisions**:
- Playwright over Selenium for better async support and modern browser features
- Multiple selector fallbacks for robustness against site changes
- Screenshots saved on login failure for debugging (`login_error.png`)
- Configurable headless mode for development vs production

### 2. Database Layer (`database.py`)
- **SQLite** for local persistence with two normalized tables:
  - `products`: Stores unique products (name, URL)
  - `price_history`: Stores all price snapshots with timestamps
- Context manager pattern for connection handling
- Prevents duplicate entries via UNIQUE constraints
- Complex queries for price changes and historical analysis

**Key Design Decisions**:
- ROW_NUMBER() window function for latest price queries
- Indexes on product_id and scraped_at for performance
- UNIQUE constraints prevent duplicate price entries in same scrape window
- All timestamps stored as ISO format strings for SQLite compatibility

### 3. Flask Web Application (`app.py`)
- **Read-only** web interface for viewing data
- Three main views:
  - Home: All products with latest prices and recent changes
  - Product detail: Full price history for a single product
- Custom Jinja filters for formatting (prices, dates, CSS classes)
- Independent from scraper (can run separately)

**Key Design Decisions**:
- Template inheritance via base.html for consistent styling
- CSS-only styling (no external frameworks) for simplicity
- Database queries in route handlers (no ORM for this small app)
- No authentication (designed for local/internal use)

## Code Organization

### Entry Points
- `run_scraper.py`: CLI script for scheduled scraping
- `app.py`: Flask web server

### Core Modules
- `database.py`: All SQLite operations and schema
- `scraper.py`: Playwright automation and extraction logic

### Templates
- `templates/base.html`: Base template with styles and layout
- `templates/index.html`: Home page with product list and changes
- `templates/product_detail.html`: Individual product price history

### Configuration
- `.env`: Environment variables (credentials, paths)
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container definition
- `docker-compose.yml`: Service orchestration

## Important Implementation Details

### Scraper Selector Strategy

The scraper uses **fallback selector lists** to handle website variations:

```python
# Example from scraper.py:
username_selectors = [
    'input[name="username"]',
    'input[name="email"]',
    'input[type="email"]',
    # ... more fallbacks
]
```

When modifying selectors:
1. Test against the live site first
2. Add new selectors at the top of the list (most specific first)
3. Keep generic fallbacks at the end
4. Update scraper.py:124-180 for login selectors
5. Update scraper.py:200-220 for product selectors

### Database Queries

Price change detection uses window functions (database.py:145-170):

```sql
WITH ranked_prices AS (
    SELECT ..., ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY scraped_at DESC) as rn
    FROM price_history
)
```

This efficiently gets the last two prices per product without subqueries.

### Environment Variables

Required variables (fail fast if missing):
- `WEBSITE_USERNAME`: Login username
- `WEBSITE_PASSWORD`: Login password

Optional variables (have defaults):
- `DATABASE_PATH`: Default `data/products.db`
- `FLASK_HOST`: Default `0.0.0.0`
- `FLASK_PORT`: Default `5000`
- `FLASK_DEBUG`: Default `False`

### Error Handling

The scraper implements a **retry pattern** (scraper.py:34-48):
- 3 retry attempts by default
- Exponential backoff (5s, 10s, 15s)
- Screenshots saved on login failure
- Detailed logging at each step

When debugging failures:
1. Check logs for exception messages
2. Look for `login_error.png` screenshot
3. Verify credentials in .env
4. Test selectors against current website HTML

## Common Modifications

### Adding New Scraped Fields

1. Update `scraper.py:_extract_product_from_element()` to extract the field
2. Add field to product dictionary
3. Update `database.py` to add new column (write migration if needed)
4. Update Flask templates to display the field

### Changing Target Website/URL

1. Update `self.target_url` in `scraper.py:__init__` (line 20)
2. Update `self.login_url` if different (line 21)
3. Test and adjust login selectors in `_login()` method
4. Test and adjust product selectors in `_extract_products()` method

### Modifying Database Schema

1. Update table definitions in `database.py:_init_tables()` (lines 38-73)
2. Consider backward compatibility (existing databases)
3. Add migration logic or document manual migration steps
4. Update relevant query methods

### Customizing Flask UI

- Templates in `templates/` use Jinja2
- Styling in `<style>` blocks within `base.html`
- Add custom filters in `app.py` (see examples at lines 49-70)
- Grid layout uses CSS Grid for responsive design

## Testing Locally

Since credentials are required:

1. **Without valid credentials**: The scraper will fail at login. Use this to test error handling.

2. **With valid credentials**:
   ```bash
   # Run once to populate database
   python run_scraper.py

   # Start web app to view results
   python app.py
   ```

3. **Testing scraper changes**: Set `headless=False` in `run_scraper.py` temporarily to see browser actions.

## Deployment Considerations

- Database grows indefinitely (no cleanup implemented)
- No rate limiting or request throttling
- Login credentials stored in .env (ensure proper file permissions: `chmod 600 .env`)
- Flask development server used (consider gunicorn for production)
- No HTTPS on Flask app (use reverse proxy if exposing externally)

## File Ownership

The original requirements are in `claude.md` (lowercase). This CLAUDE.md file documents the implemented system.
