# syntax=docker/dockerfile:1

# Setting Up operating system and Python
FROM python:3.9-alpine

# Set current working directory
WORKDIR /api

# Copy all the required pip packages and install
COPY requirement.txt requirement.txt
RUN pip3 install -r requirement.txt

# Copy all the file into current working directory of the container
COPY . .

## Run django
# Initialize database
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
# Run server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]