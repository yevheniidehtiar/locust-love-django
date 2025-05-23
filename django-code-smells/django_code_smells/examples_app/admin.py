from django.contrib import admin
from django.db.models import Count # Import Count
from .models import Author, Book, Publisher, Tag

# Register your models here.

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'count_of_books') # Added count_of_books

    def count_of_books(self, obj):
        # This method calculates the number of books for each author.
        # If an author has many books, this is generally okay as it's per author object.
        # However, if this involved complex joins or was part of a global aggregation for EACH row, it could be slow.
        # A more direct example of a slow count is often with .count() on a large, filtered, joined queryset.
        return obj.books.count() # Uses related manager, efficient for single object.
    
    # Example of a queryset annotation that could be slow if not optimized,
    # especially if the admin tries to sort by it or if it's complex.
    # This is more about overall queryset performance than per-row count slowness.
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #         book_count_annotation=Count('books') # Example annotation
    #     )
    #     return queryset

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'total_published_books')

    def total_published_books(self, obj):
        """
        This method counts books published by this publisher.
        For a list view of publishers, this method will be called for each publisher instance.
        Each call executes a .count() query. If there are many publishers on a page,
        this results in N count queries (N+1 problem for counts).

        Example of a slow count scenario in Django Admin:
        If `obj.books` is a large related set, or if the underlying query for `obj.books.count()`
        becomes complex due to other admin list filters or model properties, this can be slow.
        Imagine if `Book` model had a complex default filter or if `Publisher` had many thousands of books.
        The count query itself, repeated N times, is the issue.
        """
        return obj.books.count() # N+1 issue: 1 count query per publisher in the list view

    # To optimize the above, one would typically annotate the count in `get_queryset`:
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #         _book_count=Count('books')
    #     )
    #     return queryset
    #
    # def total_published_books(self, obj):
    #     return obj._book_count
    # total_published_books.admin_order_field = '_book_count' # Allows sorting


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'publisher',
        'publication_year',
        'pages',
        'display_author_bio_preview',  # New: Method from model
        'display_tag_names',           # New: Method from model
    )
    list_filter = ('publication_year', 'publisher', 'tags', 'author') # Added author to filter
    search_fields = ('title', 'author__name', 'publisher__name', 'tags__name') # Added tags__name

    def display_author_bio_preview(self, obj):
        """
        Calls the get_author_bio_preview method from the Book model.
        This demonstrates a common performance issue in Django Admin:
        If `obj.author.bio` is accessed, and `author` was not part of a
        `select_related` in the admin's queryset, each row in the list
        will trigger a separate DB query to fetch the author's bio.
        This is an N+1 problem.
        """
        return obj.get_author_bio_preview()
    display_author_bio_preview.short_description = "Author Bio (Preview)"

    def display_tag_names(self, obj):
        """
        Calls the get_tag_names method from the Book model.
        This method iterates over `obj.tags.all()`. If `tags` were not
        part of a `prefetch_related` in the admin's queryset, each row
        will trigger DB queries to fetch its tags, leading to an N+1 problem,
        potentially N*M queries if not careful.
        """
        return obj.get_tag_names()
    display_tag_names.short_description = "Tags"

    # To optimize these, you would typically use select_related and prefetch_related
    # in the get_queryset method of the ModelAdmin:
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.select_related('author', 'publisher').prefetch_related('tags')
    #     return queryset

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_of_books_with_tag')

    def number_of_books_with_tag(self, obj):
        """
        Calculates the number of books associated with this tag.
        Similar to the Publisher example, this will execute a separate .count() query
        for each tag instance displayed in the admin list view, leading to N+1 queries.
        """
        return obj.books.count()

    # Optimized version using queryset annotation:
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #         _book_count=Count('books')
    #     )
    #     return queryset
    #
    # def number_of_books_with_tag(self, obj):
    #     return obj._book_count
    # number_of_books_with_tag.admin_order_field = '_book_count'
