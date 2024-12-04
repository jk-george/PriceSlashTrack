"""Processes and cleans the data extracted from extract.py"""
from datetime import datetime
import logging


def configure_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


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
                logging.error(f"""Invalid price: {
                              product['product_id']}""")
                continue

            cleaned_product_data = {
                "price": price,
                "product_id": int(product["product_id"]),
                "timestamp": datetime.now()
            }
            cleaned_data.append(cleaned_product_data)

        except (KeyError, ValueError) as e:
            logging.error(f"""Error transforming product {
                          product.get("product_id")}: {str(e)}""")
            continue

    return cleaned_data


if __name__ == "__main__":

    fake_data = [{'product_id': 8, 'original_price': '£49.99', 'discount_price': '£22.49', 'game_title': 'Cyberpunk 2077', 'website': 'https://store.steampowered.com'},
                 {'product_id': 9, 'original_price': '£10.99', 'discount_price': '£7.69', 'game_title': 'Stardew Valley', 'website': 'https://store.steampowered.com'}]

    cleaned_data = main_transform_product_data(fake_data)

    print(cleaned_data)
