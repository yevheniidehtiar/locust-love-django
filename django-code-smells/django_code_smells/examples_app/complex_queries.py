from django.db.models import Count, Avg, Sum, F, Q
from django.utils import timezone
from datetime import timedelta
import logging

from .complex_models import Department, Employee, Project, ProjectAssignment, Document, Task

logger = logging.getLogger(__name__)

def get_project_performance_report(project_code):
    """
    Generate a performance report for a project with nested function calls
    that cause N+1 queries. This is a complex example where the N+1 issues
    are hard to detect during code review.
    
    The function has several nested helper functions that each access related
    objects, causing N+1 queries.
    """
    try:
        # Get the project - 1 query
        project = Project.objects.get(code=project_code)
        
        # Build the report
        report = {
            'project_name': project.name,
            'project_code': project.code,
            'department': get_department_info(project),
            'budget_info': get_budget_info(project),
            'timeline': get_timeline_info(project),
            'team': get_team_info(project),
            'tasks': get_task_summary(project),
            'documents': get_document_info(project),
        }
        
        return report
    except Project.DoesNotExist:
        logger.error(f"Project with code {project_code} not found")
        return None

def get_department_info(project):
    """
    Get information about the project's department.
    This causes an N+1 query when called for each project.
    """
    # This will cause an N+1 query by accessing the related department
    department = project.department
    
    return {
        'name': department.name,
        'code': department.code,
        'description': department.description,
        'total_projects': get_department_project_count(department),
    }

def get_department_project_count(department):
    """
    Get the count of projects in a department.
    This causes another N+1 query.
    """
    # This will cause an N+1 query by accessing the related projects
    return department.projects.count()

def get_budget_info(project):
    """
    Get budget information for the project.
    This causes N+1 queries by accessing related assignments.
    """
    # Calculate total hours allocated - this will cause an N+1 query
    assignments = ProjectAssignment.objects.filter(project=project)
    total_hours = sum(assignment.hours_allocated for assignment in assignments)
    
    # Calculate cost per hour (simplified)
    cost_per_hour = project.budget / total_hours if total_hours > 0 else 0
    
    return {
        'total_budget': project.budget,
        'total_hours': total_hours,
        'cost_per_hour': cost_per_hour,
    }

def get_timeline_info(project):
    """
    Get timeline information for the project.
    """
    # Calculate days elapsed and remaining
    today = timezone.now().date()
    days_elapsed = (today - project.start_date).days if today > project.start_date else 0
    days_remaining = (project.end_date - today).days if project.end_date and today < project.end_date else 0
    
    # Get task completion status - this will cause N+1 queries
    tasks = Task.objects.filter(project=project)
    total_tasks = tasks.count()
    completed_tasks = sum(1 for task in tasks if task.status == 'DONE')
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        'start_date': project.start_date,
        'end_date': project.end_date,
        'days_elapsed': days_elapsed,
        'days_remaining': days_remaining,
        'completion_percentage': completion_percentage,
    }

def get_team_info(project):
    """
    Get information about the project team.
    This causes multiple N+1 queries by accessing related employees and their departments.
    """
    # Get all assignments for this project - 1 query
    assignments = ProjectAssignment.objects.filter(project=project)
    
    team_members = []
    for assignment in assignments:
        # Get employee details - this will cause N+1 queries
        employee = assignment.employee
        
        # Get employee's department - this will cause another N+1 query
        department = employee.department
        
        # Get employee's manager - this will cause another N+1 query
        manager = employee.manager
        
        team_member = {
            'name': f"{employee.first_name} {employee.last_name}",
            'email': employee.email,
            'department': department.name,
            'role': assignment.role,
            'hours_allocated': assignment.hours_allocated,
            'manager': f"{manager.first_name} {manager.last_name}" if manager else "No Manager",
        }
        
        # Get tasks assigned to this employee on this project - another N+1 query
        tasks = Task.objects.filter(project=project, assigned_to=employee)
        team_member['assigned_tasks'] = [task.title for task in tasks]
        
        team_members.append(team_member)
    
    return team_members

def get_task_summary(project):
    """
    Get a summary of tasks for the project.
    This causes multiple N+1 queries by accessing related tasks and their assignees.
    """
    # Get all tasks for this project - 1 query
    tasks = Task.objects.filter(project=project)
    
    # Group tasks by status
    task_summary = {
        'TODO': [],
        'IN_PROGRESS': [],
        'REVIEW': [],
        'DONE': [],
    }
    
    for task in tasks:
        # Get assignee details - this will cause N+1 queries
        assignee = task.assigned_to
        
        task_info = {
            'id': task.id,
            'title': task.title,
            'assignee': f"{assignee.first_name} {assignee.last_name}",
            'priority': task.priority,
            'due_date': task.due_date,
            'is_overdue': task.is_overdue,  # This property may cause additional queries
        }
        
        # Get subtasks - this will cause N+1 queries
        subtasks = Task.objects.filter(parent_task=task)
        if subtasks.exists():
            task_info['subtasks'] = [
                {
                    'title': subtask.title,
                    'status': subtask.status,
                    'assignee': f"{subtask.assigned_to.first_name} {subtask.assigned_to.last_name}",  # N+1 query
                }
                for subtask in subtasks
            ]
        
        task_summary[task.status].append(task_info)
    
    return task_summary

def get_document_info(project):
    """
    Get information about documents related to the project.
    This causes N+1 queries by accessing related documents and their uploaders.
    """
    # Get all documents for this project - 1 query
    documents = Document.objects.filter(project=project)
    
    document_info = []
    for document in documents:
        # Get uploader details - this will cause N+1 queries
        uploader = document.uploaded_by
        
        # This will load the large blob field for each document
        content_size = len(document.content) if document.content else 0
        
        doc_info = {
            'title': document.title,
            'file_type': document.file_type,
            'upload_date': document.upload_date,
            'uploader': f"{uploader.first_name} {uploader.last_name}",
            'size': f"{content_size} bytes",
        }
        
        document_info.append(doc_info)
    
    return document_info

# Additional complex example with deeply nested functions and hard-to-detect N+1 queries
def analyze_department_performance(department_code, start_date=None, end_date=None):
    """
    Analyze the performance of a department across all its projects.
    This function has deeply nested calls and complex logic that makes
    N+1 queries hard to detect during code review.
    """
    try:
        # Set default date range if not provided
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=90)  # Last 90 days
        if not end_date:
            end_date = timezone.now().date()
        
        # Get the department - 1 query
        department = Department.objects.get(code=department_code)
        
        # Get all projects in this department - 1 query
        projects = Project.objects.filter(department=department)
        
        # Initialize the analysis result
        analysis = {
            'department': {
                'name': department.name,
                'code': department.code,
                'total_projects': projects.count(),
                'active_projects': sum(1 for p in projects if not p.end_date or p.end_date >= timezone.now().date()),
            },
            'projects': [],
            'employees': get_employee_performance(department, start_date, end_date),
            'overall_metrics': calculate_overall_metrics(department, projects, start_date, end_date),
        }
        
        # Analyze each project
        for project in projects:
            project_analysis = analyze_single_project(project, start_date, end_date)
            analysis['projects'].append(project_analysis)
        
        return analysis
    except Department.DoesNotExist:
        logger.error(f"Department with code {department_code} not found")
        return None

def analyze_single_project(project, start_date, end_date):
    """
    Analyze a single project's performance.
    This function contains nested logic that causes N+1 queries.
    """
    # Get tasks within date range - 1 query
    tasks = Task.objects.filter(
        project=project,
        created_date__date__gte=start_date,
        created_date__date__lte=end_date
    )
    
    # Calculate task metrics
    total_tasks = tasks.count()
    completed_tasks = sum(1 for task in tasks if task.status == 'DONE')
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get team performance - this will cause N+1 queries
    team_performance = get_team_performance(project, tasks)
    
    # Calculate budget utilization
    budget_utilization = calculate_budget_utilization(project)
    
    return {
        'name': project.name,
        'code': project.code,
        'start_date': project.start_date,
        'end_date': project.end_date,
        'budget': project.budget,
        'task_metrics': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completion_rate,
        },
        'team_performance': team_performance,
        'budget_utilization': budget_utilization,
    }

def get_team_performance(project, tasks):
    """
    Get performance metrics for each team member on a project.
    This function causes multiple N+1 queries.
    """
    # Get all assignments for this project - 1 query
    assignments = ProjectAssignment.objects.filter(project=project)
    
    team_performance = []
    for assignment in assignments:
        # Get employee - this will cause an N+1 query
        employee = assignment.employee
        
        # Get tasks assigned to this employee - this will cause an N+1 query
        employee_tasks = [task for task in tasks if task.assigned_to_id == employee.id]
        total_employee_tasks = len(employee_tasks)
        completed_employee_tasks = sum(1 for task in employee_tasks if task.status == 'DONE')
        
        # Calculate performance metrics
        completion_rate = (completed_employee_tasks / total_employee_tasks * 100) if total_employee_tasks > 0 else 0
        
        # Get overdue tasks - this may cause additional queries through the is_overdue property
        overdue_tasks = sum(1 for task in employee_tasks if task.is_overdue)
        
        team_performance.append({
            'employee': f"{employee.first_name} {employee.last_name}",
            'role': assignment.role,
            'total_tasks': total_employee_tasks,
            'completed_tasks': completed_employee_tasks,
            'completion_rate': completion_rate,
            'overdue_tasks': overdue_tasks,
        })
    
    return team_performance

def calculate_budget_utilization(project):
    """
    Calculate budget utilization for a project.
    This function causes N+1 queries by accessing related assignments.
    """
    # Get all assignments - 1 query
    assignments = ProjectAssignment.objects.filter(project=project)
    
    # Calculate total hours allocated
    total_hours = sum(assignment.hours_allocated for assignment in assignments)
    
    # Calculate cost per hour
    cost_per_hour = project.budget / total_hours if total_hours > 0 else 0
    
    # Get employees and their salaries - this will cause N+1 queries
    employee_costs = []
    for assignment in assignments:
        # Get employee - this will cause an N+1 query
        employee = assignment.employee
        
        # Calculate cost for this employee
        employee_cost = employee.salary * assignment.hours_allocated / 2000  # Assuming 2000 working hours per year
        
        employee_costs.append({
            'employee': f"{employee.first_name} {employee.last_name}",
            'hours': assignment.hours_allocated,
            'cost': employee_cost,
        })
    
    total_cost = sum(item['cost'] for item in employee_costs)
    utilization_percentage = (total_cost / project.budget * 100) if project.budget > 0 else 0
    
    return {
        'total_budget': project.budget,
        'total_cost': total_cost,
        'utilization_percentage': utilization_percentage,
        'employee_costs': employee_costs,
    }

def get_employee_performance(department, start_date, end_date):
    """
    Get performance metrics for all employees in a department.
    This function causes multiple N+1 queries through nested function calls.
    """
    # Get all employees in this department - 1 query
    employees = Employee.objects.filter(department=department)
    
    employee_performance = []
    for employee in employees:
        # Get all tasks assigned to this employee within date range - this will cause an N+1 query
        tasks = Task.objects.filter(
            assigned_to=employee,
            created_date__date__gte=start_date,
            created_date__date__lte=end_date
        )
        
        # Calculate task metrics
        total_tasks = tasks.count()
        completed_tasks = sum(1 for task in tasks if task.status == 'DONE')
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Get projects this employee is assigned to - this will cause an N+1 query
        projects = Project.objects.filter(
            projectassignment__employee=employee,
            start_date__lte=end_date,
            end_date__gte=start_date if start_date else timezone.now().date()
        ).distinct()
        
        employee_performance.append({
            'name': f"{employee.first_name} {employee.last_name}",
            'email': employee.email,
            'manager': employee.manager.full_name if employee.manager else "No Manager",  # This may cause an N+1 query
            'projects': [project.name for project in projects],
            'task_metrics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': completion_rate,
            },
        })
    
    return employee_performance

def calculate_overall_metrics(department, projects, start_date, end_date):
    """
    Calculate overall performance metrics for a department.
    This function aggregates data from multiple sources and causes N+1 queries.
    """
    # Get all tasks in all projects within date range
    all_tasks = []
    for project in projects:
        # This will cause N+1 queries
        project_tasks = Task.objects.filter(
            project=project,
            created_date__date__gte=start_date,
            created_date__date__lte=end_date
        )
        all_tasks.extend(project_tasks)
    
    # Calculate task metrics
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for task in all_tasks if task.status == 'DONE')
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate budget metrics
    total_budget = sum(project.budget for project in projects)
    
    # Calculate employee metrics
    employees = Employee.objects.filter(department=department)
    total_employees = employees.count()
    
    # Calculate average tasks per employee
    avg_tasks_per_employee = total_tasks / total_employees if total_employees > 0 else 0
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate,
        'total_budget': total_budget,
        'total_employees': total_employees,
        'avg_tasks_per_employee': avg_tasks_per_employee,
    }