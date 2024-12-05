"""Processes and cleans the data extracted from extract.py"""
from datetime import datetime
import logging
from connect_to_database import configure_logging


def clean_price(price_str: str) -> float:
    """Cleans current/discount price string to float"""
    try:
        cleaned_price = float(price_str.replace(
            "£", "").replace(",", "").strip())
        return cleaned_price if cleaned_price >= 0 else None
    except ValueError:
        return None


def main_transform_product_data(products_data: list[dict]) -> list[dict]:
    """Transforms scraped raw product data into cleaned data ready to be uploaded"""
    cleaned_data = []

    for product in products_data:
        try:
            price = clean_price(product["discount_price"])
            if not price:
                logging.error("Invalid price: {%s}", product['product_id'])
                continue

            cleaned_product_data = {
                "price": price,
                "product_id": int(product["product_id"]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            cleaned_data.append(cleaned_product_data)
        except (KeyError, ValueError) as e:
            logging.error("Error transforming product %s: %s",
                          product.get("product_id"), str(e))
            continue

    return cleaned_data


if __name__ == "__main__":

    configure_logging()
    fake_data = [{'product_id': 8, 'original_price': '£49.99', 'discount_price': '£22.49', 'game_title': 'Cyberpunk 2077', 'website': 'https://store.steampowered.com'},
                 {'product_id': 9, 'original_price': '£10.99', 'discount_price': '£7.69',
                     'game_title': 'Stardew Valley', 'website': 'https://store.steampowered.com'},
                 {'product_id': 5, 'original_price': '£149.99', 'discount_price': '£129.99', 'product_name': 'Smartwatch', 'website': 'https://store.steampowered.com'}]

    new_data = main_transform_product_data(fake_data)
    print(new_data)
