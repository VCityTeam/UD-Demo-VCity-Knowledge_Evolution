FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fetch-forecast.py .
COPY json-to-rdf.py .
COPY upload-trig.py .
RUN mkdir -p weather-data
CMD ["sh", "-c", "python fetch-forecast.py && python json-to-rdf.py && python upload-trig.py"]
