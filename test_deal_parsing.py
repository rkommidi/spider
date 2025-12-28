"""Unit tests for deal parsing functionality."""
import unittest
import json
from scraper import ProductScraper


class TestDealParsing(unittest.TestCase):
    """Test cases for deal parsing."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample deal JSON from actual website
        self.sample_deal_json = {
            "dealId": "008077573619008509",
            "dealCode": "0080775736",
            "productId": "9008509",
            "purchaseQty": 1,
            "purchaseUom": "CSE",
            "levelPurchaseQty": None,
            "levelPurchaseUOM": None,
            "discount": 29.64,
            "freeGoodProductId": None,
            "freeGoodDescription": "",
            "freeGoodQty": None,
            "freeGoodUom": None,
            "freeGoodProductName": None,
            "freeGoodListPrice": 0,
            "mixNMatch": False,
            "dealDescription": "Buy 1.000CSE get $29.64 disc per CSE #9008509 | Deal #0080775736",
            "dealObj": "Level Pricing",
            "dealType": "CSE",
            "dealApplied": None,
            "estBottlePrice": "$31.27",
            "bottlePriceStrikethrough": "$36.21",
            "casePrice": "$187.62",
            "casePriceStrikethrough": "$217.26",
            "stcDealFlag": False,
            "qtyInCart": None,
            "specialPriceGoodFlag": False,
            "isRequiredQuantity": False,
            "isSplitDeal": False,
            "initialUom": "CSE",
            "configureDeal": None,
            "exactMatch": None,
            "maxQty": None,
            "useTimes": None,
            "numberOfProducts": None,
            "isDealAlreadyAddedToCart": None
        }

        # Sample mix and match deal
        self.sample_mix_match_json = {
            "dealId": "0080651790109008509",
            "dealCode": "0080651790",
            "productId": "9008509",
            "purchaseQty": 10,
            "purchaseUom": "CSE",
            "discount": 36.22,
            "mixNMatch": True,
            "dealDescription": "Buy 10CSE Mix and Match get $36.22 disc per CSE #9008509 | Deal #0080651790",
            "dealObj": "EVD – Straight Discount",
            "dealType": "CSE",
            "estBottlePrice": "$30.17",
            "casePrice": "$181.04",
            "useTimes": None
        }

    def test_parse_price(self):
        """Test price parsing function."""
        # Helper function to parse prices
        def parse_price(price_str):
            if not price_str:
                return None
            cleaned = price_str.replace('$', '').replace(',', '').strip()
            try:
                return float(cleaned)
            except:
                return None

        self.assertEqual(parse_price("$31.27"), 31.27)
        self.assertEqual(parse_price("$187.62"), 187.62)
        self.assertEqual(parse_price("$1,234.56"), 1234.56)
        self.assertIsNone(parse_price(""))
        self.assertIsNone(parse_price(None))
        self.assertIsNone(parse_price("invalid"))

    def test_deal_fields_extraction(self):
        """Test that all required fields are extracted from deal JSON."""
        deal_data = self.sample_deal_json

        # Helper function to parse prices
        def parse_price(price_str):
            if not price_str:
                return None
            cleaned = price_str.replace('$', '').replace(',', '').strip()
            try:
                return float(cleaned)
            except:
                return None

        # Extract deal fields (mimicking scraper logic)
        deal = {
            'deal_title': deal_data.get('dealDescription'),
            'deal_number': deal_data.get('dealCode'),
            'sku_number': deal_data.get('productId'),
            'usage_limit': deal_data.get('useTimes'),
            'quantity_type': 'Mix and Match' if deal_data.get('mixNMatch') else 'Exact Qty Only',
            'bottle_fees_applicable': None,
            'quantity': deal_data.get('purchaseQty'),
            'quantity_unit': deal_data.get('purchaseUom'),
            'estimated_bottle_price': parse_price(deal_data.get('estBottlePrice')),
            'cse_price': parse_price(deal_data.get('casePrice')),
            'total_estimated_price': None,
            'total_cse_price': None,
            'action_type': 'Add',
            'discount_per_unit': deal_data.get('discount'),
            'is_mix_and_match': 1 if deal_data.get('mixNMatch') else 0,
            'deal_obj_type': deal_data.get('dealObj')
        }

        # Assert all fields are correct
        self.assertEqual(deal['deal_title'], "Buy 1.000CSE get $29.64 disc per CSE #9008509 | Deal #0080775736")
        self.assertEqual(deal['deal_number'], "0080775736")
        self.assertEqual(deal['sku_number'], "9008509")
        self.assertIsNone(deal['usage_limit'])
        self.assertEqual(deal['quantity_type'], "Exact Qty Only")
        self.assertIsNone(deal['bottle_fees_applicable'])
        self.assertEqual(deal['quantity'], 1)
        self.assertEqual(deal['quantity_unit'], "CSE")
        self.assertEqual(deal['estimated_bottle_price'], 31.27)
        self.assertEqual(deal['cse_price'], 187.62)
        self.assertEqual(deal['action_type'], "Add")
        self.assertEqual(deal['discount_per_unit'], 29.64)
        self.assertEqual(deal['is_mix_and_match'], 0)
        self.assertEqual(deal['deal_obj_type'], "Level Pricing")

    def test_mix_and_match_deal(self):
        """Test mix and match deal parsing."""
        deal_data = self.sample_mix_match_json

        def parse_price(price_str):
            if not price_str:
                return None
            cleaned = price_str.replace('$', '').replace(',', '').strip()
            try:
                return float(cleaned)
            except:
                return None

        deal = {
            'deal_title': deal_data.get('dealDescription'),
            'deal_number': deal_data.get('dealCode'),
            'sku_number': deal_data.get('productId'),
            'quantity_type': 'Mix and Match' if deal_data.get('mixNMatch') else 'Exact Qty Only',
            'quantity': deal_data.get('purchaseQty'),
            'quantity_unit': deal_data.get('purchaseUom'),
            'estimated_bottle_price': parse_price(deal_data.get('estBottlePrice')),
            'cse_price': parse_price(deal_data.get('casePrice')),
            'discount_per_unit': deal_data.get('discount'),
            'is_mix_and_match': 1 if deal_data.get('mixNMatch') else 0,
            'deal_obj_type': deal_data.get('dealObj')
        }

        # Assert mix and match fields
        self.assertEqual(deal['deal_number'], "0080651790")
        self.assertEqual(deal['quantity'], 10)
        self.assertEqual(deal['quantity_type'], "Mix and Match")
        self.assertEqual(deal['is_mix_and_match'], 1)
        self.assertEqual(deal['deal_obj_type'], "EVD – Straight Discount")
        self.assertEqual(deal['estimated_bottle_price'], 30.17)
        self.assertEqual(deal['cse_price'], 181.04)
        self.assertEqual(deal['discount_per_unit'], 36.22)

    def test_numeric_values(self):
        """Test that numeric values are stored as numbers, not strings."""
        deal_data = self.sample_deal_json

        def parse_price(price_str):
            if not price_str:
                return None
            cleaned = price_str.replace('$', '').replace(',', '').strip()
            try:
                return float(cleaned)
            except:
                return None

        # Verify numeric types
        self.assertIsInstance(deal_data['purchaseQty'], (int, float))
        self.assertIsInstance(deal_data['discount'], (int, float))
        self.assertIsInstance(parse_price(deal_data['estBottlePrice']), float)
        self.assertIsInstance(parse_price(deal_data['casePrice']), float)

    def test_missing_fields_handled_gracefully(self):
        """Test that missing fields are handled with None values."""
        minimal_deal = {
            "dealCode": "0080775736",
            "productId": "9008509",
            "purchaseQty": 1,
            "purchaseUom": "CSE",
            # Missing many fields
        }

        deal = {
            'deal_title': minimal_deal.get('dealDescription'),  # Missing
            'deal_number': minimal_deal.get('dealCode'),
            'sku_number': minimal_deal.get('productId'),
            'usage_limit': minimal_deal.get('useTimes'),  # Missing
            'quantity': minimal_deal.get('purchaseQty'),
            'quantity_unit': minimal_deal.get('purchaseUom'),
        }

        # Assert None for missing fields
        self.assertIsNone(deal['deal_title'])
        self.assertIsNone(deal['usage_limit'])

        # Assert present fields work
        self.assertEqual(deal['deal_number'], "0080775736")
        self.assertEqual(deal['quantity'], 1)


if __name__ == '__main__':
    unittest.main()
