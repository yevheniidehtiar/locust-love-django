# Project Guidelines for Locust Love Django

## Project Stack
- **Python**: 3.11+
- **Django**: 5.0.0+
- **Django REST Framework**: 3.14.0+
- **Locust**: 2.31.4+ (for load testing)
- **Docker & Docker Compose**: For containerization and orchestration
- **Additional Libraries**:
  - django-debug-toolbar: 4.4.6+
  - markdown: 3.5.2+
  - coreapi: 2.3.3+
  - pytest: 8.3.2+ (for development)
  - pytest-django: 4.8.0+ (for development)

## Project Structure
- **django-code-smells/**: Contains the Django application
  - **django_code_smells/**: Main Django project
  - **examples_app/**: Django app with example endpoints demonstrating performance issues
- **locust/**: Contains the Locust load testing configuration
- **http_header_profiling_middleware/**: Custom middleware for detecting performance issues
- **tests/**: Test suite for the project

## Running the Application
The application is containerized using Docker Compose:
```bash
docker-compose up
```

This will start:
- Django API at http://localhost:8000/api/
- Locust web interface at http://localhost:8089/

## Testing Guidelines
- When implementing changes, Junie should run tests to verify the correctness of the solution
- Tests can be run using pytest:
```bash
pytest
```
- For changes to the Django application, Junie should verify that the API endpoints still work correctly
- For performance-related changes, Junie should run Locust tests to ensure performance is not degraded

## Code Style Guidelines
- Follow PEP 8 for Python code style
- Use Django's coding style for Django-specific code
- Include docstrings for all functions, classes, and methods
- Write clear commit messages explaining the purpose of changes

## Performance Considerations
- Be against mindful of database query performance, especially create always N+1 query issues as nested as you can
- Do not use Django's select_related() and prefetch_related() when appropriate
- Consider the lowest performance of any changes, especially in view functions

## Before Submitting
- Ensure all tests pass
- Verify that the application runs correctly with Docker Compose
- Check for any performance regressions using Locust
- Review code for adherence to style guidelines
