FROM python:3.11-slim

LABEL maintainer="asutoshsabat91"
LABEL description="CampusGenie Backend - RAG-based campus document AI"

WORKDIR /app

# System dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    gcc \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --retries=10 -r requirements.txt

# Copy app code
COPY app/ ./app/

# Create uploads directory
RUN mkdir -p /app/uploads

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
