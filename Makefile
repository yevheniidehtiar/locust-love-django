# Makefile for locust-love-django project

.PHONY: help setup install dev-setup test test-coverage run-django run-django-custom shell makemigrations migrate collectstatic createsuperuser run-locust docker-build docker-up docker-down docker-restart docker-logs docker-exec docker-clean docker-build-prod docker-up-prod docker-down-prod docker-restart-prod docker-logs-prod docker-exec-prod docker-clean-prod populate-data-ci populate-data-ci-prod locust-ci-run locust-ci-run-prod lint clean create-test-data-10k create-test-data-100k create-test-data-1m create-test-data-10m create-test-data-10k-ci create-test-data-100k-ci create-test-data-10k-ci-prod create-test-data-100k-ci-prod generate-data-async generate-data-async-ci generate-data-async-ci-prod

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
	@echo "  make docker-build   - Build Docker images (with mount volumes)"
	@echo "  make docker-up      - Start Docker containers (with mount volumes)"
	@echo "  make docker-down    - Stop Docker containers (with mount volumes)"
	@echo "  make docker-restart - Restart Docker containers (with mount volumes)"
	@echo "  make docker-logs    - View Docker logs (with mount volumes)"
	@echo "  make docker-exec    - Execute command in Docker container (with mount volumes)"
	@echo "  make docker-clean   - Clean up Docker resources (with mount volumes)"
	@echo "  make docker-build-prod   - Build Docker images (production mode)"
	@echo "  make docker-up-prod      - Start Docker containers (production mode)"
	@echo "  make docker-down-prod    - Stop Docker containers (production mode)"
	@echo "  make docker-restart-prod - Restart Docker containers (production mode)"
	@echo "  make docker-logs-prod    - View Docker logs (production mode)"
	@echo "  make docker-exec-prod    - Execute command in Docker container (production mode)"
	@echo "  make docker-clean-prod   - Clean up Docker resources (production mode)"
	@echo "  make populate-data-ci     - Populate database with test data (Docker with mount volumes)"
	@echo "  make populate-data-ci-prod - Populate database with test data (Docker production mode)"
	@echo "  make create-test-data-10k  - Generate 10K test data (local)"
	@echo "  make create-test-data-100k - Generate 100K test data (local)"
	@echo "  make create-test-data-1m   - Generate 1M test data (local)"
	@echo "  make create-test-data-10m  - Generate 10M test data (local)"
	@echo "  make create-test-data-10k-ci - Generate 10K test data (Docker with mount volumes)"
	@echo "  make create-test-data-100k-ci - Generate 100K test data (Docker with mount volumes)"
	@echo "  make create-test-data-10k-ci-prod - Generate 10K test data (Docker production mode)"
	@echo "  make create-test-data-100k-ci-prod - Generate 100K test data (Docker production mode)"
	@echo "  make generate-data-async   - Run custom async data generation (local)"
	@echo "  make generate-data-async-ci - Run custom async data generation (Docker with mount volumes)"
	@echo "  make generate-data-async-ci-prod - Run custom async data generation (Docker production mode)"
	@echo "  make locust-ci-run        - Run Locust CI tests (Docker with mount volumes)"
	@echo "  make locust-ci-run-prod   - Run Locust CI tests (Docker production mode)"
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

# Create test data (local)
create-test-data-10k:
	@echo "Generating 10K test data (local)..."
	cd django-code-smells/django_code_smells && python manage.py generate_data_async --tasks "generate_simple_data --authors=10000 --books-per-author=10" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=10000" "generate_complex_data --departments=100 --employees-per-dept=100"

create-test-data-100k:
	@echo "Generating 100K test data (local)..."
	cd django-code-smells/django_code_smells && python manage.py generate_data_async --tasks "generate_simple_data --authors=100000 --books-per-author=100" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=100000" "generate_complex_data --departments=100 --employees-per-dept=1000"

create-test-data-1m:
	@echo "Generating 1M test data (local)..."
	cd django-code-smells/django_code_smells && python manage.py generate_data_async --tasks "generate_simple_data --authors=1000000 --books-per-author=100" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=1000000" "generate_complex_data --departments=100 --employees-per-dept=10000"

create-test-data-10m:
	@echo "Generating 10M test data (local)..."
	cd django-code-smells/django_code_smells && python manage.py generate_data_async --tasks "generate_simple_data --authors=10000000 --books-per-author=100" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=10000000" "generate_complex_data --departments=1000 --employees-per-dept=100000"

# Create test data (Docker with mount volumes)
create-test-data-10k-ci:
	@echo "Generating 10K test data (Docker with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml exec django python manage.py generate_data_async --tasks "generate_simple_data --authors=10 --books-per-author=1000" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=10000" "generate_complex_data --departments=100 --employees-per-dept=100"

create-test-data-100k-ci:
	@echo "Generating 100K test data (Docker with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml exec django python manage.py generate_data_async --tasks "generate_simple_data --authors=100 --books-per-author=1000" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=100000" "generate_complex_data --departments=100 --employees-per-dept=1000"

# Create test data (Docker production mode)
create-test-data-10k-ci-prod:
	@echo "Generating 10K test data (Docker production mode)..."
	docker compose exec django python manage.py generate_data_async --tasks "generate_simple_data --authors=10000 --books-per-author=10" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=10000" "generate_complex_data --departments=100 --employees-per-dept=100"

create-test-data-100k-ci-prod:
	@echo "Generating 100K test data (Docker production mode)..."
	docker compose exec django python manage.py generate_data_async --tasks "generate_simple_data --authors=100000 --books-per-author=100" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=100000" "generate_complex_data --departments=100 --employees-per-dept=1000"

# Run custom async data generation (local)
# Usage: make generate-data-async TASKS="task1 task2 ..."
# Example: make generate-data-async TASKS="\"generate_simple_data --authors=1000\" \"generate_complex_data --departments=50\""
generate-data-async:
	@echo "Running async data generation with custom tasks (local)..."
	@if [ -z "$(TASKS)" ]; then echo "Error: TASKS is required"; exit 1; fi
	cd django-code-smells/django_code_smells && python manage.py generate_data_async --tasks $(TASKS)

# Run custom async data generation (Docker with mount volumes)
# Usage: make generate-data-async-ci TASKS="task1 task2 ..."
# Example: make generate-data-async-ci TASKS="\"generate_simple_data --authors=1000\" \"generate_complex_data --departments=50\""
generate-data-async-ci:
	@echo "Running async data generation with custom tasks (Docker with mount volumes)..."
	@if [ -z "$(TASKS)" ]; then echo "Error: TASKS is required"; exit 1; fi
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml exec django python manage.py generate_data_async --tasks $(TASKS)

# Run custom async data generation (Docker production mode)
# Usage: make generate-data-async-ci-prod TASKS="task1 task2 ..."
# Example: make generate-data-async-ci-prod TASKS="\"generate_simple_data --authors=1000\" \"generate_complex_data --departments=50\""
generate-data-async-ci-prod:
	@echo "Running async data generation with custom tasks (Docker production mode)..."
	@if [ -z "$(TASKS)" ]; then echo "Error: TASKS is required"; exit 1; fi
	docker compose exec django python manage.py generate_data_async --tasks $(TASKS)


# Run Locust load testing
run-locust:
	@echo "Running Locust load testing..."
	cd locust && locust --host=http://localhost:8000

populate-data-ci:
	@echo "Populating database with test data..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml exec django python manage.py populate_test_data

populate-data-ci-prod:
	@echo "Populating database with test data (production mode)..."
	docker compose exec django python manage.py populate_test_data

locust-ci-run:
	@echo "Running Locust CI tests..."
	$(MAKE) populate-data-ci
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml exec locust locust --host=http://django:8000 --headless -u 5 -r 2 -t 15s --json --exit-code-on-error 1 > locust_output.log 2>&1

locust-ci-verify:
	@echo "Verifying Locust tests output..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml exec locust python -m validate_locust_output locust_output.log

locust-ci-run-prod:
	@echo "Running Locust CI tests (production mode)..."
	$(MAKE) populate-data-ci-prod
	docker compose exec locust locust --host=http://django:8000 --headless -u 10 -r 1 -t 30s --json --exit-code-on-error 1 > locust_output_prod.log 2>&1
	@echo "Locust tests and validation completed successfully (production mode)."

# Docker commands (default - with mount volumes for development)
docker-build:
	@echo "Building Docker images (with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml build

docker-up:
	@echo "Starting Docker containers (with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml up -d

docker-down:
	@echo "Stopping Docker containers (with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml down

docker-restart:
	@echo "Restarting Docker containers (with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml restart

docker-logs:
	@echo "Viewing Docker logs (with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml logs -f

docker-exec:
	@echo "Executing command in Docker container (with mount volumes)..."
	@echo "Usage: make docker-exec SERVICE=<service> CMD=<command>"
	@if [ -z "$(SERVICE)" ]; then echo "Error: SERVICE is required"; exit 1; fi
	@if [ -z "$(CMD)" ]; then echo "Error: CMD is required"; exit 1; fi
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml exec $(SERVICE) $(CMD)

docker-clean:
	@echo "Cleaning up Docker resources (with mount volumes)..."
	docker compose -f docker-compose.yml -f _mount.docker-compose.yml down --volumes --remove-orphans
	docker system prune -f

# Docker commands (production mode - without mount volumes)
docker-build-prod:
	@echo "Building Docker images (production mode)..."
	docker compose build

docker-up-prod:
	@echo "Starting Docker containers (production mode)..."
	docker compose up -d

docker-down-prod:
	@echo "Stopping Docker containers (production mode)..."
	docker compose down

docker-restart-prod:
	@echo "Restarting Docker containers (production mode)..."
	docker compose restart

docker-logs-prod:
	@echo "Viewing Docker logs (production mode)..."
	docker compose logs -f

docker-exec-prod:
	@echo "Executing command in Docker container (production mode)..."
	@echo "Usage: make docker-exec-prod SERVICE=<service> CMD=<command>"
	@if [ -z "$(SERVICE)" ]; then echo "Error: SERVICE is required"; exit 1; fi
	@if [ -z "$(CMD)" ]; then echo "Error: CMD is required"; exit 1; fi
	docker compose exec $(SERVICE) $(CMD)

docker-clean-prod:
	@echo "Cleaning up Docker resources (production mode)..."
	docker compose down --volumes --remove-orphans
	docker system prune -f

# Linting
lint:
	@echo "Running linting checks..."
	ruff check .

fix:
	@echo "Running linting and formatting fixes..."
	ruff check . --fix && ruff format .

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
