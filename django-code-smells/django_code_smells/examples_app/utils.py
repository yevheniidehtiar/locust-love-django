# examples_app/utils.py
from .models import Book

def get_book_publisher_name(book_id):
    """
    Fetches a book and returns its publisher's name.
    If called repeatedly for different books without prefetching
    the publisher, this can contribute to an N+1 problem.
    """
    try:
        book = Book.objects.get(id=book_id)
        if book.publisher:
            return book.publisher.name
        return "Publisher not available"
    except Book.DoesNotExist:
        return "Book not found"

def get_book_tags_as_string(book_id):
    """
    Fetches a book and returns a comma-separated string of its tag names.
    Accessing book.tags.all() can cause extra queries if not handled carefully,
    especially if this function is called per book in a list.
    """
    try:
        book = Book.objects.get(id=book_id)
        # This .tags.all() and then iterating it by list comprehension for names
        # is a classic M2M N+1 source if not prefetched.
        return ", ".join([tag.name for tag in book.tags.all()])
    except Book.DoesNotExist:
        return "Book not found"
