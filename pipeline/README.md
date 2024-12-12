## 📋 Overview

This module is responsible for extracting product information from various online shopping sites, cleaning the extracted content, and loading the final cleaned data. The extraction process involves:
1. Web scraping relevant data (product name, original and discount price etc.)
2. Transforming the data into a list of dictionaries and loading it into the RDS database.

# 🛠️ Prerequisites
- **Docker** installed.
- Setup **ECR** repository to store the ETL pipeline Docker image.

Optional:
- **Python** installed (For running locally)

## ⚙️ Setup
Create an `.env` file and fill it with the following variables:
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=<your_aws_access_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>

# Email Configuration
FROM_EMAIL=<your-verified-ses-sender-email>

# RDS Configuration
DB_USER=<database_username>
DB_PASSWORD=<database_password>
DB_NAME=<database_name>
DB_PORT=<database_port>
DB_HOST=<database_host>
```

### ☁️ Pushing to the Cloud
To deploy the overall cloud infrastructure, the ETL pipeline must be containerised and hosted on the cloud:

1. Make sure you have the Docker application running in the background.
2. Dockerise and upload the application:
```bash
bash etl_docker_push.sh
```
This will:
- Authenticate your AWS credentials with Docker.
- Create the Docker image.
- Tag the Docker image.
- Upload the tagged image to the ECR repository.

### 💻 Running Locally (MacOS, **Optional**)
The ETL pipeline can also be ran locally by:

1. Creating and activating a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
2. Installing requirements:
```bash
pip install -r requirements.txt
```
3. Running the entire process locally (extracting, cleaning, and uploading to the RDS)
```bash
python etl.py
```

## 📁 Files
- `extract.py`: This file handles the extraction of product data from (currently) Steam URLs. It uses the `BeautifulSoup` library to scrape all relevant data.
- `transform.py`: This file handles the data cleaning, namely validating prices, product IDs and timestamps.
- `load.py`: This file inserts the cleaned data into the RDS database.
- `email_notifier.py`: This script handles the email notification of users. It checks the database and notifies users when the product they have subscribed to has fallen below their chosen price threshold.
- `etl.py`: This file combines the extract, transform, load, and email processes into one script.
- `etl.dockerfile`: This file Dockerises `etl.py` so that it can be run on the cloud.

### ✅ Test Coverage
To generate a detailed test report:
```bash
pytest -vv
```
To include coverage results:
```bash
pytest --cov -vv
```