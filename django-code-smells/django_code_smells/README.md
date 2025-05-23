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

---

## Advanced Performance Scenarios & Django Admin

The examples have been expanded to cover more complex N+1 scenarios and common performance pitfalls within the Django Admin interface.

### Enhanced Models for Detailed Examples

The models in `examples_app/models.py` have been enhanced:
-   **`Publisher` model**: A new model linked to `Book` via a `ForeignKey`.
-   **`Tag` model**: A new model linked to `Book` via a `ManyToManyField`.
-   **`Author` model**: Extended with `email` and `bio` fields.
-   **`Book` model**: Extended with a `publisher` ForeignKey, `tags` ManyToManyField, `isbn`, and `pages`. It also includes methods like `get_author_bio_preview()` and `get_tag_names()` which are used in admin examples.

These richer models allow for more realistic demonstrations of complex queries and admin performance issues.

### N+1 Queries Across Different Files/Classes

A common challenge is identifying N+1 queries when the problematic database access is hidden in utility functions or methods in different classes/files.

-   **`examples_app/utils.py`**: Contains functions like `get_book_publisher_name(book_id)` and `get_book_tags_as_string(book_id)`. These functions fetch details for a single book, including related objects (publisher, tags).
-   **`examples_app/query_examples.py`**: Functions like `get_all_book_publisher_names_service_level_n_plus_one()` and `get_all_book_tags_service_level_n_plus_one()` demonstrate this issue. They loop through a queryset of books and call these utility functions for each book. If the utility functions internally re-fetch the book or its related objects without prior prefetching, N+1 queries occur.
-   The `query_examples.py` file also includes conceptual "optimized" versions (e.g., `get_all_book_publisher_names_optimized`) that illustrate how prefetching (`select_related`, `prefetch_related`) in the calling code is crucial. For these optimizations to be effective, the utility functions would typically need to be refactored to work with model instances and their already-fetched related data, rather than re-querying by ID.

### Django Admin Performance Examples

The `examples_app/admin.py` file now includes demonstrations of common performance issues encountered in the Django Admin:

1.  **Slow Counts in Admin List View**:
    -   Methods like `total_published_books` in `PublisherAdmin` and `number_of_books_with_tag` in `TagAdmin` are added to `list_display`.
    -   These methods typically perform a `.count()` on a related manager (e.g., `publisher.books.count()`).
    -   When the admin list page for Publishers or Tags is rendered, these methods are called for *each item* in the list, resulting in numerous separate count queries (an N+1 problem for counts). This can be very slow for lists with many items or if the count queries themselves are complex.
    -   The `admin.py` file includes comments on how this can be optimized by annotating the count in the `ModelAdmin`'s `get_queryset` method.

2.  **Slow Property Rendering from Related Objects**:
    -   The `BookAdmin`'s `list_display` now includes `display_author_bio_preview` and `display_tag_names`. These call methods on the `Book` model (`get_author_bio_preview()` and `get_tag_names()`).
    -   `get_author_bio_preview()` accesses `book.author.bio`. If `author` is not fetched using `select_related` in the admin's queryset, each book row will trigger an extra query for its author's details.
    -   `get_tag_names()` accesses `book.tags.all()`. If `tags` are not fetched using `prefetch_related`, each book row will trigger extra queries for its tags.
    -   This demonstrates how seemingly simple display methods can hide N+1 queries, significantly slowing down admin page loads.
    -   The `admin.py` includes comments on optimizing this with `select_related` and `prefetch_related` in `get_queryset`.

These examples aim to provide a clearer understanding of how to identify and address these subtle but impactful performance bottlenecks.
