# Set runtime conditions
FROM python:3.9
ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1

# Make directory for project 
RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt

# Install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "/bin/bash", "-c", "python manage.py runserver 0.0.0.0:8000" ]
# Run command will be in docker-compose.yml
