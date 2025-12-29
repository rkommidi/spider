#!/usr/bin/env python3
"""Debug script to inspect login page structure"""
import os
from playwright.sync_api import sync_playwright
import time

def debug_login_page():
    username = os.getenv('WEBSITE_USERNAME', '')
    login_url = os.getenv('LOGIN_URL', 'https://now.breakthrubev.com/bbg/en/login')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"Navigating to: {login_url}")
        page.goto(login_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)  # Wait for any JS to execute

        # Take screenshot
        page.screenshot(path="/app/screenshots/debug_login.png")
        print("Screenshot saved to /app/screenshots/debug_login.png")

        # Get page title
        title = page.title()
        print(f"\nPage title: {title}")

        # Get page URL (in case of redirects)
        url = page.url
        print(f"Current URL: {url}")

        # Find all input fields
        print("\n=== All Input Fields ===")
        inputs = page.query_selector_all('input')
        for i, inp in enumerate(inputs):
            input_type = inp.get_attribute('type') or 'text'
            input_name = inp.get_attribute('name') or ''
            input_id = inp.get_attribute('id') or ''
            input_placeholder = inp.get_attribute('placeholder') or ''
            input_class = inp.get_attribute('class') or ''
            is_visible = inp.is_visible()

            print(f"\nInput {i+1}:")
            print(f"  Type: {input_type}")
            print(f"  Name: {input_name}")
            print(f"  ID: {input_id}")
            print(f"  Placeholder: {input_placeholder}")
            print(f"  Class: {input_class}")
            print(f"  Visible: {is_visible}")

        # Find all buttons
        print("\n\n=== All Buttons ===")
        buttons = page.query_selector_all('button')
        for i, btn in enumerate(buttons):
            btn_type = btn.get_attribute('type') or ''
            btn_text = btn.inner_text() or ''
            btn_class = btn.get_attribute('class') or ''
            is_visible = btn.is_visible()

            print(f"\nButton {i+1}:")
            print(f"  Type: {btn_type}")
            print(f"  Text: {btn_text}")
            print(f"  Class: {btn_class}")
            print(f"  Visible: {is_visible}")

        # Get page HTML snippet
        print("\n\n=== Page HTML (first 2000 chars) ===")
        html = page.content()
        print(html[:2000])

        browser.close()

if __name__ == '__main__':
    debug_login_page()
