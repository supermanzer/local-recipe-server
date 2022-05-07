# Set runtime conditions
FROM python:3.9
ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1

# Make directory for project 
RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt

# Install requirements
RUN apt -y update
RUN apt install -y software-properties-common
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install tesseract
RUN add-apt-repository -y ppa:alex-p/tesseract-ocr5
RUN apt install -y tesseract-ocr

CMD [ "/bin/bash", "-c", "python manage.py runserver 0.0.0.0:8000" ]
