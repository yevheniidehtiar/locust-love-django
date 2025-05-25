# Data Generation Commands for Performance Testing

This directory contains Django management commands for generating large volumes of test data to support performance testing. These commands use factory_boy to create realistic test data with appropriate relationships between models.

## Available Commands

### 1. Generate Simple Data

This command generates data for the simple models: Author, Book, Product, and IndexedProduct.

```bash
python manage.py generate_simple_data [options]
```

#### Options:

- `--authors`: Number of authors to create (default: 1000)
- `--books-per-author`: Number of books per author (default: 5)
- `--products`: Number of products to create (default: 10000)
- `--indexed-products`: Number of indexed products to create (default: 10000)
- `--batch-size`: Batch size for bulk creation (default: 1000)
- `--skip-authors`: Skip author creation
- `--skip-books`: Skip book creation
- `--skip-products`: Skip product creation
- `--skip-indexed-products`: Skip indexed product creation

#### Examples:

Generate 10,000 authors with 10 books each:
```bash
python manage.py generate_simple_data --authors=10000 --books-per-author=10
```

Generate only products:
```bash
python manage.py generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=1000000
```

### 2. Generate Complex Data

This command generates data for the complex models: Department, Employee, Project, ProjectAssignment, Document, and Task.

```bash
python manage.py generate_complex_data [options]
```

#### Options:

- `--departments`: Number of departments to create (default: 50)
- `--employees-per-dept`: Number of employees per department (default: 100)
- `--projects-per-dept`: Number of projects per department (default: 10)
- `--assignments-per-project`: Number of assignments per project (default: 5)
- `--documents-per-project`: Number of documents per project (default: 20)
- `--tasks-per-project`: Number of tasks per project (default: 50)
- `--subtasks-ratio`: Ratio of tasks that are subtasks (default: 0.3)
- `--batch-size`: Batch size for bulk creation (default: 1000)
- `--skip-departments`: Skip department creation
- `--skip-employees`: Skip employee creation
- `--skip-projects`: Skip project creation
- `--skip-assignments`: Skip project assignment creation
- `--skip-documents`: Skip document creation
- `--skip-tasks`: Skip task creation

#### Examples:

Generate a complete dataset with default settings:
```bash
python manage.py generate_complex_data
```

Generate a large organization with 100 departments and 1000 employees per department:
```bash
python manage.py generate_complex_data --departments=100 --employees-per-dept=1000
```

Generate only tasks for existing projects:
```bash
python manage.py generate_complex_data --skip-departments --skip-employees --skip-projects --skip-assignments --skip-documents --tasks-per-project=1000
```

## Performance Considerations

When generating millions of records, consider the following:

1. **Batch Size**: Adjust the batch size based on your system's memory. Larger batch sizes can be more efficient but require more memory.

2. **Database Indexes**: Ensure your database has appropriate indexes before generating large volumes of data.

3. **Incremental Generation**: Use the skip options to generate data incrementally if needed.

4. **Database Transactions**: The commands use database transactions to ensure data integrity and improve performance.

5. **Memory Usage**: Monitor memory usage when generating very large datasets. You may need to adjust batch sizes or generate data in multiple steps.

## Example Workflow for Performance Testing

1. Generate a base dataset with reasonable defaults:
```bash
python manage.py generate_simple_data
python manage.py generate_complex_data
```

2. Run Locust tests to establish baseline performance:
```bash
locust -f locust_tests/locustfile.py
```

3. Generate additional data to test scaling:
```bash
python manage.py generate_simple_data --authors=10000 --books-per-author=20 --skip-products --skip-indexed-products
python manage.py generate_complex_data --departments=100 --employees-per-dept=500 --skip-projects --skip-assignments --skip-documents --skip-tasks
```

4. Run Locust tests again to measure performance with larger dataset.

### 3. Generate Data Asynchronously

This command allows you to run multiple data generation tasks concurrently using Django 5's async capabilities.

```bash
python manage.py generate_data_async [options]
```

#### Options:

- `--tasks`: List of data generation tasks to run asynchronously (space-separated)
- `--simple-data`: Run generate_simple_data command with default parameters
- `--complex-data`: Run generate_complex_data command with default parameters

#### Examples:

Run both simple and complex data generation with default parameters:
```bash
python manage.py generate_data_async --simple-data --complex-data
```

Run specific data generation tasks with custom parameters:
```bash
python manage.py generate_data_async --tasks "generate_simple_data --authors=1000000 --books-per-author=100" "generate_simple_data --skip-authors --skip-books --skip-indexed-products --products=1000000" "generate_complex_data"
```

Generate a large dataset with multiple concurrent tasks:
```bash
python manage.py generate_data_async --tasks "generate_simple_data --authors=10000 --books-per-author=20 --skip-products --skip-indexed-products" "generate_complex_data --departments=100 --employees-per-dept=500 --skip-projects --skip-assignments --skip-documents --skip-tasks"
```
