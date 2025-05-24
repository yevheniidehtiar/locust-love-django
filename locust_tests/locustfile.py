import locust
import logging
from locust import HttpUser, TaskSet, task, between
from locust.runners import MasterRunner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserBehavior(TaskSet):
    @task(1)
    def get_authors(self):
        with self.client.get("/api/authors/", catch_response=True) as response:
            if response.status_code == 200:
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

        # Parse N+1 query headers
        for key, value in headers.items():
            if key.startswith("DJ_TB_SQL_NPLUS1"):
                query_index = key.split("_")[-1]
                if "STACK" in query_index:
                    nplus1_queries.setdefault(query_index[:-6], {})["stack"] = value
                else:
                    nplus1_queries[query_index] = {"query_info": value}

            # Parse Slow query headers
            if key.startswith("DJ_TB_SQL_SLOW"):
                query_index = key.split("_")[-1]
                if "STACK" in query_index:
                    slow_queries.setdefault(query_index[:-6], {})["stack"] = value
                else:
                    slow_queries[query_index] = {"query_info": value}

        # Log stack traces
        for idx, query in nplus1_queries.items():
            if "stack" in query:
                logger.info(f"N+1 Query Stack Trace {idx}: {query['stack']}")

        for idx, query in slow_queries.items():
            if "stack" in query:
                logger.info(f"Slow Query Stack Trace {idx}: {query['stack']}")

        # Custom metric reporting
        for idx, query in nplus1_queries.items():
            if "query_info" in query:
                locust.events.request.fire(
                    request_type="N+1 Query",
                    name=query["query_info"],
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=0,
                    exception=None,
                    context={},
                )

        for idx, query in slow_queries.items():
            if "query_info" in query:
                locust.events.request.fire(
                    request_type="Slow Query",
                    name=query["query_info"],
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=0,
                    exception=None,
                    context={},
                )


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)


def custom_stats_printer(environment, **kwargs):
    for stat in environment.runner.stats.entries.values():
        if stat.name and stat.response_times:
            logger.info(
                f"Custom Report - {stat.name} | Avg Response Time: {stat.avg_response_time} ms | "
                f"Median Response Time: {stat.median_response_time} ms | "
                f"99% Response Time: {stat.get_response_time_percentile(0.99)} ms"
            )


# This will print custom stats in the log every 10 seconds
if isinstance(locust.runners.get_runner(), MasterRunner):
    locust.events.init.add_listener(
        lambda environment, **kwargs: environment.events.stats_printer.add_listener(
            custom_stats_printer
        )
    )
