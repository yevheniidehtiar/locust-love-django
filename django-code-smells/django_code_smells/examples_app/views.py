from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
from .query_examples import (
    get_all_books_and_authors_n_plus_one,
    get_all_books_and_authors_optimized,
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