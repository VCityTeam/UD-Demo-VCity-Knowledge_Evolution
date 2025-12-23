FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts - use underscores for proper Python module imports
COPY fetch_forecast.py .
COPY json_to_rdf.py .
COPY upload_trig.py .
COPY server.py .

RUN mkdir -p weather-data

# MODE can be "batch" (default) or "server"
ENV MODE=batch
ENV PORT=5000

# Use entrypoint script to handle different modes
CMD ["sh", "-c", "if [ \"$MODE\" = \"server\" ]; then python server.py; else python fetch_forecast.py && python json_to_rdf.py && python upload_trig.py; fi"]
