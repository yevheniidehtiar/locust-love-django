FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install locust==2.31.4

# Copy locust files
COPY locustfile.py /app/

EXPOSE 8089

# Run Locust
CMD ["locust", "--host=http://django:8000"]