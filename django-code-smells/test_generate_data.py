#!/usr/bin/env python
import os
import sys
import django

# Add the Django project directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'django_code_smells'))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_code_smells.settings")
django.setup()

# Import the management command
from django.core.management import call_command

# Run the generate_complex_data command with 100 departments
print("Running generate_complex_data command with 100 departments...")
call_command('generate_complex_data', departments=100, employees_per_dept=5, projects_per_dept=2, batch_size=20)
print("Command completed successfully!")
