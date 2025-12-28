#!/bin/bash
# Script to scrape all spirit categories to get all 7,000 products

echo "Starting multi-category scrape to collect all products..."
echo "This will run multiple scrapes for different spirit categories"
echo ""

# Main spirit categories
categories=(
    "vodka"
    "whiskey"
    "rum"
    "gin"
    "tequila"
    "mezcal"
    "brandy"
    "cognac"
    "scotch"
    "bourbon"
    "rye"
    "cordials"
    "liqueur"
)

for category in "${categories[@]}"; do
    echo "====================================="
    echo "Scraping category: $category"
    echo "====================================="
    python run_scraper.py --query "$category" --infinite-scroll --scroll-max-attempts 200 2>&1 | tee -a /tmp/scrape_category_${category}.log
    echo ""
    echo "Completed: $category"
    echo ""
    sleep 5
done

echo "====================================="
echo "All categories scraped!"
echo "====================================="

# Count total products
echo "Total products in database:"
sqlite3 data/products.db "SELECT COUNT(*) FROM products;"
