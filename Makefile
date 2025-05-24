# Makefile for locust-love-django project

.PHONY: help setup install dev-setup test test-coverage run-django run-django-custom shell makemigrations migrate collectstatic createsuperuser run-locust docker-build docker-up docker-down docker-restart docker-logs docker-exec docker-clean lint clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make help           - Show this help message"
	@echo "  make setup          - Set up the development environment"
	@echo "  make install        - Install dependencies"
	@echo "  make dev-setup      - Install development dependencies"
	@echo "  make test           - Run tests"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make run-django     - Run Django development server"
	@echo "  make run-django-custom - Run Django with custom port and settings"
	@echo "  make shell          - Run Django shell"
	@echo "  make makemigrations - Create Django migrations"
	@echo "  make migrate        - Run Django migrations"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make run-locust     - Run Locust load testing"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Start Docker containers"
	@echo "  make docker-down    - Stop Docker containers"
	@echo "  make docker-restart - Restart Docker containers"
	@echo "  make docker-logs    - View Docker logs"
	@echo "  make docker-exec    - Execute command in Docker container"
	@echo "  make docker-clean   - Clean up Docker resources"
	@echo "  make lint           - Run linting checks"
	@echo "  make clean          - Clean up temporary files"

# Setup development environment
setup: install dev-setup

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -e .
	pip install -r django-code-smells/django_code_smells/requirements.txt
	pip install -e http_header_profiling_middleware

# Install development dependencies
dev-setup:
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/

# Run tests with coverage report
test-coverage:
	@echo "Running tests with coverage report..."
	pytest --cov=django_code_smells --cov=http_header_profiling_middleware --cov=locust tests/ --cov-report=term --cov-report=html

# Run Django development server
run-django:
	@echo "Running Django development server..."
	cd django-code-smells/django_code_smells && python manage.py runserver

# Run Django with custom port and settings
run-django-custom:
	@echo "Running Django with custom port and settings..."
	@echo "Usage: make run-django-custom PORT=<port> SETTINGS=<settings_module>"
	@if [ -z "$(PORT)" ]; then PORT=8000; fi
	@if [ -z "$(SETTINGS)" ]; then SETTINGS=django_code_smells.settings; fi
	cd django-code-smells/django_code_smells && python manage.py runserver $(PORT) --settings=$(SETTINGS)

# Run Django shell
shell:
	@echo "Running Django shell..."
	cd django-code-smells/django_code_smells && python manage.py shell

# Create Django migrations
makemigrations:
	@echo "Creating migrations..."
	cd django-code-smells/django_code_smells && python manage.py makemigrations

# Run migrations
migrate:
	@echo "Running migrations..."
	cd django-code-smells/django_code_smells && python manage.py migrate

# Collect static files
collectstatic:
	@echo "Collecting static files..."
	cd django-code-smells/django_code_smells && python manage.py collectstatic --noinput

# Create superuser
createsuperuser:
	@echo "Creating superuser..."
	cd django-code-smells/django_code_smells && python manage.py createsuperuser

# Run Locust load testing
run-locust:
	@echo "Running Locust load testing..."
	cd locust && locust --host=http://localhost:8000

# Docker commands
docker-build:
	@echo "Building Docker images..."
	docker compose build

docker-up:
	@echo "Starting Docker containers..."
	docker compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker compose down

docker-restart:
	@echo "Restarting Docker containers..."
	docker compose restart

docker-logs:
	@echo "Viewing Docker logs..."
	docker compose logs -f

docker-exec:
	@echo "Executing command in Docker container..."
	@echo "Usage: make docker-exec SERVICE=<service> CMD=<command>"
	@if [ -z "$(SERVICE)" ]; then echo "Error: SERVICE is required"; exit 1; fi
	@if [ -z "$(CMD)" ]; then echo "Error: CMD is required"; exit 1; fi
	docker compose exec $(SERVICE) $(CMD)

docker-clean:
	@echo "Cleaning up Docker resources..."
	docker compose down --volumes --remove-orphans
	docker system prune -f

# Linting
lint:
	@echo "Running linting checks..."
	flake8 django-code-smells/django_code_smells
	flake8 locust
	flake8 http_header_profiling_middleware

# Clean up temporary files
clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
