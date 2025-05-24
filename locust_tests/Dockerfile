FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install locust==2.37.5

# Set Python to not buffer stdout/stderr
ENV PYTHONUNBUFFERED=1

# Copy locust files
COPY locustfile.py /app/
COPY entrypoint.sh /app/
COPY startup_logger.py /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8089

# Use our entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Run Locust
CMD ["locust", "--host=http://django:8000"]
