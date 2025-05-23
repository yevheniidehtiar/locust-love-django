from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=150)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True) # For potentially larger text processing

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, related_name='books', on_delete=models.SET_NULL, null=True, blank=True)
    publication_year = models.IntegerField()
    isbn = models.CharField(max_length=20, blank=True, null=True)
    pages = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='books', blank=True)

    def __str__(self):
        return self.title

    # Example property that could be slow if used in admin list_display
    def get_author_bio_preview(self):
        if self.author and self.author.bio:
            return self.author.bio[:50] + "..."
        return "N/A"

    # Example property involving M2M, could be slow in admin
    def get_tag_names(self):
        return ", ".join([tag.name for tag in self.tags.all()]) # Potential N+1 in admin if tags not prefetched
