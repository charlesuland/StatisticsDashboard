FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r /app/requirements.txt

RUN git clone https://github.com/charlesuland/StatisticsDashboard.git
RUN mv StatisticsDashboard/backend/* /app && rm -rf StatisticsDashboard 

# Create uploads and configs directories and make them writable
RUN mkdir -p /app/uploads /app/configs

ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
