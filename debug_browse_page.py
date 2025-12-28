#!/usr/bin/env python3
"""Debug script to inspect the browse page structure."""

import os
import time
from playwright.sync_api import sync_playwright
from scraper import ProductScraper
from dotenv import load_dotenv

load_dotenv()

def debug_browse_page():
    """Check what's on the browse page."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Run headless
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

            # Navigate to browse page
            url = "https://now.breakthrubev.com/bbg/en/Shop-All/Spirits"
            print(f"\nNavigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(5)

            # Check for different product selectors
            print("\n=== Checking product selectors ===")
            selectors_to_try = [
                '.m-product-card',
                '.product-card',
                '[class*="product"]',
                '.a-product',
                '.product-item',
                'article',
                '[data-product-id]',
            ]

            for selector in selectors_to_try:
                elements = page.query_selector_all(selector)
                print(f"{selector}: {len(elements)} elements")

            # Check page title and body text
            print(f"\n=== Page Info ===")
            print(f"Title: {page.title()}")
            print(f"URL: {page.url}")

            # Get all links
            links = page.query_selector_all('a[href*="/p/"]')
            print(f"\nProduct links (href contains '/p/'): {len(links)}")
            if links:
                for i, link in enumerate(links[:5]):
                    print(f"  {i+1}. {link.get_attribute('href')}")

            # Take screenshot
            page.screenshot(path="browse_page_debug.png")
            print("\nScreenshot saved: browse_page_debug.png")

            print("\nDebug complete!")

        finally:
            browser.close()

if __name__ == '__main__':
    debug_browse_page()
