#!/usr/bin/env python3
"""
Script to update qty_per_case for existing products by re-visiting their detail pages.
"""

import os
import sys
import time
import logging
from database import Database
from scraper import ProductScraper
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Update qty_per_case for products with NULL values but recognizable patterns."""

    # Load environment
    load_dotenv()

    # Initialize database
    db_path = os.getenv('DATABASE_PATH', 'data/products.db')
    db = Database(db_path)

    # Get ALL products that need QTY/CSE extraction
    # Now that we fixed the selector, we can extract from product overview page
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, url
            FROM products
            WHERE qty_per_case IS NULL
            ORDER BY name
            LIMIT 100
        """)
        products = [dict(row) for row in cursor.fetchall()]

    if not products:
        logger.info("No products found needing QTY/CSE extraction")
        return

    logger.info(f"Found {len(products)} products to update")

    # Use Playwright directly like the scraper does
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            # Initialize scraper for helper methods
            scraper = ProductScraper(
                username=os.getenv('WEBSITE_USERNAME'),
                password=os.getenv('WEBSITE_PASSWORD'),
                headless=True
            )

            # Login first
            logger.info("Logging in...")
            scraper._login(page)

            updated_count = 0
            for i, product in enumerate(products, 1):
                product_id = product['id']
                name = product['name']
                url = product['url']

                logger.info(f"[{i}/{len(products)}] Updating: {name}")

                try:
                    # Navigate to product page
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    time.sleep(2)  # Wait for dynamic content

                    # Extract details using the scraper's method
                    details = scraper._extract_product_details(page, url)

                    if details and 'qty_per_case' in details and details['qty_per_case']:
                        # Update the product
                        with db.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE products SET qty_per_case = ? WHERE id = ?",
                                (details['qty_per_case'], product_id)
                            )
                            conn.commit()
                        logger.info(f"  ✓ Updated qty_per_case = {details['qty_per_case']}")
                        updated_count += 1
                    else:
                        logger.info(f"  ✗ No QTY/CSE extracted")

                    # Small delay to be polite
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"  Error updating product {product_id}: {str(e)}")
                    continue

            logger.info(f"\n{'='*60}")
            logger.info(f"Update complete!")
            logger.info(f"  Products updated: {updated_count}/{len(products)}")
            logger.info(f"{'='*60}")

        finally:
            browser.close()

if __name__ == '__main__':
    main()
