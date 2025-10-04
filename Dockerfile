# Start from the specified Python version
FROM python:3.13-slim

# Install Tesseract OCR and other system dependencies
# These are necessary for pdf2image, pytesseract, and general image processing.
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-dev \
    libsqlite3-dev
    # Clean up to keep the final image size small
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install 'uv' package manager globally
RUN pip install uv

# Copy dependency files first for Docker caching
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies using uv from the locked file
RUN uv sync

# Copy the rest of the application code
COPY . .

# CRITICAL STEP 1: Initialize the SQLite database tables
# This runs the create_tables() function from database.py to create the ImportantDates table in app_data.db
RUN python database.py

# CRITICAL STEP 2: Define the command to start the FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "$PORT"]