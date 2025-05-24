# Locust Love Django

This project demonstrates how to use Locust to load test a Django application and detect performance issues like N+1 queries and slow queries.

## Components

1. **Django Application**
   - REST API exposing Author and Book models
   - Example endpoints demonstrating N+1 queries and optimized queries
   - Custom middleware for detecting and reporting performance issues

2. **Locust**
   - Load testing tool configured to call the Django API
   - Reports performance metrics and detects issues


## Setup

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone the repository
2. Run the application with Docker Compose:

```bash
docker-compose up
```

3. Access the applications:
   - Django API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/ (username: admin, password: admin)
   - API Documentation: http://localhost:8000/docs/
   - Locust Web Interface: http://localhost:8089/

## API Endpoints

- `/api/authors/` - List and create authors
- `/api/books/` - List and create books
- `/api/examples/n-plus-one/` - Demonstrates N+1 query problem
- `/api/examples/optimized/` - Demonstrates optimized query
- `/api/examples/expensive/` - Demonstrates an expensive query

## Running Load Tests

1. Open the Locust web interface at http://localhost:8089/
2. Enter the number of users and spawn rate
3. Start the test
4. Monitor the results in the Locust web interface

## Architecture

The application is composed of two Docker containers:

1. **Django** - Runs the Django application with the REST API
2. **Locust** - Runs the Locust load testing tool

The Locust container sends requests to the Django container and collects performance metrics.

## Performance Issues Detection

The application includes a custom middleware that detects:

1. **N+1 Queries** - When a query is executed multiple times in a loop
2. **Slow Queries** - Queries that take a long time to execute

These issues are reported in the response headers and logged by Locust.

## Extending Performance Cases

See [Tasks to Extend Performance Cases Portfolio](tasks_to_extend_performance_cases.md) for a comprehensive list of planned extensions to the performance cases portfolio.
