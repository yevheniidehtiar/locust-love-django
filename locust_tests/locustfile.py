import os
import sys
import json
from dataclasses import asdict
from html import escape
from time import time

from flask import Blueprint, make_response, render_template, request

from locust import FastHttpUser, TaskSet, task, between, events, run_single_user

from locust_tests.locustfiles.performance_metrics.models import \
    PERFORMANCE_METRICS_UI_HEADERS, PerformanceMetrics
from locustfiles.performance_metrics.parsers import parse_django_response
from locustfiles.startup_logger import logger


class UserBehavior(TaskSet):
    # @task(1)
    # def get_authors(self):
    #     logger.debug("Executing get_authors task")
    #     with self.client.get("/api/authors/", catch_response=True) as response:
    #         if response.status_code == 200:
    #             logger.debug(f"get_authors response status: {response.status_code}")
    #
    #
    # @task(2)
    # def get_books(self):
    #     with self.client.get("/api/books/", catch_response=True) as response:
    #         if response.status_code == 200:
    #             logger.debug(f"get_books response status: {response.status_code}")

    # @task(3)
    # def n_plus_one_example(self):
    #     with self.client.get("/api/examples/n-plus-one/", catch_response=True) as response:
    #         if response.status_code == 200:
    #             logger.debug(f"n_plus_one_example response status: {response.status_code}")


    # @task(3)
    # def optimized_query_example(self):
    #     with self.client.get("/api/examples/optimized/", catch_response=True) as response:
    #         if response.status_code == 200:
    #             logger.debug(f"optimized_query_example response status: {response.status_code}")

    @task(3)
    def expensive_query_example(self):
        with self.client.get("/api/examples/expensive/",
                             catch_response=True, debug_stream=sys.stderr) as response:
            if response.status_code == 200:
                logger.debug(f"expensive_query_example response status: {response.status_code}")
    #
    # @task(3)
    # def complex_nested_queries_example(self):
    #     with self.client.get("/api/examples/complex-nested-queries/", catch_response=True) as response:
    #         if response.status_code == 200:
    #             logger.debug(f"complex_nested_queries_example response status: {response.status_code}")
    #
    # @task(3)
    # def department_performance_analysis_example(self):
    #     with self.client.get("/api/examples/department-performance-analysis/", catch_response=True) as response:
    #         if response.status_code == 200:
    #             logger.debug(f"department_performance_analysis_example response status: {response.status_code}")


class WebsiteUser(FastHttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)


performance_metrics: dict[tuple[str, str], dict[str, int | float | str]] = {}

path = os.path.dirname(os.path.abspath(__file__))
extend = Blueprint(
    "extend",
    "extend_web_ui",
    static_folder = f"{path}/static/",
    static_url_path = "/extend/static/",
    template_folder = f"{path}/templates/",
)

@events.init.add_listener
def locust_init(environment, **kwargs):
    """
    Load data on locust init.
    :param environment:
    :param kwargs:
    :return:
    """

    if environment.web_ui:
        # this code is only run on the master node (the web_ui instance doesn't exist on workers)
        def get_performance_metrics():
            metrics_tmp = []
            if performance_metrics:
                for idx, (name, metrics) in enumerate(performance_metrics.items()):
                    if idx > 500:
                        break
                    metrics_tmp.append(
                        {
                            "name": str(name[0]),
                            "method": str(name[1]),
                            "safe_name": escape(str(name[0]), quote=False),
                            **metrics
                        }
                    )
            return metrics_tmp

        @environment.web_ui.app.after_request
        def extend_stats_response(response):
            if request.path != "/stats/requests":
                return response

            # extended_stats contains the data where extended_tables looks for its data: "cache-statistics"
            response.set_data(
                json.dumps(
                    {
                        **response.json,
                        "extended_stats": [
                            {
                                "key": "performance-metrics",
                                "data": get_performance_metrics()
                            }
                        ]
                    }
                )
            )

            return response

        @extend.route("/performance")
        def extend_web_ui():
            """
            Add route to access the extended web UI with our new tab.
            """
            # ensure the template_args are up to date before using them
            environment.web_ui.update_template_args()

            return render_template(
                "index.html",
                template_args={
                    **environment.web_ui.template_args,
                    # extended_tabs and extended_tables keys must match.
                    "extended_tabs": [
                        {
                            "title": "Performance metrics",
                            "key": "performance-metrics"
                        }
                    ],
                    "extended_tables": [
                        {
                            "key": "performance-metrics",
                            "structure": [
                                {"key": "name", "title": "Name"},
                                *[
                                    {"key": key, "title": title}
                                    for key, title in
                                    PERFORMANCE_METRICS_UI_HEADERS.items()
                                ]
                            ]
                        }
                    ],
                    "extended_csv_files": [{"href": "/performance/csv",
                                            "title": "Download Performance "
                                                     "Metrics CSV"}
                                           ],

                },
            )

        @extend.route("/performance/csv")
        def request_performance_csv():
            """
            Add route to enable downloading of cache stats as CSV
            """
            response = make_response(performance_csv())
            file_name = f"performance-{time()}.csv"
            disposition = f"attachment;filename={file_name}"
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response

        def performance_csv():
            """Returns the cache stats as CSV."""
            rows = [",".join(['"Name"', *list(PERFORMANCE_METRICS_UI_HEADERS.keys())])]

            if performance_metrics:
                for name, stats in performance_metrics.items():
                    rows.append(f'"{name}",' + ",".join(
                        str(v) for v in stats.values()))
            return "\n".join(rows)

        # register our new routes and extended UI with the Locust web UI
        environment.web_ui.app.register_blueprint(extend)

@events.request.add_listener
def my_request_handle_performance_metrics(
        request_type, name, response_time, response_length, response,
        context, exception, start_time, url, **kwargs
):
    metrics = parse_django_response(response)
    # performance_metrics[(name, request_type)] = asdict(metrics)

    existing_metrics = performance_metrics.get((name, request_type))
    if existing_metrics is None:
        performance_metrics[(name, request_type)] = asdict(metrics)
    else:
        performance_metrics[(name, request_type)] = metrics.average(existing_metrics)

    # import pdb
    # pdb.set_trace()

@events.report_to_master.add_listener
def on_report_to_master(client_id, data):
    """
    This event is triggered on the worker instances every time a stats report is
    to be sent to the locust master. It will allow us to add our extra cache
    data to the dict that is being sent, and then we clear the local stats in the worker.
    """
    global performance_metrics
    data["performance_metrics"] = performance_metrics
    performance_metrics = {}

@events.worker_report.add_listener
def on_worker_report(client_id, data):
    """
    This event is triggered on the master instance when a new stats report arrives
    from a worker. Here we just add the cache to the master's aggregated stats dict.
    """
    for name, metrics in data["performance_metrics"].items():
        performance_metrics.setdefault(name, asdict(PerformanceMetrics()))
        for stat_name, value in metrics.items():
            performance_metrics[name][stat_name] += value

@events.reset_stats.add_listener
def on_reset_stats():
    """
    Event handler that get triggered on click of web UI Reset Stats button
    """

    global performance_metrics
    performance_metrics = {}

if __name__ == "__main__":
    run_single_user(WebsiteUser)
