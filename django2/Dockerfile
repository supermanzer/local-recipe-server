# --- Development Stage: Single-Stage Build for Fast Iteration ---

# Use the full Python 3.12-bookworm image to ensure all necessary
# build tools (like compilers and headers) are available for complex
# libraries (e.g., psycopg2, numpy, opencv-python).
FROM python:3.12-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory for the application
WORKDIR /app

# --- Install System Dependencies ---
# Install libraries required for your pinned dependencies:
# - build-essential & libpq-dev for compiling psycopg2 and other packages.
# - tesseract-ocr & libtesseract-dev for pytesseract.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    libtesseract-dev \
    # Clean up to reduce layer size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
# This layer is cached well since requirements.txt changes less often than code
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the default Django development port
EXPOSE 8000

# Default command to run the development server
# This is ideal for local development with a mounted volume.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
