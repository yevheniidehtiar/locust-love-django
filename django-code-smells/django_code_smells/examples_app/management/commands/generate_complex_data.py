from django.core.management.base import BaseCommand
from django.db import transaction
from examples_app.factories import (
    DepartmentFactory,
    EmployeeFactory,
    ProjectFactory,
    ProjectAssignmentFactory,
    DocumentFactory,
    TaskFactory,
)
from examples_app.complex_models import Department, Employee, Project, ProjectAssignment
import time
import random
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate large volumes of data for complex models (Department, Employee, Project, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--departments",
            type=int,
            default=50,
            help="Number of departments to create",
        )
        parser.add_argument(
            "--employees-per-dept",
            type=int,
            default=100,
            help="Number of employees per department",
        )
        parser.add_argument(
            "--projects-per-dept",
            type=int,
            default=10,
            help="Number of projects per department",
        )
        parser.add_argument(
            "--assignments-per-project",
            type=int,
            default=5,
            help="Number of assignments per project",
        )
        parser.add_argument(
            "--documents-per-project",
            type=int,
            default=20,
            help="Number of documents per project",
        )
        parser.add_argument(
            "--tasks-per-project",
            type=int,
            default=50,
            help="Number of tasks per project",
        )
        parser.add_argument(
            "--subtasks-ratio",
            type=float,
            default=0.3,
            help="Ratio of tasks that are subtasks",
        )
        parser.add_argument(
            "--batch-size", type=int, default=1000, help="Batch size for bulk creation"
        )
        parser.add_argument(
            "--skip-departments", action="store_true", help="Skip department creation"
        )
        parser.add_argument(
            "--skip-employees", action="store_true", help="Skip employee creation"
        )
        parser.add_argument(
            "--skip-projects", action="store_true", help="Skip project creation"
        )
        parser.add_argument(
            "--skip-assignments",
            action="store_true",
            help="Skip project assignment creation",
        )
        parser.add_argument(
            "--skip-documents", action="store_true", help="Skip document creation"
        )
        parser.add_argument(
            "--skip-tasks", action="store_true", help="Skip task creation"
        )

    def handle(self, *args, **options):
        start_time = time.time()

        departments_count = options["departments"]
        employees_per_dept = options["employees_per_dept"]
        projects_per_dept = options["projects_per_dept"]
        assignments_per_project = options["assignments_per_project"]
        documents_per_project = options["documents_per_project"]
        tasks_per_project = options["tasks_per_project"]
        subtasks_ratio = options["subtasks_ratio"]
        batch_size = options["batch_size"]

        if not options["skip_departments"]:
            self.generate_departments(departments_count, batch_size)

        if not options["skip_employees"]:
            self.generate_employees(employees_per_dept, batch_size)
            self.assign_managers()

        if not options["skip_projects"]:
            self.generate_projects(projects_per_dept, batch_size)

        if not options["skip_assignments"]:
            self.generate_project_assignments(assignments_per_project, batch_size)

        if not options["skip_documents"]:
            self.generate_documents(documents_per_project, batch_size)

        if not options["skip_tasks"]:
            self.generate_tasks(tasks_per_project, subtasks_ratio, batch_size)

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated complex data in {elapsed_time:.2f} seconds"
            )
        )

    def generate_departments(self, count, batch_size):
        """Generate departments in batches"""
        self.stdout.write(f"Generating {count} departments...")
        start_time = time.time()

        batches = count // batch_size + (1 if count % batch_size else 0)

        for i in range(batches):
            batch_count = min(batch_size, count - i * batch_size)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} departments)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                DepartmentFactory.create_batch(batch_count)

            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {count} departments in {elapsed_time:.2f} seconds"
            )
        )

    def generate_employees(self, employees_per_dept, batch_size):
        """Generate employees for each department"""
        departments = Department.objects.all()
        dept_count = departments.count()

        if dept_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No departments found. Please create departments first."
                )
            )
            return

        total_employees = dept_count * employees_per_dept
        self.stdout.write(
            f"Generating {employees_per_dept} employees for each of {dept_count} departments ({total_employees} total)..."
        )
        start_time = time.time()

        batches = total_employees // batch_size + (
            1 if total_employees % batch_size else 0
        )
        employees_created = 0

        for i in range(batches):
            batch_count = min(batch_size, total_employees - employees_created)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} employees)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                for j in range(batch_count):
                    # Distribute employees evenly among departments
                    dept_index = (employees_created + j) % dept_count
                    department = departments[dept_index]
                    EmployeeFactory.create(department=department)

            employees_created += batch_count
            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {employees_created} employees in {elapsed_time:.2f} seconds"
            )
        )

    def assign_managers(self):
        """Assign managers to employees"""
        self.stdout.write("Assigning managers to employees...")
        start_time = time.time()

        # Get all departments
        departments = Department.objects.all()

        for department in departments:
            self.stdout.write(
                f"  Assigning managers in department {department.name}..."
            )

            # Get all employees in this department
            employees = Employee.objects.filter(department=department)
            employee_count = employees.count()

            if employee_count == 0:
                continue

            # Select ~10% of employees as managers
            manager_count = max(1, int(employee_count * 0.1))
            potential_managers = list(employees[:manager_count])

            # Assign a top manager (no manager)
            top_manager = potential_managers[0]

            with transaction.atomic():
                # Update top manager to have no manager
                top_manager.manager = None
                top_manager.save()

                # Assign other managers to report to top manager
                for manager in potential_managers[1:]:
                    manager.manager = top_manager
                    manager.save()

                # Assign remaining employees to random managers
                for employee in employees[manager_count:]:
                    employee.manager = random.choice(potential_managers)
                    employee.save()

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f"Assigned managers in {elapsed_time:.2f} seconds")
        )

    def generate_projects(self, projects_per_dept, batch_size):
        """Generate projects for each department"""
        departments = Department.objects.all()
        dept_count = departments.count()

        if dept_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No departments found. Please create departments first."
                )
            )
            return

        total_projects = dept_count * projects_per_dept
        self.stdout.write(
            f"Generating {projects_per_dept} projects for each of {dept_count} departments ({total_projects} total)..."
        )
        start_time = time.time()

        batches = total_projects // batch_size + (
            1 if total_projects % batch_size else 0
        )
        projects_created = 0

        for i in range(batches):
            batch_count = min(batch_size, total_projects - projects_created)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} projects)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                for j in range(batch_count):
                    # Distribute projects evenly among departments
                    dept_index = (projects_created + j) % dept_count
                    department = departments[dept_index]
                    ProjectFactory.create(department=department)

            projects_created += batch_count
            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {projects_created} projects in {elapsed_time:.2f} seconds"
            )
        )

    def generate_project_assignments(self, assignments_per_project, batch_size):
        """Generate project assignments linking employees to projects"""
        projects = Project.objects.all()
        project_count = projects.count()

        if project_count == 0:
            self.stdout.write(
                self.style.WARNING("No projects found. Please create projects first.")
            )
            return

        employees = Employee.objects.all()
        employee_count = employees.count()

        if employee_count == 0:
            self.stdout.write(
                self.style.WARNING("No employees found. Please create employees first.")
            )
            return

        total_assignments = project_count * assignments_per_project
        self.stdout.write(
            f"Generating {assignments_per_project} assignments for each of {project_count} projects ({total_assignments} total)..."
        )
        start_time = time.time()

        batches = total_assignments // batch_size + (
            1 if total_assignments % batch_size else 0
        )
        assignments_created = 0

        # Convert querysets to lists for better performance in loops
        projects_list = list(projects)
        employees_list = list(employees)

        for i in range(batches):
            batch_count = min(batch_size, total_assignments - assignments_created)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} assignments)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                for j in range(batch_count):
                    # Determine which project this assignment belongs to
                    project_index = (assignments_created + j) // assignments_per_project
                    if project_index >= project_count:
                        break

                    project = projects_list[project_index]

                    # Select a random employee for this assignment
                    # Avoid creating duplicate assignments for the same project-employee-role combination
                    attempts = 0
                    max_attempts = 10
                    assignment_created = False

                    while not assignment_created and attempts < max_attempts:
                        employee = random.choice(employees_list)
                        role = random.choice(
                            ["Developer", "Designer", "Manager", "Tester", "Analyst"]
                        )

                        # Check if this assignment already exists
                        if not ProjectAssignment.objects.filter(
                            project=project, employee=employee, role=role
                        ).exists():
                            ProjectAssignmentFactory.create(
                                project=project, employee=employee, role=role
                            )
                            assignment_created = True

                        attempts += 1

                    if assignment_created:
                        assignments_created += 1

            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {assignments_created} project assignments in {elapsed_time:.2f} seconds"
            )
        )

    def generate_documents(self, documents_per_project, batch_size):
        """Generate documents for each project"""
        projects = Project.objects.all()
        project_count = projects.count()

        if project_count == 0:
            self.stdout.write(
                self.style.WARNING("No projects found. Please create projects first.")
            )
            return

        employees = Employee.objects.all()
        employee_count = employees.count()

        if employee_count == 0:
            self.stdout.write(
                self.style.WARNING("No employees found. Please create employees first.")
            )
            return

        total_documents = project_count * documents_per_project
        self.stdout.write(
            f"Generating {documents_per_project} documents for each of {project_count} projects ({total_documents} total)..."
        )
        start_time = time.time()

        batches = total_documents // batch_size + (
            1 if total_documents % batch_size else 0
        )
        documents_created = 0

        # Convert querysets to lists for better performance in loops
        projects_list = list(projects)
        employees_list = list(employees)

        for i in range(batches):
            batch_count = min(batch_size, total_documents - documents_created)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"  Generating batch {i + 1}/{batches} ({batch_count} documents)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                for j in range(batch_count):
                    # Determine which project this document belongs to
                    project_index = (documents_created + j) // documents_per_project
                    if project_index >= project_count:
                        break

                    project = projects_list[project_index]

                    # Select a random employee as the uploader
                    employee = random.choice(employees_list)

                    DocumentFactory.create(project=project, uploaded_by=employee)

                    documents_created += 1

            batch_elapsed = time.time() - batch_start
            self.stdout.write(f"  Batch completed in {batch_elapsed:.2f} seconds")

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {documents_created} documents in {elapsed_time:.2f} seconds"
            )
        )

    def generate_tasks(self, tasks_per_project, subtasks_ratio, batch_size):
        """Generate tasks for each project, including subtasks"""
        projects = Project.objects.all()
        project_count = projects.count()

        if project_count == 0:
            self.stdout.write(
                self.style.WARNING("No projects found. Please create projects first.")
            )
            return

        employees = Employee.objects.all()
        employee_count = employees.count()

        if employee_count == 0:
            self.stdout.write(
                self.style.WARNING("No employees found. Please create employees first.")
            )
            return

        total_tasks = project_count * tasks_per_project
        self.stdout.write(
            f"Generating {tasks_per_project} tasks for each of {project_count} projects ({total_tasks} total)..."
        )
        start_time = time.time()

        # First, create all parent tasks
        parent_tasks_per_project = int(tasks_per_project * (1 - subtasks_ratio))
        total_parent_tasks = project_count * parent_tasks_per_project

        self.stdout.write(
            f"  First creating {parent_tasks_per_project} parent tasks per project ({total_parent_tasks} total)..."
        )

        batches = total_parent_tasks // batch_size + (
            1 if total_parent_tasks % batch_size else 0
        )
        parent_tasks_created = 0

        # Convert querysets to lists for better performance in loops
        projects_list = list(projects)
        employees_list = list(employees)

        # Dictionary to store parent tasks by project
        project_parent_tasks = {project.id: [] for project in projects_list}

        for i in range(batches):
            batch_count = min(batch_size, total_parent_tasks - parent_tasks_created)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"    Generating parent task batch {i + 1}/{batches} ({batch_count} tasks)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                for j in range(batch_count):
                    # Determine which project this task belongs to
                    project_index = (
                        parent_tasks_created + j
                    ) // parent_tasks_per_project
                    if project_index >= project_count:
                        break

                    project = projects_list[project_index]

                    # Select random employees as assignee and creator
                    assignee = random.choice(employees_list)
                    creator = random.choice(employees_list)

                    task = TaskFactory.create(
                        project=project,
                        assigned_to=assignee,
                        created_by=creator,
                        parent_task=None,  # This is a parent task
                    )

                    # Store this task as a potential parent for subtasks
                    project_parent_tasks[project.id].append(task)

                    parent_tasks_created += 1

            batch_elapsed = time.time() - batch_start
            self.stdout.write(
                f"    Parent task batch completed in {batch_elapsed:.2f} seconds"
            )

        # Now create subtasks
        subtasks_per_project = tasks_per_project - parent_tasks_per_project
        total_subtasks = project_count * subtasks_per_project

        self.stdout.write(
            f"  Now creating {subtasks_per_project} subtasks per project ({total_subtasks} total)..."
        )

        batches = total_subtasks // batch_size + (
            1 if total_subtasks % batch_size else 0
        )
        subtasks_created = 0

        for i in range(batches):
            batch_count = min(batch_size, total_subtasks - subtasks_created)
            if batch_count <= 0:
                break

            self.stdout.write(
                f"    Generating subtask batch {i + 1}/{batches} ({batch_count} tasks)..."
            )
            batch_start = time.time()

            with transaction.atomic():
                for j in range(batch_count):
                    # Determine which project this subtask belongs to
                    project_index = (subtasks_created + j) // subtasks_per_project
                    if project_index >= project_count:
                        break

                    project = projects_list[project_index]

                    # Get parent tasks for this project
                    parent_tasks = project_parent_tasks.get(project.id, [])

                    if not parent_tasks:
                        # Skip if no parent tasks for this project
                        continue

                    # Select a random parent task
                    parent_task = random.choice(parent_tasks)

                    # Select random employees as assignee and creator
                    assignee = random.choice(employees_list)
                    creator = random.choice(employees_list)

                    TaskFactory.create(
                        project=project,
                        assigned_to=assignee,
                        created_by=creator,
                        parent_task=parent_task,
                    )

                    subtasks_created += 1

            batch_elapsed = time.time() - batch_start
            self.stdout.write(
                f"    Subtask batch completed in {batch_elapsed:.2f} seconds"
            )

        total_tasks_created = parent_tasks_created + subtasks_created
        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {total_tasks_created} tasks ({parent_tasks_created} parent tasks, {subtasks_created} subtasks) in {elapsed_time:.2f} seconds"
            )
        )
