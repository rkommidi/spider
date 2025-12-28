import os
import time
from typing import List, Dict, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductScraper:
    """Handles web scraping of product prices using Playwright."""

    def __init__(self, username: str, password: str, headless: bool = True, search_query: str = "oban"):
        """
        Initialize the scraper.

        Args:
            username: Login username
            password: Login password
            headless: Run browser in headless mode
            search_query: Product search query (default: "oban")
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.search_query = search_query
        self.target_url = f"https://now.breakthrubev.com/bbg/en/search?text={search_query}"
        self.login_url = os.getenv('LOGIN_URL', "https://www.breakthrubev.com/login")
        self.base_domain = "https://now.breakthrubev.com"

    def scrape_products(self, max_retries: int = 3) -> List[Dict]:
        """
        Scrape products with retry logic.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            List of scraped products

        Raises:
            Exception: If scraping fails after all retries
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping attempt {attempt + 1}/{max_retries}")
                return self._scrape_with_playwright()
            except Exception as e:
                logger.error(f"Scraping attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(5 * (attempt + 1))

    def _scrape_with_playwright(self) -> List[Dict]:
        """
        Perform the actual scraping using Playwright.

        Returns:
            List of scraped products
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()

            try:
                # Login
                logger.info("Attempting to log in...")
                self._login(page)

                # Navigate to search results
                logger.info(f"Navigating to search results: {self.target_url}")
                page.goto(self.target_url, wait_until="networkidle", timeout=30000)
                time.sleep(2)

                # Extract products
                logger.info("Extracting product data...")
                products = self._extract_products(page)
                logger.info(f"Successfully extracted {len(products)} products")

                return products

            finally:
                browser.close()

    def _login(self, page: Page):
        """
        Handle the login flow.

        Args:
            page: Playwright page object

        Raises:
            Exception: If login fails
        """
        try:
            page.goto(self.login_url, wait_until="networkidle", timeout=30000)
            time.sleep(1)

            # Accept cookie notice if present
            try:
                cookie_btn = page.wait_for_selector('button.js-cookie-banner-btn', timeout=3000)
                if cookie_btn:
                    cookie_btn.click()
                    logger.info("Accepted cookie notice")
                    time.sleep(1)
            except:
                logger.info("No cookie notice found or already accepted")
                pass

            # Look for common login form selectors
            # These selectors may need to be adjusted based on actual site structure
            # Gigya-specific selectors for the visible login form
            username_selectors = [
                'input[placeholder="Email *"]',
                'input.gigya-input-text[name="username"]',
                'input[name="username"][placeholder]',
                'input[name="username"]',
                'input[name="email"]',
                'input[type="email"]',
                'input[id*="username"]',
                'input[id*="email"]',
                '#username',
                '#email'
            ]

            password_selectors = [
                'input[placeholder="Password *"]',
                'input.gigya-input-password[name="password"]',
                'input[name="password"][placeholder]',
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]

            submit_selectors = [
                'input.gigya-input-submit[type="submit"]',
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Sign in")'
            ]

            # Find and fill username field (only visible fields)
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = page.wait_for_selector(selector, state='visible', timeout=5000)
                    if username_field and username_field.is_visible():
                        logger.info(f"Found username field with selector: {selector}")
                        break
                except:
                    continue

            if not username_field:
                raise Exception("Could not find username field")

            username_field.fill(self.username)
            time.sleep(1)

            # Find and fill password field (only visible fields)
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = page.wait_for_selector(selector, state='visible', timeout=5000)
                    if password_field and password_field.is_visible():
                        logger.info(f"Found password field with selector: {selector}")
                        break
                except:
                    continue

            if not password_field:
                raise Exception("Could not find password field")

            password_field.fill(self.password)
            # Wait for form to update/enable submit button
            time.sleep(2)

            # Find and click submit button - the "Log in" button is an input element
            submit_clicked = False

            # Try to click the visible Gigya submit button (it's an input, not a button)
            try:
                # Find all submit inputs and click the visible one
                submit_inputs = page.query_selector_all('input.gigya-input-submit[type="submit"]')
                for submit_input in submit_inputs:
                    if submit_input.is_visible():
                        logger.info("Found visible Gigya submit button, clicking...")
                        submit_input.click(force=True)
                        submit_clicked = True
                        break
            except Exception as e:
                logger.warning(f"Failed to click Gigya submit: {e}")

            # Fallback: try other selectors
            if not submit_clicked:
                for selector in submit_selectors:
                    try:
                        submit_button = page.wait_for_selector(selector, state='visible', timeout=3000)
                        if submit_button and submit_button.is_visible():
                            logger.info(f"Found submit button with selector: {selector}")
                            submit_button.click(force=True)
                            submit_clicked = True
                            break
                    except:
                        continue

            if not submit_clicked:
                raise Exception("Could not click submit button")

            # Wait for navigation after login
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeoutError:
                # Sometimes networkidle doesn't trigger, wait for URL change instead
                time.sleep(3)

            logger.info("Login successful")

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            # Take screenshot for debugging
            page.screenshot(path="login_error.png")
            raise Exception(f"Login failed: {str(e)}")

    def _extract_products(self, page: Page) -> List[Dict]:
        """
        Extract product information from the search results page.

        Args:
            page: Playwright page object

        Returns:
            List of product dictionaries
        """
        products = []
        scraped_at = datetime.now()

        # Wait for product listings to load
        # The new portal uses m-product-card class
        try:
            page.wait_for_selector('.m-product-card', timeout=10000)
            logger.info("Product cards loaded successfully")
        except PlaywrightTimeoutError:
            logger.warning("Product selector not found, attempting alternate selectors")

        # New portal uses .m-product-card for product containers
        product_selectors = [
            '.m-product-card',
            'div[class*="product-card"]',
            '.product',
            '.product-item',
        ]

        # Try different selectors to find products
        product_elements = []
        for selector in product_selectors:
            product_elements = page.query_selector_all(selector)
            if product_elements:
                logger.info(f"Found {len(product_elements)} products using selector: {selector}")
                break

        if not product_elements:
            logger.warning("No products found with standard selectors")
            # Take screenshot for debugging
            page.screenshot(path="no_products_found.png")
            return products

        # First pass: Extract all basic product info from search results
        basic_products = []
        for idx, element in enumerate(product_elements, 1):
            try:
                logger.info(f"Extracting basic info from product {idx}/{len(product_elements)}")
                basic_product = self._extract_product_from_element(element)
                if basic_product:
                    basic_products.append(basic_product)
                    logger.info(f"Got basic info: {basic_product['name']}")
                else:
                    logger.warning(f"Could not extract basic product info from element {idx}")
            except Exception as e:
                logger.error(f"Error extracting basic info from product {idx}: {str(e)}")
                continue

        logger.info(f"Extracted basic info for {len(basic_products)} products, now fetching details...")

        # Second pass: Visit each product detail page to get additional fields
        for idx, basic_product in enumerate(basic_products, 1):
            try:
                if basic_product.get('url'):
                    logger.info(f"[{idx}/{len(basic_products)}] Extracting details for: {basic_product['name']}")
                    try:
                        detailed_product = self._extract_product_details(page, basic_product['url'])
                        # Merge basic and detailed data
                        product = {**basic_product, **detailed_product}
                        product['scraped_at'] = scraped_at
                        products.append(product)
                        logger.info(f"[{idx}/{len(basic_products)}] Successfully extracted: {basic_product['name']}")
                    except Exception as e:
                        logger.error(f"Error extracting details for {basic_product['name']}: {str(e)}")
                        # Add product with basic info only
                        basic_product['scraped_at'] = scraped_at
                        products.append(basic_product)
                        logger.info(f"Added {basic_product['name']} with basic info only")
                else:
                    # No URL, just use basic data
                    basic_product['scraped_at'] = scraped_at
                    products.append(basic_product)
                    logger.info(f"Added {basic_product['name']} (no URL for details)")
            except Exception as e:
                logger.error(f"Error processing product {basic_product.get('name', 'unknown')}: {str(e)}", exc_info=True)
                continue

        return products

    def _extract_product_from_element(self, element) -> Optional[Dict]:
        """
        Extract product data from a single element.

        Args:
            element: Playwright element locator

        Returns:
            Product dictionary or None if extraction fails
        """
        product = {
            'name': None,
            'price': None,
            'url': None
        }

        # Extract product name
        # New portal uses .m-product-card__name .a-product-name
        name_selectors = [
            '.m-product-card__name .a-product-name',
            '.m-product-card__name',
            '.a-product-name',
            '.product-name',
            '.product-title',
            'h2',
            'h3',
        ]

        for selector in name_selectors:
            try:
                name_elem = element.query_selector(selector)
                if name_elem:
                    product['name'] = name_elem.inner_text().strip()
                    if product['name']:
                        break
            except:
                continue

        # Extract price
        # New portal uses .m-product-card__price .a-price
        price_selectors = [
            '.m-product-card__price .a-price',
            '.a-price',
            '.m-product-card__price',
            '.price',
            '.product-price',
            '[class*="price"]',
        ]

        for selector in price_selectors:
            try:
                price_elem = element.query_selector(selector)
                if price_elem:
                    price_text = price_elem.inner_text().strip()
                    # Extract numeric value from price string
                    price = self._parse_price(price_text)
                    if price is not None:
                        product['price'] = price
                        break
            except:
                continue

        # Extract URL
        # New portal uses a.m-product-card__link
        try:
            link_elem = element.query_selector('a.m-product-card__link, a')
            if link_elem:
                href = link_elem.get_attribute('href')
                if href:
                    # Make absolute URL if relative
                    if href.startswith('/'):
                        product['url'] = f"{self.base_domain}{href}"
                    elif href.startswith('http'):
                        product['url'] = href
        except:
            pass

        # Only return if we have at least name
        if product['name']:
            if product['price'] is None:
                logger.warning(f"Product {product['name']} has no price, will extract details anyway")
            return product
        else:
            logger.warning(f"Product element missing name, URL: {product.get('url')}")
            return None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price from text string.

        Args:
            price_text: Price as text (e.g., "$19.99", "£20.50")

        Returns:
            Price as float or None if parsing fails
        """
        try:
            # Remove currency symbols and whitespace
            cleaned = price_text.replace('$', '').replace('£', '').replace('€', '').replace(',', '').strip()

            # Extract first number (handles cases like "$19.99 USD")
            import re
            match = re.search(r'\d+\.?\d*', cleaned)
            if match:
                return float(match.group())

        except Exception as e:
            logger.error(f"Failed to parse price '{price_text}': {str(e)}")

        return None

    def _extract_product_details(self, page: Page, product_url: str) -> Dict:
        """
        Extract detailed product information from product detail page.

        Args:
            page: Playwright page object
            product_url: URL of the product detail page

        Returns:
            Dictionary with detailed product fields
        """
        details = {}

        try:
            # Navigate to product detail page
            page.goto(product_url, wait_until="networkidle", timeout=15000)
            time.sleep(1)

            # Extract brand from data attribute
            brand_elem = page.query_selector('[data-product-brand]')
            if brand_elem:
                details['brand'] = brand_elem.get_attribute('data-product-brand')

            # Extract supplier from data attribute
            supplier_elem = page.query_selector('[data-product-supplier]')
            if supplier_elem:
                details['supplier'] = supplier_elem.get_attribute('data-product-supplier')

            # Extract all description list items (contains most product details)
            desc_items = page.query_selector_all('.m-description-list__item')
            for item in desc_items:
                label_elem = item.query_selector('.m-description-list__item-label')
                data_elem = item.query_selector('.m-description-list__item-data')

                if label_elem and data_elem:
                    label = label_elem.inner_text().strip()
                    data = data_elem.inner_text().strip()

                    # Map labels to database fields
                    if label == 'Product ID':
                        details['product_id'] = data
                    elif label == 'Bottle UPC':
                        details['bottle_upc'] = data
                    elif label == 'Case UPC':
                        details['case_upc'] = data
                    elif label == 'Size':
                        details['size'] = data
                    elif label == 'QTY/CSE':
                        try:
                            details['qty_per_case'] = int(data)
                        except:
                            details['qty_per_case'] = data
                    elif label == 'Proof/ABV':
                        details['proof_abv'] = data
                    elif label == 'Container Type':
                        details['container_type'] = data
                    elif label == 'Brand':
                        details['brand'] = data
                    elif label == 'Supplier':
                        details['supplier'] = data
                    elif label == 'Country of Origin':
                        details['country_of_origin'] = data
                    elif label == 'Region':
                        details['region'] = data

            # Extract categories from URL path
            # URL format: /Shop-All/Spirits/Vodka/American-Vodka/Product-Name/p/12345
            current_url = page.url
            categories = []

            try:
                if '/Shop-All/' in current_url:
                    # Extract the path between Shop-All and /p/
                    parts = current_url.split('/Shop-All/')[1].split('/p/')[0]
                    # Split by / and decode URL encoding
                    import urllib.parse
                    category_parts = [urllib.parse.unquote(p) for p in parts.split('/') if p]

                    # Remove the last part (product name) - it's usually the most specific
                    if len(category_parts) > 1:
                        categories = category_parts[:-1]
                    else:
                        categories = category_parts
            except Exception as e:
                logger.debug(f"Could not extract categories from URL: {str(e)}")

            # Also try breadcrumbs as fallback
            if not categories:
                breadcrumbs = page.query_selector_all('.m-breadcrumbs__link, .breadcrumb a, nav[aria-label="breadcrumb"] a')
                for bc in breadcrumbs:
                    cat = bc.inner_text().strip()
                    if cat and cat not in ['Home', 'Shop All']:
                        categories.append(cat)

            if categories:
                details['categories'] = ', '.join(categories)

            # Extract QTY/CSE from product name if not already extracted
            # Look for patterns like "6B", "12B", "24B" (bottles per case)
            # or "6/12PK", "15/4PK" etc.
            if 'qty_per_case' not in details or not details['qty_per_case']:
                import re
                # Get product name from URL and page title
                product_name_from_url = page.url.split('/p/')[0].split('/')[-1] if '/p/' in page.url else ''
                product_name_from_title = page.title()

                # Try both sources
                for product_name in [product_name_from_url, product_name_from_title]:
                    if not product_name:
                        continue

                    # Pattern 1: "6B", "12B" etc (X bottles)
                    match = re.search(r'(\d+)B\b', product_name, re.IGNORECASE)
                    if match:
                        try:
                            qty = int(match.group(1))
                            details['qty_per_case'] = qty
                            logger.info(f"Extracted qty_per_case={qty} from product name pattern 'XB': {product_name[:50]}")
                            break
                        except:
                            pass

                    # Pattern 2: "12/10PK", "15/4PK" or "12-10PK" etc (X packs of Y)
                    match = re.search(r'(\d+)[/-](\d+)PK', product_name, re.IGNORECASE)
                    if match:
                        try:
                            qty = int(match.group(1)) * int(match.group(2))
                            details['qty_per_case'] = qty
                            logger.info(f"Extracted qty_per_case={qty} from product name pattern 'X/YPK': {product_name[:50]}")
                            break
                        except:
                            pass

            # Extract deals as structured data
            deals = self._extract_deals(page)
            if deals:
                details['deals'] = deals

            # Extract product description/details
            desc_section = page.query_selector('.m-product-overview__description')
            if desc_section:
                desc_text = desc_section.inner_text().strip()
                details['product_details'] = desc_text[:1000] if len(desc_text) > 1000 else desc_text

        except Exception as e:
            logger.error(f"Error extracting product details from {product_url}: {str(e)}")

        return details

    def _extract_deals(self, page: Page) -> List[Dict]:
        """
        Extract structured deal information from product page.

        Args:
            page: Playwright page object

        Returns:
            List of deal dictionaries with parsed fields
        """
        import json
        import re

        deals = []

        try:
            # Find all deal forms (they contain deal data as JSON in hidden inputs)
            deal_forms = page.query_selector_all('form[action*="/cart/add/deal"]')

            for form in deal_forms:
                try:
                    # Get the deal JSON from hidden input
                    deal_input = form.query_selector('input[name="deal"]')
                    if not deal_input:
                        continue

                    deal_json_str = deal_input.get_attribute('value')
                    if not deal_json_str:
                        continue

                    # Parse the JSON
                    deal_data = json.loads(deal_json_str)

                    # Determine action type (Add or Build button)
                    action_button = form.query_selector('button[type="submit"]')
                    action_type = None
                    if action_button:
                        button_text = action_button.inner_text().strip()
                        if 'Add' in button_text:
                            action_type = 'Add'
                        elif 'Build' in button_text:
                            action_type = 'Build'

                    # Parse price values (remove $ and convert to float)
                    def parse_price(price_str):
                        if not price_str:
                            return None
                        # Remove $ and commas, convert to float
                        cleaned = price_str.replace('$', '').replace(',', '').strip()
                        try:
                            return float(cleaned)
                        except:
                            return None

                    # Extract and map fields
                    deal = {
                        'deal_title': deal_data.get('dealDescription'),
                        'deal_number': deal_data.get('dealCode'),
                        'sku_number': deal_data.get('productId'),
                        'usage_limit': deal_data.get('useTimes'),
                        'quantity_type': 'Mix and Match' if deal_data.get('mixNMatch') else 'Exact Qty Only',
                        'bottle_fees_applicable': None,  # Not found in JSON
                        'quantity': deal_data.get('purchaseQty'),
                        'quantity_unit': deal_data.get('purchaseUom'),
                        'estimated_bottle_price': parse_price(deal_data.get('estBottlePrice')),
                        'cse_price': parse_price(deal_data.get('casePrice')),
                        'total_estimated_price': None,  # Calculate if needed
                        'total_cse_price': None,  # Calculate if needed
                        'action_type': action_type,
                        'discount_per_unit': deal_data.get('discount'),
                        'is_mix_and_match': 1 if deal_data.get('mixNMatch') else 0,
                        'deal_obj_type': deal_data.get('dealObj')
                    }

                    # Calculate totals if we have the data
                    if deal['quantity'] and deal['estimated_bottle_price']:
                        # Assuming quantity is in cases and we need to know bottles per case
                        # For now, just use the case price as total
                        deal['total_cse_price'] = deal['cse_price']

                    deals.append(deal)

                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse deal JSON: {str(e)}")
                    continue
                except Exception as e:
                    logger.warning(f"Error extracting deal: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting deals: {str(e)}")

        return deals
