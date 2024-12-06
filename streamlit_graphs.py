import os
from dotenv import load_dotenv
import pandas as pd
import altair as alt
import streamlit as st
import psycopg2

load_dotenv()


def get_connection():
    """Gets connection to the database"""
    try:
        connection = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"]
        )
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def get_cursor(conn):
    """Gets cursor to the database"""
    if conn:
        try:
            return conn.cursor()
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            return None
    return None


if __name__ == "__main__":
    print(get_connection())
