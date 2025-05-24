from django.core.management.base import BaseCommand
from django.db import transaction
from examples_app.factories import (
    AuthorFactory,
    BookFactory,
    ProductFactory,
    IndexedProductFactory,
)
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate large volumes of data for simple models (Author, Book, Product, IndexedProduct)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--authors", type=int, default=1000, help="Number of authors to create"
        )
        parser.add_argument(
            "--books-per-author", type=int, default=5, help="Number of books per author"
        )
        parser.add_argument(
            "--products", type=int, default=10000, help="Number of products to create"
        )
        parser.add_argument(
            "--indexed-products",
            type=int,
            default=10000,
            help="Number of indexed products to create",
        )
        parser.add_argument(
            "--batch-size", type=int, default=1000, help="Batch size for bulk creation"
        )
        parser.add_argument(
            "--skip-authors", action="store_true", help="Skip author creation"
        )
        parser.add_argument(
            "--skip-books", action="store_true", help="Skip book creation"
        )
        parser.add_argument(
            "--skip-products", action="store_true", help="Skip product creation"
        )
        parser.add_argument(
            "--skip-indexed-products",
            action="store_true",
            help="Skip indexed product creation",
        )

    def handle(self, *args, **options):
        start_time = time.time()

        authors_count = options["authors"]
        books_per_author = options["books_per_author"]
        products_count = options["products"]
        indexed_products_count = options["indexed_products"]
        batch_size = options["batch_size"]

        if not options["skip_authors"]:
            self.generate_authors(authors_count, batch_size)

        if not options["skip_books"]:
            self.generate_books(books_per_author, batch_size)

        if not options["skip_products"]:
            self.generate_products(products_count, batch_size)

        if not options["skip_indexed_products"]:
            self.generate_indexed_products(indexed_products_count, batch_size)

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated data in {elapsed_time:.2f} seconds"
            )
        )

    def generate_authors(self, count, batch_size):
        """Generate authors in batches"""
        self.stdout.write(f"Generating {count} authors...")
        start_time = time.time()

        batches = count // batch_size + (1 if count % batch_size else 0)

        for i in range(batches):
            batch_count = min(batch_size, count - i * batch_size)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} authors)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                AuthorFactory.create_batch(batch_count)

            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {count} authors in {elapsed_time:.2f} seconds"
            )
        )

    def generate_books(self, books_per_author, batch_size):
        """Generate books for existing authors"""
        from examples_app.models import Author

        authors = Author.objects.all()
        author_count = authors.count()

        if author_count == 0:
            self.stdout.write(
                self.style.WARNING("No authors found. Please create authors first.")
            )
            return

        total_books = author_count * books_per_author
        self.stdout.write(
            f"Generating {books_per_author} books for each of {author_count} authors ({total_books} total)..."
        )
        start_time = time.time()

        batches = total_books // batch_size + (1 if total_books % batch_size else 0)
        books_created = 0

        for i in range(batches):
            batch_count = min(batch_size, total_books - books_created)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} books)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                for j in range(batch_count):
                    # Distribute books evenly among authors
                    author_index = (books_created + j) % author_count
                    author = authors[author_index]
                    BookFactory.create(author=author)

            books_created += batch_count
            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {books_created} books in {elapsed_time:.2f} seconds"
            )
        )

    def generate_products(self, count, batch_size):
        """Generate products in batches"""
        self.stdout.write(f"Generating {count} products...")
        start_time = time.time()

        batches = count // batch_size + (1 if count % batch_size else 0)

        for i in range(batches):
            batch_count = min(batch_size, count - i * batch_size)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} products)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                ProductFactory.create_batch(batch_count)

            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {count} products in {elapsed_time:.2f} seconds"
            )
        )

    def generate_indexed_products(self, count, batch_size):
        """Generate indexed products in batches"""
        self.stdout.write(f"Generating {count} indexed products...")
        start_time = time.time()

        batches = count // batch_size + (1 if count % batch_size else 0)

        for i in range(batches):
            batch_count = min(batch_size, count - i * batch_size)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} indexed products)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                IndexedProductFactory.create_batch(batch_count)

            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {count} indexed products in {elapsed_time:.2f} seconds"
            )
        )
