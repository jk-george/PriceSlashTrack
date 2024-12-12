FROM python:3.12

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY dashboard.py .
COPY homepage.py .
COPY dashboard_etl.py .
COPY database_connection.py .
COPY logo.png .
COPY .streamlit .

CMD ["streamlit","run","dashboard.py"]