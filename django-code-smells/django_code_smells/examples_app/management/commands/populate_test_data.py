from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone  # Import timezone
from examples_app.models import (
    Author,
    Book,
    Category,
    Product,
    Customer,
    Order,
    OrderItem,
)  # Corrected
from examples_app.complex_models import (
    Department,
    Employee,
    Project,
    Task,
    ProjectAssignment,
)  # Corrected, Added ProjectAssignment
from faker import Faker
import random


class Command(BaseCommand):
    help = "Populates the database with a significant amount of test data."

    def handle(self, *args, **options):
        self.faker = Faker()
        # To ensure unique fields get unique values across multiple runs if DB is not cleared
        self.faker.unique.clear()

        self.stdout.write("Deleting existing data...")
        with transaction.atomic():
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Customer.objects.all().delete()
            Product.objects.all().delete()  # Will delete from examples_app.models.Product
            Category.objects.all().delete()  # Will delete from examples_app.models.Category
            Task.objects.all().delete()
            ProjectAssignment.objects.all().delete()  # Explicitly delete ProjectAssignments
            Project.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()
            Book.objects.all().delete()
            Author.objects.all().delete()
        self.stdout.write("Existing data deleted.")

        self.stdout.write("Creating new test data...")

        # Create Authors
        self.stdout.write("Creating Authors...")
        authors_to_create = []
        for _ in range(random.randint(50, 100)):
            authors_to_create.append(Author(name=self.faker.name()))
        Author.objects.bulk_create(authors_to_create)
        author_list = list(Author.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(author_list)} Authors.")
        )

        # Create Books
        self.stdout.write("Creating Books...")
        books_to_create = []
        if not author_list:
            self.stdout.write(
                self.style.WARNING("No authors found, cannot create books.")
            )
        else:
            for _ in range(random.randint(500, 1000)):
                books_to_create.append(
                    Book(
                        title=self.faker.sentence(nb_words=random.randint(2, 6)),
                        author=random.choice(author_list),
                        publication_date=self.faker.date_this_century(),  # Uses field from models.py
                        isbn=self.faker.unique.isbn13(),
                    )
                )
            Book.objects.bulk_create(books_to_create)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {Book.objects.count()} Books."
                )
            )

        # Create Departments (from complex_models)
        self.stdout.write("Creating Departments...")
        departments_to_create = []
        for _ in range(random.randint(5, 10)):
            departments_to_create.append(
                Department(
                    name=self.faker.unique.bs().title()
                    + " Division",  # Changed for more uniqueness
                    code=self.faker.unique.bothify(text="DEPT-###??").upper(),
                    description=self.faker.bs(),
                )
            )
        Department.objects.bulk_create(departments_to_create)
        department_list = list(Department.objects.all())
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(department_list)} Departments."
            )
        )

        # Create Employees (from complex_models)
        self.stdout.write("Creating Employees...")
        employees_to_create = []
        if not department_list:
            self.stdout.write(
                self.style.WARNING("No departments found, cannot create employees.")
            )
        else:
            for _ in range(random.randint(50, 100)):
                employees_to_create.append(
                    Employee(
                        first_name=self.faker.first_name(),
                        last_name=self.faker.last_name(),
                        email=self.faker.unique.email(),
                        username=self.faker.unique.user_name(),
                        department=random.choice(department_list),
                        hire_date=self.faker.date_between(
                            start_date="-15y", end_date="today"
                        ),
                        salary=random.randint(30000, 150000),
                    )
                )
            Employee.objects.bulk_create(employees_to_create)
            employee_list = list(Employee.objects.all())
            # Assign managers
            for emp in employee_list:
                if random.random() < 0.25:  # 25% chance to have a manager
                    possible_managers = [
                        m
                        for m in employee_list
                        if m.id != emp.id and m.department == emp.department
                    ]
                    if possible_managers:
                        emp.manager = random.choice(possible_managers)
                        emp.save()  # Individual save needed for manager assignment
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(employee_list)} Employees."
                )
            )

        # Create Projects (from complex_models)
        self.stdout.write("Creating Projects...")
        projects_to_create = []
        if not department_list:
            self.stdout.write(
                self.style.WARNING(
                    "No departments found, cannot assign projects. They will be null."
                )
            )
        for _ in range(random.randint(20, 30)):
            projects_to_create.append(
                Project(
                    name=self.faker.catch_phrase()
                    + " Initiative",  # More descriptive names
                    code=self.faker.unique.bothify(text="PROJ####??").upper(),
                    description=self.faker.text(max_nb_chars=250),
                    start_date=self.faker.date_between(
                        start_date="-2y", end_date="-1m"
                    ),
                    end_date=self.faker.date_between(
                        start_date="today", end_date="+3y"
                    ),
                    budget=random.randint(20000, 1000000),
                    department=random.choice(department_list)
                    if department_list
                    else None,
                )
            )
        Project.objects.bulk_create(projects_to_create)
        project_list = list(Project.objects.all())

        if employee_list and project_list:  # Add members to projects if employees exist
            project_assignments_to_create = []
            for proj in project_list:
                # Ensure start_date is not None before using it
                assignment_start_date = (
                    proj.start_date if proj.start_date else self.faker.date_this_year()
                )
                members_count = random.randint(
                    1, min(len(employee_list), 7)
                )  # Assign 1-7 members
                members_for_project = random.sample(employee_list, members_count)
                for emp in members_for_project:
                    project_assignments_to_create.append(
                        ProjectAssignment(
                            project=proj,
                            employee=emp,
                            role=self.faker.job().title(),  # Assign a role
                            assignment_date=self.faker.date_between(
                                start_date=assignment_start_date, end_date="today"
                            ),  # Assign date
                            hours_allocated=random.randint(20, 160),  # Assign hours
                        )
                    )
            if project_assignments_to_create:
                ProjectAssignment.objects.bulk_create(project_assignments_to_create)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(project_list)} Projects and assigned members via ProjectAssignment."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping Project member assignment due to missing employees or projects."
                )
            )

        # Create Tasks (from complex_models)
        self.stdout.write("Creating Tasks...")
        tasks_to_create = []
        if not project_list or not employee_list:
            self.stdout.write(
                self.style.WARNING(
                    "No projects or employees found, cannot create tasks comprehensively."
                )
            )
        else:
            for _ in range(random.randint(200, 300)):
                tasks_to_create.append(
                    Task(
                        title=self.faker.sentence(
                            nb_words=random.randint(3, 8)
                        ),  # Use 'title' field
                        description=self.faker.text(max_nb_chars=300),
                        project=random.choice(project_list),
                        assigned_to=random.choice(
                            employee_list
                        ),  # Use 'assigned_to' field
                        created_by=random.choice(employee_list),
                        due_date=self.faker.date_between(
                            start_date="today", end_date="+1y"
                        ),
                        status=random.choice([s[0] for s in Task.STATUS_CHOICES]),
                        priority=random.choice([p[0] for p in Task.PRIORITY_CHOICES]),
                        estimated_hours=random.choice(
                            [0.5, 1, 2, 3, 4, 5, 8, 13, 21]
                        ),  # Fibonacci-ish hours
                    )
                )
            Task.objects.bulk_create(tasks_to_create)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {Task.objects.count()} Tasks."
                )
            )

        # Create Categories (from examples_app.models)
        self.stdout.write("Creating Categories...")
        categories_to_create = []
        for _ in range(random.randint(10, 20)):
            categories_to_create.append(
                Category(
                    name=self.faker.unique.bs().capitalize()
                    + " Category",  # Changed for more uniqueness
                    description=self.faker.text(max_nb_chars=100),
                )
            )
        Category.objects.bulk_create(categories_to_create)
        category_list = list(Category.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(category_list)} Categories.")
        )

        # Create Products (from examples_app.models)
        self.stdout.write("Creating Products...")
        products_to_create = []
        if not category_list:
            self.stdout.write(
                self.style.WARNING(
                    "No categories found, products will not have categories."
                )
            )

        for _ in range(random.randint(100, 200)):
            products_to_create.append(
                Product(
                    name=self.faker.catch_phrase(),  # Changed from ecommerce_name
                    sku=self.faker.unique.ean(length=13),
                    category=random.choice(category_list) if category_list else None,
                    price=round(random.uniform(1.99, 2999.99), 2),
                    description=self.faker.paragraph(nb_sentences=random.randint(2, 5)),
                    stock_quantity=random.randint(0, 500),
                )
            )
        Product.objects.bulk_create(products_to_create)
        product_list = list(Product.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(product_list)} Products.")
        )

        # Create Customers (from examples_app.models)
        self.stdout.write("Creating Customers...")
        customers_to_create = []
        for _ in range(random.randint(50, 100)):
            customers_to_create.append(
                Customer(
                    name=self.faker.name(),
                    email=self.faker.unique.email(),
                    address=self.faker.address(),
                )
            )
        Customer.objects.bulk_create(customers_to_create)
        customer_list = list(Customer.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(customer_list)} Customers.")
        )

        # Create Orders (from examples_app.models)
        self.stdout.write("Creating Orders...")
        orders_to_create = []
        if not customer_list:
            self.stdout.write(
                self.style.WARNING("No customers found, cannot create orders.")
            )
        else:
            for _ in range(random.randint(200, 300)):
                orders_to_create.append(
                    Order(
                        customer=random.choice(customer_list),
                        order_date=self.faker.date_time_between(
                            start_date="-3y",
                            end_date="now",
                            tzinfo=timezone.get_current_timezone(),
                        ),
                        status=random.choice([s[0] for s in Order.STATUS_CHOICES]),
                        # total_amount will be updated after OrderItems are created
                    )
                )
            Order.objects.bulk_create(orders_to_create)
            order_list = list(Order.objects.all())
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {len(order_list)} Orders.")
            )

            # Create OrderItems (from examples_app.models)
            self.stdout.write("Creating OrderItems...")
            order_items_to_create = []
            if not order_list:
                self.stdout.write(
                    self.style.WARNING("No orders found, cannot create order items.")
                )
            elif not product_list:
                self.stdout.write(
                    self.style.WARNING("No products found, cannot create order items.")
                )
            else:
                for order_instance in order_list:
                    for _ in range(random.randint(1, 5)):
                        chosen_product = random.choice(product_list)
                        order_items_to_create.append(
                            OrderItem(
                                order=order_instance,
                                product=chosen_product,
                                quantity=random.randint(1, 8),
                                price_at_purchase=chosen_product.price,  # Capture current price
                            )
                        )
                OrderItem.objects.bulk_create(order_items_to_create)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created {OrderItem.objects.count()} OrderItems."
                    )
                )

                self.stdout.write("Updating order totals...")
                # Manually update order totals as bulk_create bypasses OrderItem.save() which updates Order.total_amount
                for order_instance in order_list:
                    order_instance.update_total_amount()
                self.stdout.write(self.style.SUCCESS("Order totals updated."))

        self.stdout.write(
            self.style.SUCCESS("Successfully populated the database with test data.")
        )
