from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Author, Book
from .serializers import (
    AuthorSerializer, 
    BookSerializer,
    UnoptimizedAuthorSerializer,
    OptimizedAuthorWithBooksSerializer
)
from .query_examples import (
    get_all_books_and_authors_n_plus_one,
    get_all_books_and_authors_optimized,
    get_author_stats_without_annotation,
    get_author_stats_with_annotation,
    query_product_without_index,
    query_product_with_index,
    complex_query_with_orm,
    complex_query_with_raw_sql,
    get_expensive_query_without_cache,
    get_expensive_query_with_cache,
    get_books_without_deferred_loading,
    get_books_with_defer,
    get_books_with_only
)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

@api_view(['GET'])
def n_plus_one_example(request):
    """API endpoint that demonstrates N+1 query problem"""
    author_names = get_all_books_and_authors_n_plus_one()
    return Response({"author_names": author_names})

@api_view(['GET'])
def optimized_query_example(request):
    """API endpoint that demonstrates optimized query"""
    author_names = get_all_books_and_authors_optimized()
    return Response({"author_names": author_names})

@api_view(['GET'])
def expensive_query_example(request):
    """API endpoint that demonstrates an expensive query"""
    # Create a simple expensive query for demonstration
    # This will fetch all books and perform additional operations
    books = Book.objects.all()
    result = []

    # Simulate some expensive operations
    for book in books:
        # This will trigger additional queries
        author_books = book.author.books.all()
        book_data = {
            "title": book.title,
            "author": book.author.name,
            "publication_year": book.publication_year,
            "author_other_books": [b.title for b in author_books if b.id != book.id]
        }
        result.append(book_data)

    return Response(result)

@api_view(['GET'])
def annotation_example(request):
    """
    API endpoint that demonstrates the benefits of using annotations for calculations.

    This example shows two approaches:
    1. Without annotations: Calculations are performed in Python after fetching data
    2. With annotations: Calculations are performed in the database

    The second approach is more efficient, especially with large datasets,
    as it reduces the amount of data transferred and leverages database optimizations.
    """
    # Get author statistics without using annotations (less efficient)
    without_annotation = get_author_stats_without_annotation()

    # Get author statistics using annotations (more efficient)
    with_annotation = get_author_stats_with_annotation()

    return Response({
        "without_annotation": without_annotation,
        "with_annotation": with_annotation,
        "explanation": "The 'with_annotation' approach is more efficient because it performs calculations in the database rather than in Python. This reduces the number of queries and the amount of data transferred."
    })

@api_view(['GET'])
def database_index_example(request):
    """
    API endpoint that demonstrates the performance impact of database indexes.

    This example shows two approaches:
    1. Without index: Querying a field without an index requires a full table scan
    2. With index: Querying a field with an index allows for faster lookups

    The second approach is more efficient, especially with large datasets,
    as it allows the database to quickly locate matching records without scanning the entire table.

    Note: For a real demonstration, you would need a large number of records to see a significant difference.
    """
    # Use a sample SKU pattern for the demonstration
    sku_pattern = "ABC"

    # Query products without an index (less efficient)
    without_index = query_product_without_index(sku_pattern)

    # Query products with an index (more efficient)
    with_index = query_product_with_index(sku_pattern)

    return Response({
        "without_index": {
            "results": without_index,
            "explanation": "Without an index, the database performs a full table scan to find matching products."
        },
        "with_index": {
            "results": with_index,
            "explanation": "With an index, the database can quickly locate matching products without scanning the entire table."
        },
        "general_explanation": "Database indexes improve query performance by creating a data structure that allows the database to find rows quickly without scanning the entire table. This is particularly important for large tables and frequently queried fields."
    })

@api_view(['GET'])
def raw_sql_example(request):
    """
    API endpoint that demonstrates when using raw SQL might be more efficient than the ORM.

    This example shows two approaches to a complex query:
    1. Using Django's ORM: Convenient but potentially less efficient for complex queries
    2. Using raw SQL: More control and potentially better performance for complex queries

    The raw SQL approach is often more efficient for complex queries because:
    - It executes in a single database query rather than multiple queries
    - It avoids the overhead of the ORM's query generation
    - It can use database-specific optimizations
    - It gives you full control over the exact SQL executed

    Note: For simple queries, the ORM is usually preferable for its safety and convenience.
    """
    # Set parameters for the query
    min_year = 1950
    max_year = 2020
    min_avg_year = 1980

    # Execute the query using Django's ORM
    orm_results = complex_query_with_orm(min_year, max_year, min_avg_year)

    # Execute the same query using raw SQL
    raw_sql_results = complex_query_with_raw_sql(min_year, max_year, min_avg_year)

    return Response({
        "orm_query": {
            "results": orm_results,
            "explanation": "This approach uses Django's ORM, which is convenient but requires multiple database queries and Python processing for complex operations."
        },
        "raw_sql_query": {
            "results": raw_sql_results,
            "explanation": "This approach uses raw SQL, which can execute the entire complex query in a single database operation, often resulting in better performance."
        },
        "general_explanation": "Raw SQL is typically more efficient for complex queries involving multiple joins, aggregations, or specific database features. However, it sacrifices some of the safety and convenience of the ORM, so it should be used judiciously."
    })

@api_view(['GET'])
def query_caching_example(request):
    """
    API endpoint that demonstrates the benefits of query caching.

    This example shows three scenarios:
    1. Without cache: The expensive query is executed each time
    2. With cache (first call): The query is executed and results are stored in cache
    3. With cache (subsequent call): The results are retrieved from cache, avoiding the database query

    Caching is particularly beneficial for:
    - Expensive queries that take a long time to execute
    - Queries that are called frequently but whose results don't change often
    - Reducing database load during high traffic periods
    """
    # Set parameters for the query
    min_year = 1950
    max_year = 2020
    min_avg_year = 1980

    # Execute the query without caching
    without_cache_results, without_cache_time = get_expensive_query_without_cache(
        min_year, max_year, min_avg_year
    )

    # Execute the query with caching (first call - cache miss)
    with_cache_results_first, with_cache_time_first, from_cache_first = get_expensive_query_with_cache(
        min_year, max_year, min_avg_year
    )

    # Execute the query with caching again (second call - cache hit)
    with_cache_results_second, with_cache_time_second, from_cache_second = get_expensive_query_with_cache(
        min_year, max_year, min_avg_year
    )

    return Response({
        "without_cache": {
            "results": without_cache_results,
            "execution_time": without_cache_time,
            "explanation": "Without caching, the expensive query is executed each time, which can be slow."
        },
        "with_cache_first_call": {
            "results": with_cache_results_first,
            "execution_time": with_cache_time_first,
            "from_cache": from_cache_first,
            "explanation": "On the first call with caching, the query is still executed, but the results are stored in the cache for future use."
        },
        "with_cache_second_call": {
            "results": with_cache_results_second,
            "execution_time": with_cache_time_second,
            "from_cache": from_cache_second,
            "explanation": "On subsequent calls, the results are retrieved from the cache, avoiding the expensive database query."
        },
        "general_explanation": "Caching query results can significantly improve performance by avoiding repeated database hits. This is particularly useful for expensive queries that are called frequently but whose results don't change often."
    })

@api_view(['GET'])
def deferred_loading_example(request):
    """
    API endpoint that demonstrates the benefits of deferred loading in Django.

    This example shows three approaches:
    1. Without deferred loading: All fields are loaded from the database
    2. With defer(): Specific fields are deferred (not loaded) from the database
    3. With only(): Only specific fields are loaded from the database

    Deferred loading is useful for:
    - Models with many fields, especially large text or binary fields
    - When you only need a subset of fields for a particular operation
    - Reducing the amount of data transferred from the database
    """
    # Get books without deferred loading (all fields are loaded)
    without_deferred = get_books_without_deferred_loading()

    # Get books with defer() (specific fields are not loaded)
    with_defer = get_books_with_defer()

    # Get books with only() (only specific fields are loaded)
    with_only = get_books_with_only()

    return Response({
        "without_deferred_loading": {
            "results": without_deferred,
            "explanation": "Without deferred loading, all fields are loaded from the database, which can be inefficient if you don't need all fields."
        },
        "with_defer": {
            "results": with_defer,
            "explanation": "With defer(), specific fields are not loaded from the database until accessed, which can improve performance if those fields are large or not needed."
        },
        "with_only": {
            "results": with_only,
            "explanation": "With only(), only the specified fields are loaded from the database, which can be more efficient when you only need a few fields from a model with many fields."
        },
        "general_explanation": "Deferred loading allows you to optimize database queries by loading only the fields you need. This can significantly reduce the amount of data transferred from the database and improve performance, especially for models with many fields or large text/binary fields."
    })

@api_view(['GET'])
def serializer_optimization_example(request):
    """
    API endpoint that demonstrates optimizing DRF serializers for better performance.

    This example shows two approaches:
    1. Unoptimized: Using nested serializers without optimizing the queryset
    2. Optimized: Using nested serializers with proper queryset optimization

    Serializer optimization is useful for:
    - Reducing the number of database queries (avoiding N+1 query problems)
    - Improving response times for complex nested resources
    - Reducing server load and memory usage
    - Providing a more efficient API
    """
    # Get all authors using an unoptimized approach
    # This will cause N+1 queries when accessing books and book counts
    unoptimized_authors = Author.objects.all()
    unoptimized_serializer = UnoptimizedAuthorSerializer(unoptimized_authors, many=True)

    # Get all authors using an optimized approach
    # This prefetches related books and annotates book counts in a single query
    optimized_authors = Author.objects.prefetch_related(
        'books'  # Prefetch related books to avoid N+1 queries
    ).annotate(
        book_count=Count('books')  # Annotate book count to avoid additional queries
    )
    optimized_serializer = OptimizedAuthorWithBooksSerializer(optimized_authors, many=True)

    return Response({
        "unoptimized_approach": {
            "results": unoptimized_serializer.data,
            "explanation": "The unoptimized approach causes N+1 queries: 1 query to get all authors, then N queries (one per author) to get their books, plus N more queries to count books."
        },
        "optimized_approach": {
            "results": optimized_serializer.data,
            "explanation": "The optimized approach uses prefetch_related to load all books in a single query and annotates the book count in the same query that fetches authors."
        },
        "optimization_techniques": {
            "prefetch_related": "Use prefetch_related to efficiently load related objects in a separate query, avoiding N+1 queries.",
            "select_related": "Use select_related for ForeignKey relationships to fetch related objects in the same query using a JOIN.",
            "annotations": "Use annotations to calculate values in the database rather than in Python.",
            "read_only_fields": "Use read_only=True for fields that don't need to be updated to avoid unnecessary processing.",
            "serializer_design": "Design serializers to minimize nested relationships and avoid redundant data."
        },
        "general_explanation": "Optimizing serializers is crucial for API performance, especially with nested resources. The key is to minimize database queries by using Django's queryset methods like prefetch_related, select_related, and annotate."
    })