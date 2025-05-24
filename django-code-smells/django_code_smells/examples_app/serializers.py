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