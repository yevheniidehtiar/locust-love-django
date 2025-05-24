from django.db import models
from datetime import date

class Department(models.Model):
    """
    Department model for organizational structure.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    """
    Employee model with relationships to Department and other Employees.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, related_name='employees', on_delete=models.CASCADE)
    manager = models.ForeignKey('self', null=True, blank=True, related_name='subordinates', on_delete=models.SET_NULL)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def department_name(self):
        return self.department.name
    
    @property
    def manager_name(self):
        if self.manager:
            return self.manager.full_name
        return "No Manager"

class Project(models.Model):
    """
    Project model with many-to-many relationship to Employee.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    department = models.ForeignKey(Department, related_name='projects', on_delete=models.CASCADE)
    employees = models.ManyToManyField(Employee, through='ProjectAssignment', related_name='projects')
    
    def __str__(self):
        return self.name

class ProjectAssignment(models.Model):
    """
    Through model for Project-Employee many-to-many relationship.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    assignment_date = models.DateField()
    hours_allocated = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('project', 'employee', 'role')
    
    def __str__(self):
        return f"{self.employee} as {self.role} on {self.project}"

class Document(models.Model):
    """
    Document model with large binary content and relationships to Project and Employee.
    """
    title = models.CharField(max_length=200)
    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(Employee, related_name='uploaded_documents', on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=20)
    content = models.BinaryField(blank=True, null=True)  # Large binary field for document content
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title

class Task(models.Model):
    """
    Task model with relationships to Project, Employee, and other Tasks.
    """
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('REVIEW', 'Review'),
        ('DONE', 'Done'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(Employee, related_name='assigned_tasks', on_delete=models.CASCADE)
    created_by = models.ForeignKey(Employee, related_name='created_tasks', on_delete=models.CASCADE)
    parent_task = models.ForeignKey('self', null=True, blank=True, related_name='subtasks', on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='TODO')
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != 'DONE' and self.due_date < date.today():
            return True
        return False