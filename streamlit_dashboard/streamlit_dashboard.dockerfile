FROM python:3.12

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir .streamlit

COPY dashboard.py .
COPY homepage.py .
COPY dashboard_etl.py .
COPY database_connection.py .
COPY logo.png .
COPY ./.streamlit/config.toml ./.streamlit/config.toml

CMD ["streamlit","run","dashboard.py"]