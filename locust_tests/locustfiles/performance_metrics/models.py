import dataclasses


@dataclasses.dataclass
class PerformanceMetrics:
    sql_count: int = 0
    sql_time: float = 0
    cpu_time: float = 0
    cache_count: int = 0
    cache_time: float = 0

    @classmethod
    def parse_server_timing_header(cls, server_timing_header: str):
        """
        TimerPanel_utime;dur=35.37100000000004;desc="User CPU time",
        TimerPanel_stime;dur=11.053999999999897;desc="System CPU time",
        TimerPanel_total;dur=46.42499999999993;desc="Total CPU time",
        TimerPanel_total_time;dur=46.4508340228349;desc="Elapsed time",
        SQLPanel_sql_time;dur=1.2462500017136335;desc="SQL 1 queries",
        CachePanel_total_time;dur=0;desc="Cache 0 Calls"
        """

        timing_metrics = server_timing_header.split(", ")
        pm = PerformanceMetrics()
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
                        # If there are many queries, it might indicate an N+1 issue
                        pm.sql_count = int(description.split()[1])
                        # If the duration is high, it might indicate a slow query
                        pm.sql_time = float(duration)
                    except (IndexError, ValueError):
                        # Handle parsing errors gracefully
                        pass

            if metric_name == "CachePanel_total_time":
                if description and "Calls" in description:
                    # Extract query count from description (e.g., "SQL 1 queries")
                    try:
                        # If there are many queries, it might indicate an N+1 issue
                        pm.cache_count = int(description.split()[1])
                        # If the duration is high, it might indicate a slow query
                        pm.cache_time = float(duration)
                    except (IndexError, ValueError):
                        # Handle parsing errors gracefully
                        pass
            if metric_name == "TimerPanel_total_time":
                pm.cpu_time = float(duration)

        return pm

    def average(self, metrics) -> dict:
        self.sql_count = int((self.sql_count + metrics['sql_count']) // 2)
        self.sql_time = round((self.sql_time + metrics['sql_time']) / 2, 4)
        self.cpu_time = round((self.cpu_time + metrics['cpu_time']) / 2, 4)
        self.cache_count = int((self.cache_count + metrics['cache_count']) // 2)
        self.cache_time = round((self.cache_time + metrics['cache_time']) /
                                2, 4)
        return dataclasses.asdict(self)


PERFORMANCE_METRICS_UI_HEADERS = {
    "sql_count": "SQL Count",
    "sql_time": "SQL Time",
    "cpu_time": "CPU Time",
    "cache_count": "Cache Count",
    "cache_time": "Cache Time",
}