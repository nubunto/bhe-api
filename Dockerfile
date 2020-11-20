FROM tiangolo/uvicorn-gunicorn:python3.7

WORKDIR /app

COPY main.py main.py
COPY berthassigner.py berthassigner.py
COPY database.py database.py
COPY env.py env.py
COPY main.py main.py
COPY models.py models.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

