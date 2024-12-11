FROM python:3.12

COPY streamlit_requirements.txt .

RUN pip install -r streamlit_requirements.txt

COPY streamlit_graphs.py .
COPY streamlit_login.py .


CMD ["streamlit","run","streamlit_login.py"]