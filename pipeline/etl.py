"""This connects the whole ETL pipeline so that it can be run using one command"""
from dotenv import load_dotenv
from extract import main_extraction_process
from transform import main_transform_product_data
from load import main_load
# from email import check_and_notify
from connect_to_database import configure_logging


def main_etl() -> None:
    """This connects the extract, transform, load and email scripts to form the ETL pipeline."""
    load_dotenv()
    configure_logging()

    raw_products_data = main_extraction_process
    cleaned_products_data = main_transform_product_data(raw_products_data)
    main_load(cleaned_products_data)
    # check_and_notify()


if __name__ == "__main__":
    main_etl()
