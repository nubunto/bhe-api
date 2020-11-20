FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY main.py main.py
COPY berthassigner.py berthassigner.py
COPY database.py database.py
COPY env.py env.py
COPY main.py main.py
COPY models.py models.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
