# Django Code Smells Examples

This directory contains examples of Django ORM usage that can lead to common performance issues, such as N+1 queries and expensive SQL operations.

## Purpose

The code examples here are intended to:
- Illustrate how certain ORM patterns can result in inefficient database querying.
- Provide a basis for demonstrating profiling tools that can detect these issues.
- Show optimized versions of these queries where applicable.

## Examples

The examples are located in `examples_app/query_examples.py`.

### Models

The examples use the following Django models defined in `examples_app/models.py`:

- `Author`:
    - `name`: CharField
- `Book`:
    - `title`: CharField
    - `author`: ForeignKey to `Author`
    - `publication_year`: IntegerField

### Query Scenarios

1.  **N+1 Query (`get_all_books_and_authors_n_plus_one`)**:
    - This function demonstrates a common N+1 scenario where iterating through a list of `Book` objects and accessing each `book.author.name` attribute triggers a separate database query for each book's author.

2.  **Optimized Query (`get_all_books_and_authors_optimized`)**:
    - This function shows how to avoid the N+1 problem by using `select_related('author')` to fetch all books and their associated authors in a single query.

3.  **Potentially Expensive Query (`get_books_by_authors_with_many_titles_expensive_query`)**:
    - This function is a conceptual placeholder for a query that could be expensive on large datasets. It aims to find authors who have written a minimum number of books and then list their titles. Such queries might involve joins, aggregations (like `Count`), and filtering that can be resource-intensive without proper database indexing or query optimization.

## Running these examples

The Python functions in `query_examples.py` are designed to illustrate ORM patterns. To execute them and see the actual SQL queries generated, you would typically:
1.  Ensure you have a Django project set up.
2.  Include `Author` and `Book` models in an installed app.
3.  Run migrations to create the database tables.
4.  Populate the database with some test data.
5.  Call these functions from a Django management command, a view, or within the Django shell (`python manage.py shell`).

These examples are primarily for illustrative purposes within the context of this repository, which focuses on SQL profiling middleware.
