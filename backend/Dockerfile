FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r /app/requirements.txt

# Copy backend source
COPY . /app

# Create uploads and configs directories and make them writable
RUN mkdir -p /app/uploads /app/configs

ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5174

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5174"]
