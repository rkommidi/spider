"""Detailed inspection of deal structure."""
import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('WEBSITE_USERNAME')
password = os.getenv('WEBSITE_PASSWORD')
login_url = os.getenv('LOGIN_URL')
product_url = "https://now.breakthrubev.com/bbg/en/Shop-All/Spirits/Vodka/American-Vodka/Tito%27s-Vodka-Handmade-1-75L/p/9008509"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Login (abbreviated)
    page.goto(login_url, wait_until="networkidle", timeout=30000)
    time.sleep(1)
    try:
        page.wait_for_selector('button.js-cookie-banner-btn', timeout=3000).click()
        time.sleep(1)
    except:
        pass
    page.wait_for_selector('input[placeholder="Email *"]', state='visible', timeout=5000).fill(username)
    time.sleep(1)
    page.wait_for_selector('input[placeholder="Password *"]', state='visible', timeout=5000).fill(password)
    time.sleep(2)
    for submit_input in page.query_selector_all('input.gigya-input-submit[type="submit"]'):
        if submit_input.is_visible():
            submit_input.click(force=True)
            break
    time.sleep(5)

    # Navigate to product
    page.goto(product_url, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    print("=== DEAL STRUCTURE ANALYSIS ===\n")

    # Find the deal table
    deal_table = page.query_selector('.c-deals-pdp__table')
    if deal_table:
        print("✓ Found deal table\n")

        # Get table HTML for analysis
        table_html = deal_table.inner_html()
        with open('deal_table.html', 'w') as f:
            f.write(table_html)
        print("Saved deal table HTML to deal_table.html\n")

        # Extract table rows
        thead = deal_table.query_selector('thead')
        tbody = deal_table.query_selector('tbody')

        if thead:
            print("=== Table Headers ===")
            headers = thead.query_selector_all('th')
            for idx, header in enumerate(headers):
                print(f"Header {idx}: {header.inner_text().strip()}")
            print()

        if tbody:
            print("=== Table Body Rows ===")
            rows = tbody.query_selector_all('tr')
            print(f"Found {len(rows)} rows\n")

            for row_idx, row in enumerate(rows[:5]):
                print(f"--- Row {row_idx + 1} ---")

                # Get all data-* attributes
                for attr in ['data-deal-title', 'data-deal-number', 'data-sku-number',
                             'data-usage-limit', 'data-quantity-type', 'data-bottle-fees-applicable']:
                    value = row.get_attribute(attr)
                    if value:
                        print(f"{attr}: {value}")

                # Get all cells
                cells = row.query_selector_all('td')
                for cell_idx, cell in enumerate(cells):
                    text = cell.inner_text().strip()
                    classes = cell.get_attribute('class')
                    print(f"  Cell {cell_idx} ({classes}): {text}")

                print()

    # Check if there's a "View All Deals" button/link
    print("\n=== Looking for 'View All Deals' ===")
    view_all = page.query_selector_all('a:has-text("View All Deals"), button:has-text("View All Deals")')
    if view_all:
        print(f"Found {len(view_all)} 'View All Deals' elements")
        for elem in view_all:
            print(f"  Text: {elem.inner_text()}")
            print(f"  href: {elem.get_attribute('href')}")

    # Click "View All Deals" if it exists
    if view_all and len(view_all) > 0:
        print("\nClicking 'View All Deals'...")
        view_all[0].click()
        time.sleep(2)

        # Check for modal/popup
        modal = page.query_selector('.modal, [class*="modal"], [role="dialog"]')
        if modal:
            print("Found modal/dialog!")
            modal_html = modal.inner_html()
            with open('deals_modal.html', 'w') as f:
                f.write(modal_html)
            print("Saved modal HTML to deals_modal.html")

            # Extract all deals from modal
            deal_items = modal.query_selector_all('[class*="deal-item"], [class*="deal-row"], tr')
            print(f"\nFound {len(deal_items)} potential deal items in modal")

            for idx, item in enumerate(deal_items[:3]):
                print(f"\n--- Deal Item {idx + 1} ---")
                print(item.inner_text()[:200])

    page.screenshot(path="deals_detailed.png")
    print("\nScreenshot saved to deals_detailed.png")

    browser.close()
