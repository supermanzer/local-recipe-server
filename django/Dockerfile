# ----------------------------------------------------------------------
# STAGE 1: Build Stage (Installs dependencies and compiles wheels)
# ----------------------------------------------------------------------
# Use the full base image for compilation tools (gcc, make, etc.)
FROM python:3.12-bookworm AS builder

# Set working directory and environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app

# --- System Dependencies for Complex Packages (opencv, pytesseract) ---
# Install necessary C-libraries for compiling psycopg2/Pillow, and runtime libs/tools for Tesseract/OpenCV.
# 'tesseract-ocr' is necessary for pytesseract.
# 'libpq-dev' and 'build-essential' are needed for many compilation steps.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    libtesseract-dev \
    # Clean up to keep the layer small
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies first (for better layer caching)
COPY requirements.txt /app/
RUN pip install --upgrade pip
# Install Python packages using --no-cache-dir
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/


# ----------------------------------------------------------------------
# STAGE 2: Production Stage (A lean, secure runtime environment)
# ----------------------------------------------------------------------
# Switch to the minimal 'slim' image for the final production container
FROM python:3.12-slim-bookworm AS final

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# --- Runtime System Dependencies ---
# Only install runtime shared libraries required by packages compiled in Stage 1
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    libpq5 \
    tesseract-ocr \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Security: Create and switch to a non-root user ---
RUN addgroup --system django_group && adduser --system --ingroup django_group django_user
ENV HOME=/home/django_user
WORKDIR $HOME/app

# Copy the compiled Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# Copy the installed system libraries/binaries from the builder stage
# We specifically need the tesseract binary and its data files
COPY --from=builder /usr/bin/tesseract /usr/bin/
COPY --from=builder /usr/share/tesseract-ocr /usr/share/tesseract-ocr

# Copy the application code
COPY --from=builder /app $HOME/app

# Set the ownership of the application directory to the non-root user
RUN chown -R django_user:django_group $HOME/app

# Switch to the non-root user
USER django_user

# ----------------------------------------------------------------------
# --- Command Structure: Flexible ENTRYPOINT/CMD for Dev or Prod ---
# ----------------------------------------------------------------------

# Use ENTRYPOINT to set the context for commands (runs Python scripts via Django)
# This executes before CMD, allowing us to override the command easily.
ENTRYPOINT ["/usr/local/bin/python", "manage.py"]

# Default CMD runs the production WSGI server (Gunicorn).
# Replace 'your_project.wsgi:application' with your actual WSGI path.
# This CMD is only executed if the user does not specify a different command.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project.wsgi:application"]
