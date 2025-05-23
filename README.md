# Django SQL Profiler Middleware

`Django SQL Profiler Middleware` is a Django middleware that leverages `django-debug-toolbar` to analyze SQL queries in your Django application. It helps identify N+1 query issues and slow queries by logging stack traces and including related UUIDs in HTTP headers. This project also includes Locust tests for performance testing.

## Features

- Identifies and logs N+1 queries and slow SQL queries.
- Logs stack traces with UUIDs for easy traceability.
- Adds HTTP headers with query information and UUIDs for reference.
- Provides a Locust test script to simulate user behavior and monitor performance.
- Easy integration with any Django project.


## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/django-sql-profiler-middleware.git
    cd django-sql-profiler-middleware
    ```

2. **Install dependencies**:

    Install the necessary Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

    Ensure `django-debug-toolbar` and `locust` are included in your `requirements.txt`.

3. **Add Middleware to Django Settings**:

    Add the middleware to your Django `settings.py`:

    ```python
    MIDDLEWARE = [
        ...
        'my_django_app.middleware.DjtbSQLProfileHttpHeaderMiddleware',
        ...
    ]
    ```

## Usage

### Running the Django Application

1. **Run the Django development server**:

    ```bash
    python manage.py runserver
    ```

2. **Access the application** in your web browser at `http://localhost:8000`.

### Running Locust for Performance Testing

1. **Run Locust**:

    Navigate to the `locust_tests` folder and run Locust:

    ```bash
    locust -f locust_tests/locustfile.py
    ```

2. **Open the Locust web interface**:

    Visit `http://localhost:8089` to start the performance tests and monitor the results.

### Logging and Monitoring

- **Stack Traces**:
  - Stack traces are logged with UUIDs for N+1 and slow queries.
  - Logs are stored in the file specified in your Django logging configuration (`settings.py`).

- **HTTP Headers**:
  - HTTP responses include headers such as `DJ_TB_SQL_NPLUS1_1`, `DJ_TB_SQL_SLOW_1`, etc., containing SQL query information and UUIDs.

## Locust Test

The Locust test script simulates user behavior by making requests to the Django application. It parses the custom HTTP headers, logs relevant information, and helps identify SQL performance issues.

## Configuration

### Logging

Ensure your logging configuration in `settings.py` is set up to capture SQL profiling logs:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django_sql_debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


# Future Enhancements
django-code-smell: A placeholder folder for future enhancements, where we will add code-smell detection and analysis tools to further improve the quality and performance of the Django application.
# License
This project is licensed under the MIT License. See the LICENSE file for details.

# Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or feature requests.

# Contact
For any questions or support, please contact [yevhenii.dehtiar@gmail.com].