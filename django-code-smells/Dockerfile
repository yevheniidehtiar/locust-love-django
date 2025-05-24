FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip
COPY django-code-smells/django_code_smells/requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project
COPY django-code-smells/django_code_smells /app/

# Install HTTP header profiling middleware
COPY http_header_profiling_middleware /app/http_header_profiling_middleware
RUN pip install -e /app/http_header_profiling_middleware

# Run migrations and create superuser
RUN python manage.py makemigrations examples_app
RUN python manage.py migrate
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell

# Create sample data
RUN echo "from examples_app.models import Author, Book; \
    author1 = Author.objects.create(name='J.R.R. Tolkien'); \
    author2 = Author.objects.create(name='George R.R. Martin'); \
    Book.objects.create(title='The Hobbit', author=author1, publication_year=1937); \
    Book.objects.create(title='The Lord of the Rings', author=author1, publication_year=1954); \
    Book.objects.create(title='A Game of Thrones', author=author2, publication_year=1996)" | python manage.py shell

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
