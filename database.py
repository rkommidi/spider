import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager


class Database:
    """Handles all SQLite database operations for product price tracking."""

    def __init__(self, db_path: str = "data/products.db"):
        self.db_path = db_path
        self._ensure_database_directory()
        self._init_tables()

    def _ensure_database_directory(self):
        """Create database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_tables(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT,
                    product_id TEXT,
                    bottle_upc TEXT,
                    case_upc TEXT,
                    size TEXT,
                    qty_per_case INTEGER,
                    proof_abv TEXT,
                    container_type TEXT,
                    brand TEXT,
                    supplier TEXT,
                    country_of_origin TEXT,
                    region TEXT,
                    categories TEXT,
                    deal_summary TEXT,
                    product_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, url)
                )
            """)

            # Migrate existing table if needed
            self._migrate_products_table(cursor)

            # Price history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    UNIQUE(product_id, price, scraped_at)
                )
            """)

            # Index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_history_product_id
                ON price_history(product_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_history_scraped_at
                ON price_history(scraped_at DESC)
            """)

            # Deals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    deal_title TEXT,
                    deal_number TEXT,
                    sku_number TEXT,
                    usage_limit TEXT,
                    quantity_type TEXT,
                    bottle_fees_applicable INTEGER,
                    quantity REAL,
                    quantity_unit TEXT,
                    estimated_bottle_price REAL,
                    cse_price REAL,
                    total_estimated_price REAL,
                    total_cse_price REAL,
                    action_type TEXT,
                    discount_per_unit REAL,
                    is_mix_and_match INTEGER,
                    deal_obj_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    UNIQUE(product_id, deal_number, quantity, quantity_unit)
                )
            """)

            # Index for faster deal queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deals_product_id
                ON deals(product_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deals_deal_number
                ON deals(deal_number)
            """)

    def _migrate_products_table(self, cursor):
        """Add new columns to products table if they don't exist."""
        # Get existing columns
        cursor.execute("PRAGMA table_info(products)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Define new columns to add
        new_columns = {
            'product_id': 'TEXT',
            'bottle_upc': 'TEXT',
            'case_upc': 'TEXT',
            'size': 'TEXT',
            'qty_per_case': 'INTEGER',
            'proof_abv': 'TEXT',
            'container_type': 'TEXT',
            'brand': 'TEXT',
            'supplier': 'TEXT',
            'country_of_origin': 'TEXT',
            'region': 'TEXT',
            'categories': 'TEXT',
            'deal_summary': 'TEXT',
            'product_details': 'TEXT'
        }

        # Add missing columns
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {column_name} {column_type}")
                    logging.info(f"Added column {column_name} to products table")
                except Exception as e:
                    logging.warning(f"Could not add column {column_name}: {e}")

    def insert_product(self, name: str, url: Optional[str] = None, **kwargs) -> int:
        """
        Insert a product or return existing product ID, update if exists.

        Args:
            name: Product name
            url: Product URL (optional)
            **kwargs: Additional product fields (product_id, bottle_upc, case_upc, size,
                     qty_per_case, proof_abv, container_type, brand, supplier,
                     country_of_origin, region, categories, deal_summary, product_details)

        Returns:
            Product ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build column names and values for insert
            base_columns = ['name', 'url']
            base_values = [name, url]

            # Add additional fields from kwargs
            valid_columns = {
                'product_id', 'bottle_upc', 'case_upc', 'size', 'qty_per_case',
                'proof_abv', 'container_type', 'brand', 'supplier',
                'country_of_origin', 'region', 'categories', 'deal_summary', 'product_details'
            }

            for col in valid_columns:
                if col in kwargs and kwargs[col] is not None:
                    base_columns.append(col)
                    base_values.append(kwargs[col])

            # Create INSERT statement
            columns_str = ', '.join(base_columns)
            placeholders = ', '.join(['?' for _ in base_columns])

            # Try to insert, ignore if exists
            cursor.execute(
                f"INSERT OR IGNORE INTO products ({columns_str}) VALUES ({placeholders})",
                base_values
            )

            # Get the product ID
            cursor.execute(
                "SELECT id FROM products WHERE name = ? AND (url = ? OR (url IS NULL AND ? IS NULL))",
                (name, url, url)
            )
            result = cursor.fetchone()
            product_id = result[0] if result else None

            # Update existing product with new fields if provided
            if product_id and kwargs:
                update_parts = []
                update_values = []
                for col in valid_columns:
                    if col in kwargs and kwargs[col] is not None:
                        update_parts.append(f"{col} = ?")
                        update_values.append(kwargs[col])

                if update_parts:
                    update_values.append(product_id)
                    cursor.execute(
                        f"UPDATE products SET {', '.join(update_parts)} WHERE id = ?",
                        update_values
                    )

            return product_id

    def insert_price(self, product_id: int, price: float, scraped_at: Optional[datetime] = None) -> bool:
        """
        Insert a price entry for a product.

        Args:
            product_id: Product ID
            price: Price value
            scraped_at: Timestamp (defaults to current time)

        Returns:
            True if inserted, False if duplicate
        """
        if scraped_at is None:
            scraped_at = datetime.now()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO price_history (product_id, price, scraped_at) VALUES (?, ?, ?)",
                    (product_id, price, scraped_at.isoformat())
                )
                return True
            except sqlite3.IntegrityError:
                # Duplicate entry
                return False

    def insert_deal(self, product_id: int, **deal_data) -> bool:
        """
        Insert a deal for a product.

        Args:
            product_id: Product ID
            **deal_data: Deal fields (deal_title, deal_number, sku_number, etc.)

        Returns:
            True if inserted, False if duplicate
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build column names and values
            columns = ['product_id']
            values = [product_id]

            valid_columns = {
                'deal_title', 'deal_number', 'sku_number', 'usage_limit',
                'quantity_type', 'bottle_fees_applicable', 'quantity',
                'quantity_unit', 'estimated_bottle_price', 'cse_price',
                'total_estimated_price', 'total_cse_price', 'action_type',
                'discount_per_unit', 'is_mix_and_match', 'deal_obj_type'
            }

            for col in valid_columns:
                if col in deal_data and deal_data[col] is not None:
                    columns.append(col)
                    values.append(deal_data[col])

            columns_str = ', '.join(columns)
            placeholders = ', '.join(['?' for _ in columns])

            try:
                cursor.execute(
                    f"INSERT INTO deals ({columns_str}) VALUES ({placeholders})",
                    values
                )
                return True
            except sqlite3.IntegrityError:
                # Duplicate entry
                return False

    def delete_deals_for_product(self, product_id: int) -> int:
        """
        Delete all deals for a product (for re-scraping fresh deals).

        Args:
            product_id: Product ID

        Returns:
            Number of deals deleted
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM deals WHERE product_id = ?", (product_id,))
            return cursor.rowcount

    def get_deals_for_product(self, product_id: int) -> List[Dict]:
        """
        Get all deals for a product.

        Args:
            product_id: Product ID

        Returns:
            List of deals
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM deals
                WHERE product_id = ?
                ORDER BY quantity ASC
            """
            cursor.execute(query, (product_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_products_with_latest_price(self) -> List[Dict]:
        """
        Get all products with their latest price and deal count.

        Returns:
            List of products with latest price information and deal count
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT
                    p.id,
                    p.name,
                    p.url,
                    p.product_id,
                    p.bottle_upc,
                    p.case_upc,
                    p.size,
                    p.qty_per_case,
                    p.proof_abv,
                    p.container_type,
                    p.brand,
                    p.supplier,
                    p.country_of_origin,
                    p.region,
                    p.categories,
                    p.product_details,
                    ph.price as latest_price,
                    ph.scraped_at as last_updated,
                    COALESCE(deal_counts.deal_count, 0) as deal_count
                FROM products p
                LEFT JOIN (
                    SELECT
                        product_id,
                        price,
                        scraped_at,
                        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY scraped_at DESC) as rn
                    FROM price_history
                ) ph ON p.id = ph.product_id AND ph.rn = 1
                LEFT JOIN (
                    SELECT product_id, COUNT(*) as deal_count
                    FROM deals
                    GROUP BY product_id
                ) deal_counts ON p.id = deal_counts.product_id
                ORDER BY p.name
            """

            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_price_history(self, product_id: int) -> List[Dict]:
        """
        Get full price history for a product.

        Args:
            product_id: Product ID

        Returns:
            List of price history entries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT
                    id,
                    product_id,
                    price,
                    scraped_at
                FROM price_history
                WHERE product_id = ?
                ORDER BY scraped_at DESC
            """

            cursor.execute(query, (product_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """
        Get product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product data or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_price_changes(self) -> List[Dict]:
        """
        Get products with price changes between last two scrapes.

        Returns:
            List of products with price change information
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                WITH ranked_prices AS (
                    SELECT
                        product_id,
                        price,
                        scraped_at,
                        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY scraped_at DESC) as rn
                    FROM price_history
                )
                SELECT
                    p.id,
                    p.name,
                    p.url,
                    current.price as current_price,
                    previous.price as previous_price,
                    (current.price - previous.price) as price_change,
                    current.scraped_at as last_updated
                FROM products p
                INNER JOIN ranked_prices current ON p.id = current.product_id AND current.rn = 1
                LEFT JOIN ranked_prices previous ON p.id = previous.product_id AND previous.rn = 2
                WHERE previous.price IS NOT NULL AND current.price != previous.price
                ORDER BY ABS(current.price - previous.price) DESC
            """

            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_last_scrape_time(self) -> Optional[str]:
        """
        Get the timestamp of the last scrape.

        Returns:
            ISO formatted timestamp or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(scraped_at) as last_scrape FROM price_history")
            result = cursor.fetchone()
            return result[0] if result and result[0] else None

    def get_statistics(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total products
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['total_products'] = cursor.fetchone()[0]

            # Total deals
            cursor.execute("SELECT COUNT(*) FROM deals")
            stats['total_deals'] = cursor.fetchone()[0]

            # Products with deals
            cursor.execute("SELECT COUNT(DISTINCT product_id) FROM deals")
            stats['products_with_deals'] = cursor.fetchone()[0]

            # Total price entries
            cursor.execute("SELECT COUNT(*) FROM price_history")
            stats['total_price_entries'] = cursor.fetchone()[0]

            # Products by category (top 10)
            cursor.execute("""
                SELECT
                    CASE
                        WHEN name LIKE '%Vodka%' THEN 'Vodka'
                        WHEN name LIKE '%Whiskey%' OR name LIKE '%Whisky%' OR name LIKE '%Bourbon%' OR name LIKE '%Scotch%' THEN 'Whiskey/Bourbon'
                        WHEN name LIKE '%Rum%' OR name LIKE '%Rhum%' THEN 'Rum'
                        WHEN name LIKE '%Gin%' THEN 'Gin'
                        WHEN name LIKE '%Tequila%' OR name LIKE '%Mezcal%' THEN 'Tequila/Mezcal'
                        ELSE 'Other'
                    END as spirit_type,
                    COUNT(*) as count
                FROM products
                GROUP BY spirit_type
                ORDER BY count DESC
            """)
            stats['by_spirit_type'] = [dict(row) for row in cursor.fetchall()]

            # Average deals per product
            if stats['total_products'] > 0:
                stats['avg_deals_per_product'] = round(stats['total_deals'] / stats['products_with_deals'], 1) if stats['products_with_deals'] > 0 else 0
            else:
                stats['avg_deals_per_product'] = 0

            return stats
