from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
    publication_year = models.IntegerField()

    def __str__(self):
        return self.title


class Product(models.Model):
    """
    Model used to demonstrate the impact of database indexes.
    The 'sku' field is frequently queried but not indexed by default.
    """

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)  # Stock Keeping Unit, not indexed by default
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class IndexedProduct(models.Model):
    """
    Same as Product model but with an index on the 'sku' field.
    This demonstrates the performance improvement when using indexes.
    """

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, db_index=True)  # Indexed for faster lookups
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
