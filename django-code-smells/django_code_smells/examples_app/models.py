from django.db import models
from django.utils import timezone


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
    publication_year = models.IntegerField(null=True)  # Made nullable for populator
    # For populator script compatibility
    publication_date = models.DateField(null=True, blank=True)
    isbn = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    Category model for products.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    """
    Model used to demonstrate the impact of database indexes.
    The 'sku' field is frequently queried but not indexed by default.
    Enhanced for e-commerce data.
    """

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, null=True, blank=True)  # Stock Keeping Unit
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class IndexedProduct(models.Model):
    """
    Same as Product model but with an index on the 'sku' field.
    This demonstrates the performance improvement when using indexes.
    """

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, db_index=True)
    category = models.ForeignKey(
        Category,
        related_name="indexed_products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Customer model.
    """

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Order model with a foreign key to Customer.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]
    customer = models.ForeignKey(
        Customer, related_name="orders", on_delete=models.CASCADE
    )
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

    def update_total_amount(self):
        total = sum(item.subtotal for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            self.save(update_fields=["total_amount"])


class OrderItem(models.Model):
    """
    OrderItem model linking Order and Product (Many-to-Many through model).
    """

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase

    def save(self, *args, **kwargs):
        if (
            self.product and self.price_at_purchase is None
        ):  # Set price only if not already set
            self.price_at_purchase = self.product.price
        super().save(*args, **kwargs)
        # Update order total after save
        if self.order:
            self.order.update_total_amount()

    def delete(self, *args, **kwargs):
        order_to_update = self.order
        super().delete(*args, **kwargs)
        if order_to_update:
            order_to_update.update_total_amount()
