from rest_framework import serializers
from .models import Author, Book

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_name', 'publication_year']

# Serializers for demonstrating optimization techniques

# Unoptimized serializers - these will cause performance issues with large datasets

class UnoptimizedBookSerializer(serializers.ModelSerializer):
    # This serializer doesn't use read_only fields where appropriate
    author_name = serializers.CharField(source='author.name')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_name', 'publication_year']

class UnoptimizedAuthorSerializer(serializers.ModelSerializer):
    # This serializer uses a nested serializer without optimizing the queryset
    # This will cause N+1 queries when accessing books
    books = UnoptimizedBookSerializer(many=True, source='books.all')

    # This uses a SerializerMethodField which requires additional processing
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'book_count']

    def get_book_count(self, obj):
        # This causes an additional query for each author
        return obj.books.count()

# Optimized serializers - these use best practices for performance

class OptimizedBookSerializer(serializers.ModelSerializer):
    # Using read_only=True for fields that don't need to be updated
    author_name = serializers.ReadOnlyField(source='author.name')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'publication_year']
        # Note: We exclude 'author' field since we're only using this serializer
        # in the context of an author, so it's redundant

class OptimizedAuthorWithBooksSerializer(serializers.ModelSerializer):
    # This serializer uses a nested serializer with a prefetched queryset
    # The queryset will be prefetched in the view using prefetch_related
    books = OptimizedBookSerializer(many=True, read_only=True)

    # This uses an annotated field from the queryset instead of a method field
    # The annotation will be done in the view
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'book_count']
