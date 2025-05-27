import logging
import locust
from locust import HttpUser, TaskSet, task, between
from locust.runners import MasterRunner


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add a debug log message at startup
logger.debug("Locust script starting up - DEBUG level")
logger.info("Locust script starting up - INFO level")


class UserBehavior(TaskSet):
    @task(1)
    def get_authors(self):
        logger.debug("Executing get_authors task")
        with self.client.get("/api/authors/", catch_response=True) as response:
            if response.status_code == 200:
                logger.debug(f"get_authors response status: {response.status_code}")
                self.parse_headers(response)

    @task(2)
    def get_books(self):
        with self.client.get("/api/books/", catch_response=True) as response:
            if response.status_code == 200:
                self.parse_headers(response)

    @task(3)
    def n_plus_one_example(self):
        with self.client.get(
            "/api/examples/n-plus-one/", catch_response=True
        ) as response:
            if response.status_code == 200:
                self.parse_headers(response)

    @task(3)
    def optimized_query_example(self):
        with self.client.get(
            "/api/examples/optimized/", catch_response=True
        ) as response:
            if response.status_code == 200:
                self.parse_headers(response)

    @task(3)
    def expensive_query_example(self):
        with self.client.get(
            "/api/examples/expensive/", catch_response=True
        ) as response:
            if response.status_code == 200:
                self.parse_headers(response)

    @task(3)
    def complex_nested_queries_example(self):
        with self.client.get(
            "/api/examples/complex-nested-queries/", catch_response=True
        ) as response:
            if response.status_code == 200:
                self.parse_headers(response)

    @task(3)
    def department_performance_analysis_example(self):
        with self.client.get(
            "/api/examples/department-performance-analysis/", catch_response=True
        ) as response:
            if response.status_code == 200:
                self.parse_headers(response)

    def parse_headers(self, response):
        headers = response.headers
        nplus1_queries = {}
        slow_queries = {}

        # Parse Server-timing header for SQL metrics
        if "Server-Timing" in headers:
            server_timing = headers["Server-Timing"]
            timing_metrics = server_timing.split(", ")

            for metric in timing_metrics:
                parts = metric.split(";")
                metric_name = parts[0]
                duration = None
                description = None

                for part in parts[1:]:
                    if part.startswith("dur="):
                        duration = part[4:]
                    elif part.startswith("desc="):
                        description = part[5:].strip('"')

                # Check for SQLPanel metrics that might indicate N+1 or slow queries
                if metric_name == "SQLPanel_sql_time":
                    if description and "queries" in description:
                        # Extract query count from description (e.g., "SQL 1 queries")
                        try:
                            query_count = int(description.split()[1])
                            # If there are many queries, it might indicate an N+1 issue
                            if query_count > 10:  # Threshold for potential N+1 issue
                                nplus1_queries["sql_panel"] = {
                                    "query_info": f"Potential N+1 issue: {description}",
                                    "duration": duration,
                                }
                            # If the duration is high, it might indicate a slow query
                            if duration and float(duration) > 0.1:  # Threshold
                                # for slow query (1 second)
                                slow_queries["sql_panel"] = {
                                    "query_info": f"Potential slow query: {description}",
                                    "duration": duration,
                                }
                        except (IndexError, ValueError):
                            # Handle parsing errors gracefully
                            pass
        else:
            logger.debug("Server-timing metrics not found, skipping")
            logger.debug(str(headers.keys()))
        # Log stack traces
        for idx, query in nplus1_queries.items():
            if "stack" in query:
                logger.info(f"N+1 Query Stack Trace {idx}: {query['stack']}")

        for idx, query in slow_queries.items():
            if "stack" in query:
                logger.info(f"Slow Query Stack Trace {idx}: {query['stack']}")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)


def custom_stats_printer(environment, **kwargs):
    logger.debug("Custom stats printer called")
    for stat in environment.runner.stats.entries.values():
        if stat.name and stat.response_times:
            logger.info(
                f"Custom Report - {stat.name} | Avg Response Time: {stat.avg_response_time} ms | "
                f"Median Response Time: {stat.median_response_time} ms | "
                f"99% Response Time: {stat.get_response_time_percentile(0.99)} ms"
            )


# This will print custom stats in the log every 10 seconds
@locust.events.init.add_listener
def on_locust_init(environment, **kwargs):
    logger.debug("Locust initialization event triggered")
    if isinstance(environment.runner, MasterRunner):
        logger.debug("Master runner detected, adding stats_printer listener")
        environment.events.stats_printer.add_listener(custom_stats_printer)
