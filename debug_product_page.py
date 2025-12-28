#!/usr/bin/env python3
"""
Debug script to check what selectors are on product detail pages.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright
from scraper import ProductScraper
from dotenv import load_dotenv

load_dotenv()

def debug_product_page(url: str):
    """Check what's actually on a product detail page."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Run headless for logging
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            # Use scraper's login method
            scraper = ProductScraper(
                username=os.getenv('WEBSITE_USERNAME'),
                password=os.getenv('WEBSITE_PASSWORD'),
                headless=True
            )

            print("Logging in...")
            scraper._login(page)

            print(f"Navigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Check for description list items
            print("\n=== Checking .m-description-list__item ===")
            desc_items = page.query_selector_all('.m-description-list__item')
            print(f"Found {len(desc_items)} description list items")

            for i, item in enumerate(desc_items[:15]):  # Show first 15
                label_elem = item.query_selector('.m-description-list__item-label')
                data_elem = item.query_selector('.m-description-list__item-data')

                label = label_elem.inner_text().strip() if label_elem else "NO LABEL"
                data = data_elem.inner_text().strip() if data_elem else "NO DATA"

                print(f"  [{i}] {label}: {data}")

                # Show HTML for QTY/CSE specifically
                if label == 'QTY/CSE':
                    print(f"      HTML: {item.inner_html()[:300]}")
                    # Try alternative selectors
                    alt_data = item.inner_text().strip()
                    print(f"      Full text: {alt_data}")
                    # Try getting next sibling
                    all_text_nodes = item.query_selector_all('*')
                    print(f"      Child elements: {len(all_text_nodes)}")
                    for child in all_text_nodes[:5]:
                        print(f"        - {child.get_attribute('class')}: {child.inner_text().strip()[:50]}")

            # Try alternative selectors
            print("\n=== Checking alternative selectors ===")

            # Try dt/dd pairs
            dt_elements = page.query_selector_all('dt')
            print(f"Found {len(dt_elements)} <dt> elements")
            for dt in dt_elements[:10]:
                dd = dt.evaluate('el => el.nextElementSibling?.textContent')
                print(f"  {dt.inner_text().strip()}: {dd}")

            # Try table rows
            print("\n=== Checking for tables ===")
            tables = page.query_selector_all('table')
            print(f"Found {len(tables)} tables")

            # Check product overview section specifically
            print("\n=== Checking for product overview ===")
            overview = page.query_selector('.product-overview, .product-details, .product-info, [class*="overview"], [class*="product-spec"]')
            if overview:
                print(f"Found overview section: {overview.get_attribute('class')}")
                print(overview.inner_text()[:500])
            else:
                print("No overview section found")

            print("\n=== Debug complete ===")

        finally:
            browser.close()

if __name__ == '__main__':
    # Test with a product that doesn't have QTY in the name
    test_url = "https://now.breakthrubev.com/bbg/en/Shop-All/Spirits/Vodka/American-Vodka/Tito%27s-Vodka-Handmade-1-75L/p/9008509"
    debug_product_page(test_url)
