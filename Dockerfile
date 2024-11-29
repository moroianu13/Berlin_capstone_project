# Python base image
FROM python:3.10-slim

# Working directory inside the container
WORKDIR /neighborhood

# Copy only requirements first (for better caching)
COPY requirements.txt /neighborhood/

# IDependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY .. /neighborhood/

# Django default port
EXPOSE 8000

# command to run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]