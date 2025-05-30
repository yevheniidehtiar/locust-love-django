from django.utils import timezone
import factory
import random
from datetime import timedelta
from .models import Author, Book, Product, IndexedProduct
from .complex_models import (
    Department,
    Employee,
    Project,
    ProjectAssignment,
    Document,
    Task,
)


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Faker("name")


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker("sentence", nb_words=4)
    author = factory.SubFactory(AuthorFactory)
    publication_year = factory.LazyFunction(lambda: random.randint(1900, 2023))


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("sentence", nb_words=3)
    sku = factory.Sequence(lambda n: f"SKU-{n:08d}")
    price = factory.LazyFunction(lambda: random.uniform(10.0, 1000.0))
    description = factory.Faker("paragraph")


class IndexedProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IndexedProduct

    name = factory.Faker("sentence", nb_words=3)
    sku = factory.Sequence(lambda n: f"SKU-{n:08d}")
    price = factory.LazyFunction(lambda: random.uniform(10.0, 1000.0))
    description = factory.Faker("paragraph")


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Faker("company")
    code = factory.Sequence(lambda n: f"DEPT-{n:03d}")
    description = factory.Faker("paragraph")


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(
        lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}@example.com"
    )
    username = factory.Sequence(
        lambda n: f"{factory.Faker('first_name').generate().lower()}.{factory.Faker('last_name').generate().lower()}.{n}"
    )
    department = factory.SubFactory(DepartmentFactory)
    # manager will be set after creation
    hire_date = factory.LazyFunction(
        lambda: timezone.now().date() - timedelta(days=random.randint(1, 3650))
    )
    salary = factory.LazyFunction(lambda: random.uniform(30000.0, 150000.0))


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Faker("sentence", nb_words=3)
    code = factory.Sequence(lambda n: f"PROJ-{n:04d}")
    description = factory.Faker("paragraph")
    start_date = factory.LazyFunction(
        lambda: timezone.now().date() - timedelta(days=random.randint(1, 365))
    )
    end_date = factory.LazyFunction(
        lambda: timezone.now().date() + timedelta(days=random.randint(1, 365))
    )
    budget = factory.LazyFunction(lambda: random.uniform(10000.0, 1000000.0))
    department = factory.SubFactory(DepartmentFactory)


class ProjectAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectAssignment

    project = factory.SubFactory(ProjectFactory)
    employee = factory.SubFactory(EmployeeFactory)
    role = factory.LazyFunction(
        lambda: random.choice(["Developer", "Designer", "Manager", "Tester", "Analyst"])
    )
    assignment_date = factory.LazyFunction(
        lambda: timezone.now().date() - timedelta(days=random.randint(1, 180))
    )
    hours_allocated = factory.LazyFunction(lambda: random.randint(10, 160))


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    title = factory.Faker("sentence", nb_words=4)
    project = factory.SubFactory(ProjectFactory)
    uploaded_by = factory.SubFactory(EmployeeFactory)
    file_type = factory.LazyFunction(
        lambda: random.choice(["PDF", "DOC", "XLS", "PPT", "TXT"])
    )
    content = factory.LazyFunction(
        lambda: bytes("Sample content for document", "utf-8")
    )
    description = factory.Faker("paragraph")


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("paragraph")
    project = factory.SubFactory(ProjectFactory)
    assigned_to = factory.SubFactory(EmployeeFactory)
    created_by = factory.SubFactory(EmployeeFactory)
    # parent_task will be set after creation for subtasks
    priority = factory.LazyFunction(
        lambda: random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    )
    status = factory.LazyFunction(
        lambda: random.choice(["TODO", "IN_PROGRESS", "REVIEW", "DONE"])
    )
    due_date = factory.LazyFunction(
        lambda: timezone.now().date() + timedelta(days=random.randint(1, 30))
    )
    estimated_hours = factory.LazyFunction(lambda: random.randint(1, 40))
