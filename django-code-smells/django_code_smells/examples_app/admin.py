from django.contrib import admin
from .models import Author, Book, Product, IndexedProduct
from .complex_models import Department, Employee, Project, ProjectAssignment, Document, Task

# Basic admin for existing models
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Product)
admin.site.register(IndexedProduct)

# Admin for Department with minimal configuration
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

# Admin for Employee with N+1 query issues
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'department_name', 'manager_name', 'salary')
    list_filter = ('department', 'hire_date')
    search_fields = ('first_name', 'last_name', 'email')
    # To fix N+1 queries from department_name and manager_name, add:
    # list_select_related = ('department', 'manager')
    
    # This method causes N+1 queries because it accesses related objects
    def department_name(self, obj):
        # This will trigger a query for each employee
        return obj.department.name
    
    # This method causes N+1 queries because it accesses related objects
    def manager_name(self, obj):
        # This will trigger a query for each employee with a manager
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return "No Manager"

# Admin for Project with N+1 query issues
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department_name', 'start_date', 'end_date', 'budget', 'employee_count', 'task_count')
    list_filter = ('department', 'start_date')
    search_fields = ('name', 'code', 'description')
    # To fix N+1 query from department_name, add:
    # list_select_related = ('department',)
    # To fix N+1 queries from employee_count and task_count,
    # override get_queryset and use annotate with Count. E.g.,
    # from django.db.models import Count
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #         employee_count_annotated=Count('employees', distinct=True),
    #         task_count_annotated=Count('tasks', distinct=True)
    #     )
    #     return queryset
    # Then update list_display to use the annotated fields:
    # list_display = (..., 'employee_count_annotated', 'task_count_annotated')
    # And define methods for these fields:
    # def employee_count(self, obj):
    #    return obj.employee_count_annotated
    # employee_count.admin_order_field = 'employee_count_annotated'
    #
    # def task_count(self, obj):
    #    return obj.task_count_annotated
    # task_count.admin_order_field = 'task_count_annotated'

    # These methods cause N+1 queries
    def department_name(self, obj):
        return obj.department.name
    
    def employee_count(self, obj):
        # This will trigger a query for each project
        return obj.employees.count()
    
    def task_count(self, obj):
        # This will trigger a query for each project
        return obj.tasks.count()

# Admin for ProjectAssignment
@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'employee_name', 'role', 'assignment_date', 'hours_allocated')
    list_filter = ('role', 'assignment_date')
    search_fields = ('project__name', 'employee__first_name', 'employee__last_name', 'role')
    # To fix N+1 queries from project_name and employee_name, add:
    # list_select_related = ('project', 'employee')
    
    # These methods cause N+1 queries
    def project_name(self, obj):
        return obj.project.name
    
    def employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

# Admin for Document with large blob field
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_name', 'uploaded_by_name', 'upload_date', 'file_type', 'content_size')
    list_filter = ('file_type', 'upload_date')
    search_fields = ('title', 'project__name', 'uploaded_by__first_name', 'uploaded_by__last_name')
    # To fix N+1 queries from project_name and uploaded_by_name, add:
    # list_select_related = ('project', 'uploaded_by')
    
    # These methods cause N+1 queries
    def project_name(self, obj):
        return obj.project.name
    
    def uploaded_by_name(self, obj):
        return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
    
    def content_size(self, obj):
        # This will load the large blob field for each document
        if obj.content:
            return f"{len(obj.content)} bytes"
        return "0 bytes"

# Admin for Task with complex N+1 query issues
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_name', 'assigned_to_name', 'created_by_name', 
                   'parent_task_title', 'priority', 'status', 'due_date', 'is_overdue')
    list_filter = ('priority', 'status', 'due_date')
    search_fields = ('title', 'description', 'project__name', 
                    'assigned_to__first_name', 'assigned_to__last_name',
                    'created_by__first_name', 'created_by__last_name')
    # To fix N+1 queries from project_name, assigned_to_name, created_by_name, and parent_task_title, add:
    # list_select_related = ('project', 'assigned_to', 'created_by', 'parent_task')
    
    # These methods cause N+1 queries
    def project_name(self, obj):
        return obj.project.name
    
    def assigned_to_name(self, obj):
        return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
    
    def created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"
    
    def parent_task_title(self, obj):
        if obj.parent_task:
            return obj.parent_task.title
        return "No parent task"
    
    # This method causes N+1 queries and uses a property that itself may cause queries
    def is_overdue(self, obj):
        # This calls the property which may trigger additional queries
        return obj.is_overdue
    is_overdue.boolean = True
