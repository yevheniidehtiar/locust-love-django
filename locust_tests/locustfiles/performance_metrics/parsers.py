from .models import PerformanceMetrics


def parse_django_response(response) -> PerformanceMetrics:
    if not response:
        return PerformanceMetrics()

    headers = getattr(response, 'headers', None)
    if not headers:
        return PerformanceMetrics()

    if "Server-Timing" in headers:
        server_timing = headers["Server-Timing"]
        pm = PerformanceMetrics.parse_server_timing_header(server_timing)
        return pm
    return PerformanceMetrics()
