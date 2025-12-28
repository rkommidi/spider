"""Inspect deal structure from product detail page."""
import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('WEBSITE_USERNAME')
password = os.getenv('WEBSITE_PASSWORD')
login_url = os.getenv('LOGIN_URL')
# Product with deals
product_url = "https://now.breakthrubev.com/bbg/en/Shop-All/Spirits/Vodka/American-Vodka/Tito%27s-Vodka-Handmade-1-75L/p/9008509"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Login
    print("Logging in...")
    page.goto(login_url, wait_until="networkidle", timeout=30000)
    time.sleep(1)

    # Accept cookies
    try:
        cookie_btn = page.wait_for_selector('button.js-cookie-banner-btn', timeout=3000)
        if cookie_btn:
            cookie_btn.click()
            time.sleep(1)
    except:
        pass

    # Fill login form
    username_field = page.wait_for_selector('input[placeholder="Email *"]', state='visible', timeout=5000)
    username_field.fill(username)
    time.sleep(1)

    password_field = page.wait_for_selector('input[placeholder="Password *"]', state='visible', timeout=5000)
    password_field.fill(password)
    time.sleep(2)

    # Click submit
    submit_inputs = page.query_selector_all('input.gigya-input-submit[type="submit"]')
    for submit_input in submit_inputs:
        if submit_input.is_visible():
            submit_input.click(force=True)
            break

    time.sleep(5)

    # Navigate to product page
    print(f"Navigating to: {product_url}")
    page.goto(product_url, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Look for deal table
    print("\n=== DEAL TABLE EXTRACTION ===\n")

    # Try to find deal table
    deal_table = page.query_selector('.m-deals-table')
    if deal_table:
        print("Found deal table!\n")

        # Get all table rows
        rows = deal_table.query_selector_all('tr')
        print(f"Found {len(rows)} rows\n")

        for idx, row in enumerate(rows):
            print(f"--- Row {idx} ---")
            cells = row.query_selector_all('td, th')
            for cell_idx, cell in enumerate(cells):
                text = cell.inner_text().strip()
                print(f"  Cell {cell_idx}: {text}")
            print()

        # Get full deal table HTML
        print("\n=== FULL DEAL TABLE HTML ===")
        print(deal_table.inner_html()[:1000])

        # Try to extract individual deals
        print("\n\n=== INDIVIDUAL DEALS ===\n")
        deal_rows = deal_table.query_selector_all('.m-deals-table__row, tr[class*="deal"]')
        print(f"Found {len(deal_rows)} deal rows")

        for idx, deal_row in enumerate(deal_rows[:3]):
            print(f"\nDeal {idx + 1}:")
            print(deal_row.inner_text())
            print("---")

    else:
        print("No deal table found")

        # Look for alternative deal structures
        print("\n=== Looking for alternative deal structures ===")
        deal_sections = page.query_selector_all('[class*="deal"]')
        print(f"Found {len(deal_sections)} elements with 'deal' in class")

        for elem in deal_sections[:5]:
            classes = elem.get_attribute('class')
            text = elem.inner_text()[:100]
            print(f"Class: {classes}")
            print(f"Text: {text}")
            print()

    # Save screenshot
    page.screenshot(path="deals_page.png")
    print("\nScreenshot saved to deals_page.png")

    browser.close()
