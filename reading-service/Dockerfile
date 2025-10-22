# Use Python 3.9 slim image as base (what is slim image? -> minimum debian and python runtime, much smaller in size)
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies (need to understand --no-cache-dir thing)
RUN pip install --no-cache-dir -r requirements.txt 

# Copy application code
COPY app.py .

# Expose port 5001 (the port our Flask app runs on) (this is not port mapping, it's more of like a documentation thing)
EXPOSE 5001

# Set environment variables (to understand the first line better)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Command to run the application
CMD ["python", "app.py"]
