FROM python:3.12

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY connect_to_database.py .
COPY email_notifier.py .
COPY extract.py .
COPY transform.py .
COPY load.py .
COPY etl.py .

CMD ["python3","etl.py"]

# docker build -t price_slash_test -f etl.dockerfile .
# docker run -p 5432:5432 --env-file .env price_slash_test