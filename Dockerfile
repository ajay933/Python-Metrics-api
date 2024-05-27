# Use a minimal Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
#RUN pip install Flask werkzeug gunicorn

# Copy your Python application code
COPY . .
RUN pip install -r requirements.txt

# Define environment variable for development mode (optional)
ENV FLASK_ENV=development
 # Remove or set to 'production' if needed

# Expose port for the application
EXPOSE 5000

# Use Gunicorn production server for reliability
CMD ["python3","api.py"]
