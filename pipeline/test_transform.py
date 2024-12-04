import unittest
from datetime import datetime
from transform import clean_price, main_transform_product_data


def test_clean_price_valid():
    """Tests valid prices convert to floats"""
    assert clean_price("£22.49") == 22.49
    assert clean_price("£1,234.56") == 1234.56
    assert clean_price("£0.00") == 0.0


def test_clean_price_invalid():
    """Tests invalid prices returns None"""
    assert clean_price("sdfa") is None
    assert clean_price("£-10.00") is None
    assert clean_price("") is None


def test_transform_product_data():
    """Tests data is valid"""

    test_data = [
        {"product_id": 1, "discount_price": "£22.49", "game_title": "Test Game"}
    ]
    result = main_transform_product_data(test_data)
    assert result[0]["product_id"] == 1
    assert result[0]["price"] == 22.49
    assert isinstance(result[0]["timestamp"], datetime)


def test_transform_invalid_data():
    """Tests invalid and missing data"""
    invalid_data = [
        {'product_id': 1},
        {'product_id': 2, 'discount_price': ''},
        {'discount_price': '£22.49'}
    ]

    result = main_transform_product_data(invalid_data)
    assert len(result) == 0
