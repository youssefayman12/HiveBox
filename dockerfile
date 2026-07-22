FROM python:3.14-slim

WORKDIR /app

COPY app.py .

CMD ["python3", "app.py"]
