from .models import Author, Book

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
