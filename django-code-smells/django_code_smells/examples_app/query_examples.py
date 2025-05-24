from .models import Author, Book, Product, IndexedProduct
from django.db.models import Avg, Count, F, Sum, Q
from django.db import connection
from django.core.cache import cache
import time

# Setup: Assume some data exists.
# For a real scenario, you'd have a Django management command or a test setup to populate this.
# We'll define functions that *would* cause N+1 if Author and Book objects were in the database
# and queried this way.

def get_all_books_and_authors_n_plus_one():
    """
    This function demonstrates an N+1 query scenario.
    Accessing `book.author.name` for each book will trigger
    an additional database query for each book to fetch its author,
    if the authors were not prefetched.
    """
    books = Book.objects.all()  # Fetches all books (1 query)
    author_names = []
    for book in books:
        # Accessing book.author.name triggers a new query for each book
        author_names.append(book.author.name) # N additional queries
    return author_names

def get_all_books_and_authors_optimized():
    """
    This function shows the optimized version using select_related
    to avoid N+1 queries.
    """
    books = Book.objects.select_related('author').all() # Fetches all books and their authors (1 query)
    author_names = []
    for book in books:
        author_names.append(book.author.name) # No additional queries
    return author_names

def get_books_by_authors_with_many_titles_expensive_query(min_books=5):
    """
    This function demonstrates a potentially expensive query.
    It finds authors who have written at least `min_books` books
    and returns titles of those books.
    This involves a join, a count aggregation, and filtering.
    While not necessarily "expensive" with small data, on large datasets
    without proper indexing or with more complex conditions, such queries can become slow.
    """
    # This example requires Django's ORM to be executable,
    # so it's more of a conceptual example here.
    # from django.db.models import Count
    # authors_with_many_books = Author.objects.annotate(num_books=Count('books')).filter(num_books__gte=min_books)
    # book_titles = []
    # for author in authors_with_many_books:
    #     for book in author.books.all(): # Could be another N+1 if not careful, or just part of the "expensive" load
    #         book_titles.append(book.title)
    # return book_titles

    # Simplified conceptual example for non-executable context:
    # Pretend this is how you'd structure the thought process for the query.

    # Actual ORM query (requires Django setup to run)
    # from django.db.models import Count
    # books = Book.objects.filter(
    #     author__in=Author.objects.annotate(num_books=Count('books')).filter(num_books__gte=min_books)
    # ).select_related('author')
    #
    # result = []
    # for book in books:
    #    result.append(f"{book.title} by {book.author.name}")
    # return result

    # For now, let's keep this function as a placeholder for the concept
    # as running complex ORM queries without a Django environment is not feasible here.
    pass

def get_author_stats_without_annotation():
    """
    This function demonstrates calculating author statistics without using annotations.
    It performs calculations in Python, which is less efficient than doing them in the database.
    """
    authors = Author.objects.all()  # Fetch all authors (1 query)
    result = []

    for author in authors:
        # Fetch all books for this author (N additional queries, one per author)
        books = author.books.all()

        # Calculate statistics in Python
        total_books = len(books)
        if total_books > 0:
            avg_publication_year = sum(book.publication_year for book in books) / total_books
        else:
            avg_publication_year = 0

        author_data = {
            "name": author.name,
            "total_books": total_books,
            "avg_publication_year": avg_publication_year
        }
        result.append(author_data)

    return result

def get_author_stats_with_annotation():
    """
    This function demonstrates using annotations to calculate author statistics in the database.
    It's more efficient than calculating in Python because the database can optimize these operations.
    """
    # Use annotations to calculate statistics in a single query
    authors = Author.objects.annotate(
        total_books=Count('books'),
        avg_publication_year=Avg('books__publication_year')
    )

    result = []
    for author in authors:
        author_data = {
            "name": author.name,
            "total_books": author.total_books,
            "avg_publication_year": author.avg_publication_year or 0  # Handle None for authors with no books
        }
        result.append(author_data)

    return result

def query_product_without_index(sku_pattern):
    """
    This function demonstrates querying products by SKU without an index.

    Without an index, the database has to perform a full table scan to find matching products,
    which becomes increasingly inefficient as the table grows.

    Args:
        sku_pattern: A pattern to search for in the SKU field (e.g., 'ABC%')

    Returns:
        A list of matching products
    """
    # Using LIKE query which is particularly slow without an index
    products = Product.objects.filter(sku__startswith=sku_pattern)

    result = []
    for product in products:
        result.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": str(product.price)
        })

    return result

def query_product_with_index(sku_pattern):
    """
    This function demonstrates querying products by SKU with an index.

    With an index, the database can quickly locate matching products without scanning the entire table,
    which is much more efficient, especially for large tables.

    Args:
        sku_pattern: A pattern to search for in the SKU field (e.g., 'ABC%')

    Returns:
        A list of matching products
    """
    # Same query as above, but on a model with an indexed SKU field
    products = IndexedProduct.objects.filter(sku__startswith=sku_pattern)

    result = []
    for product in products:
        result.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": str(product.price)
        })

    return result

def complex_query_with_orm(min_year=1950, max_year=2020, min_avg_year=1980):
    """
    This function demonstrates a complex query using Django's ORM.

    It finds authors who have written books in a specific year range and have an average
    publication year above a certain threshold, along with the count of their books and
    their most recent publication year.

    While the ORM is convenient, for complex queries it can generate less efficient SQL
    than hand-written queries, especially for queries involving multiple aggregations,
    subqueries, or specific database features.

    Args:
        min_year: Minimum publication year to consider
        max_year: Maximum publication year to consider
        min_avg_year: Minimum average publication year threshold

    Returns:
        A list of authors with their statistics
    """
    # First, get authors who have books in the specified year range
    authors_with_books_in_range = Author.objects.filter(
        books__publication_year__gte=min_year,
        books__publication_year__lte=max_year
    ).distinct()

    # Then, for each author, calculate statistics and filter by average year
    result = []
    for author in authors_with_books_in_range:
        # Get all books for this author
        books = author.books.all()

        # Calculate statistics
        book_count = books.count()
        if book_count > 0:
            avg_year = sum(book.publication_year for book in books) / book_count
            max_year = max(book.publication_year for book in books)

            # Only include authors with average year above threshold
            if avg_year >= min_avg_year:
                result.append({
                    "author_id": author.id,
                    "author_name": author.name,
                    "book_count": book_count,
                    "avg_publication_year": avg_year,
                    "most_recent_year": max_year
                })

    return result

def complex_query_with_raw_sql(min_year=1950, max_year=2020, min_avg_year=1980):
    """
    This function demonstrates the same complex query using raw SQL.

    Raw SQL can be more efficient for complex queries because:
    1. You have full control over the exact SQL executed
    2. You can use database-specific optimizations
    3. You can avoid the overhead of the ORM's query generation
    4. You can write more efficient joins and subqueries

    Args:
        min_year: Minimum publication year to consider
        max_year: Maximum publication year to consider
        min_avg_year: Minimum average publication year threshold

    Returns:
        A list of authors with their statistics
    """
    # This raw SQL query does in a single database query what the ORM version
    # does with multiple queries
    raw_query = """
    SELECT 
        a.id AS author_id,
        a.name AS author_name,
        COUNT(b.id) AS book_count,
        AVG(b.publication_year) AS avg_publication_year,
        MAX(b.publication_year) AS most_recent_year
    FROM 
        examples_app_author a
    JOIN 
        examples_app_book b ON a.id = b.author_id
    WHERE 
        b.publication_year BETWEEN %s AND %s
    GROUP BY 
        a.id, a.name
    HAVING 
        AVG(b.publication_year) >= %s
    ORDER BY 
        avg_publication_year DESC
    """

    # Execute the raw query
    with connection.cursor() as cursor:
        cursor.execute(raw_query, [min_year, max_year, min_avg_year])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return results

def get_expensive_query_without_cache(min_year=1950, max_year=2020, min_avg_year=1980):
    """
    This function demonstrates an expensive query without caching.

    Each time this function is called, it executes the database query,
    which can be slow for complex queries or large datasets.

    Args:
        min_year: Minimum publication year to consider
        max_year: Maximum publication year to consider
        min_avg_year: Minimum average publication year threshold

    Returns:
        A tuple containing the query results and the time taken to execute the query
    """
    # Record the start time
    start_time = time.time()

    # Simulate a delay for the expensive query (in a real scenario, this would be a complex query)
    time.sleep(0.5)  # Simulate 500ms of database processing time

    # Execute the query (using the same query as in complex_query_with_orm for consistency)
    authors_with_books_in_range = Author.objects.filter(
        books__publication_year__gte=min_year,
        books__publication_year__lte=max_year
    ).distinct()

    result = []
    for author in authors_with_books_in_range:
        books = author.books.all()
        book_count = books.count()
        if book_count > 0:
            avg_year = sum(book.publication_year for book in books) / book_count
            max_year = max(book.publication_year for book in books)

            if avg_year >= min_avg_year:
                result.append({
                    "author_id": author.id,
                    "author_name": author.name,
                    "book_count": book_count,
                    "avg_publication_year": avg_year,
                    "most_recent_year": max_year
                })

    # Calculate the time taken
    execution_time = time.time() - start_time

    return result, execution_time

def get_expensive_query_with_cache(min_year=1950, max_year=2020, min_avg_year=1980, cache_timeout=60):
    """
    This function demonstrates the same expensive query with caching.

    It first checks if the results are already in the cache. If they are,
    it returns the cached results, avoiding the expensive database query.
    If not, it executes the query and stores the results in the cache for future use.

    Args:
        min_year: Minimum publication year to consider
        max_year: Maximum publication year to consider
        min_avg_year: Minimum average publication year threshold
        cache_timeout: How long to cache the results (in seconds)

    Returns:
        A tuple containing the query results, the time taken, and whether the result was from cache
    """
    # Create a cache key based on the query parameters
    cache_key = f"author_stats_{min_year}_{max_year}_{min_avg_year}"

    # Record the start time
    start_time = time.time()

    # Try to get the results from the cache
    cached_result = cache.get(cache_key)

    if cached_result is not None:
        # Cache hit - return the cached results
        execution_time = time.time() - start_time
        return cached_result, execution_time, True

    # Cache miss - execute the query
    # Simulate a delay for the expensive query
    time.sleep(0.5)  # Simulate 500ms of database processing time

    # Execute the query (same as without cache)
    authors_with_books_in_range = Author.objects.filter(
        books__publication_year__gte=min_year,
        books__publication_year__lte=max_year
    ).distinct()

    result = []
    for author in authors_with_books_in_range:
        books = author.books.all()
        book_count = books.count()
        if book_count > 0:
            avg_year = sum(book.publication_year for book in books) / book_count
            max_year = max(book.publication_year for book in books)

            if avg_year >= min_avg_year:
                result.append({
                    "author_id": author.id,
                    "author_name": author.name,
                    "book_count": book_count,
                    "avg_publication_year": avg_year,
                    "most_recent_year": max_year
                })

    # Store the results in the cache for future use
    cache.set(cache_key, result, cache_timeout)

    # Calculate the time taken
    execution_time = time.time() - start_time

    return result, execution_time, False

# To make these examples runnable, you would typically use them within a Django view,
# management command, or tests, where the Django environment is initialized.

# Example of how one might call these (conceptually):
# if __name__ == '__main__':
#   # This part requires a Django application setup to run.
#   # Initialize Django settings if running standalone (simplified, not for production)
#   # import os
#   # import django
#   # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings') # Replace 'your_project.settings'
#   # django.setup()

#   # Create some dummy data (requires Django setup)
#   # author1 = Author.objects.create(name="J.R.R. Tolkien")
#   # author2 = Author.objects.create(name="George R.R. Martin")
#   # Book.objects.create(title="The Hobbit", author=author1, publication_year=1937)
#   # Book.objects.create(title="The Lord of the Rings", author=author1, publication_year=1954)
#   # Book.objects.create(title="A Game of Thrones", author=author2, publication_year=1996)

#   print("Demonstrating N+1 query:")
#   # print(get_all_books_and_authors_n_plus_one()) # This would make DB queries

#   print("\nDemonstrating optimized query:")
#   # print(get_all_books_and_authors_optimized()) # This would make DB queries

#   print("\nDemonstrating potentially expensive query (conceptual):")
#   # print(get_books_by_authors_with_many_titles_expensive_query(min_books=1))
