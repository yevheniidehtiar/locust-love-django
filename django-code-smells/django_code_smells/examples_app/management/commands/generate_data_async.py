import asyncio
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run multiple data generation tasks asynchronously"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tasks",
            type=str,
            nargs="+",
            help="List of data generation tasks to run asynchronously",
        )
        parser.add_argument(
            "--simple-data",
            action="store_true",
            help="Run generate_simple_data command with default parameters",
        )
        parser.add_argument(
            "--complex-data",
            action="store_true",
            help="Run generate_complex_data command with default parameters",
        )

    async def handle_async(self, *args, **options):
        start_time = time.time()
        tasks = options.get("tasks", [])

        # If no specific tasks provided but flags are set, add default commands
        if not tasks:
            if options.get("simple-data"):
                tasks.append("generate_simple_data")
            if options.get("complex-data"):
                tasks.append("generate_complex_data")

        if not tasks:
            self.stdout.write(
                self.style.WARNING(
                    "No tasks specified. Please provide tasks using --tasks or use --simple-data or --complex-data flags."
                )
            )
            return

        # Check if we're using SQLite
        from django.conf import settings
        is_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE']

        if is_sqlite:
            self.stdout.write(f"Running {len(tasks)} data generation tasks sequentially (SQLite detected)...")

            # Run tasks sequentially to avoid database locking issues with SQLite
            for task in tasks:
                # Parse the command and its arguments
                parts = task.split()
                command_name = parts[0]
                command_args = parts[1:] if len(parts) > 1 else []

                # Run each task one at a time
                await self.run_command(command_name, command_args)
        else:
            self.stdout.write(f"Running {len(tasks)} data generation tasks asynchronously...")

            # Create a list to hold all the task coroutines
            coroutines = []

            for task in tasks:
                # Parse the command and its arguments
                parts = task.split()
                command_name = parts[0]
                command_args = parts[1:] if len(parts) > 1 else []

                # Create a coroutine for each task
                coroutine = self.run_command(command_name, command_args)
                coroutines.append(coroutine)

            # Run all tasks concurrently for non-SQLite databases
            await asyncio.gather(*coroutines)

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully completed all data generation tasks in {elapsed_time:.2f} seconds"
            )
        )

    async def run_command(self, command_name, command_args):
        """Run a Django management command asynchronously"""
        self.stdout.write(f"Starting task: {command_name} {' '.join(command_args)}")
        task_start_time = time.time()

        # Convert command arguments to the format expected by call_command
        kwargs = {}
        for arg in command_args:
            if arg.startswith('--'):
                parts = arg[2:].split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    # Convert hyphens to underscores in the key
                    key = key.replace('-', '_')
                    # Convert value to appropriate type
                    if value.isdigit():
                        kwargs[key] = int(value)
                    elif value.lower() in ('true', 'false'):
                        kwargs[key] = value.lower() == 'true'
                    else:
                        kwargs[key] = value
                else:
                    # Handle flags without values
                    key = parts[0].replace('-', '_')
                    kwargs[key] = True

        # Run the command in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            lambda: call_command(command_name, **kwargs)
        )

        task_elapsed_time = time.time() - task_start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"Completed task: {command_name} in {task_elapsed_time:.2f} seconds"
            )
        )

    def handle(self, *args, **options):
        """Entry point for the command"""
        # Run the async handle method
        asyncio.run(self.handle_async(*args, **options))
