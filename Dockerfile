FROM python:3.9
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

EXPOSE 8000

COPY . /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
