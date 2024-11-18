# Use an official Python image as the base
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY blazegraph-exporter.py .

# Display python logs
ENV PYTHONUNBUFFERED=1

CMD ["python", "blazegraph-exporter.py"]
