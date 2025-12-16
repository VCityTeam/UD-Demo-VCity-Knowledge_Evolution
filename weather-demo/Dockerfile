FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fetch-forecast.py .
RUN mkdir -p weather-data
CMD ["python", "fetch-forecast.py"]
