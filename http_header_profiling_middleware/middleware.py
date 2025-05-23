
import uuid
import logging
from django.utils.deprecation import MiddlewareMixin
from debug_toolbar.toolbar import DebugToolbar


SQL_NPLUS1_LIMIT = 10
SQL_SLOW_LIMIT = 5
HEADER_PREFIX = "DJ_TB_SQL"

# Configure the logger
logger = logging.getLogger(__name__)


class CustomDebugToolbarHeaderMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, 'debug_toolbar'):
            toolbar = DebugToolbar(request)
            stats = toolbar.get_stats()

            sql_queries = stats.get('sql', {}).get('queries', [])

            # Identify N+1 queries (repeated queries)
            repeated_queries = {}
            for query in sql_queries:
                sql = query['sql']
                if sql in repeated_queries:
                    repeated_queries[sql]['count'] += 1
                    repeated_queries[sql]['total_time'] += query['time']
                    repeated_queries[sql]['stacktrace'].extend(query['stacktrace'])
                else:
                    repeated_queries[sql] = {
                        'count': 1,
                        'total_time': query['time'],
                        'stacktrace': query['stacktrace'],
                        'is_select': query['is_select'],
                    }

            # Filter for N+1 queries (where count > 1)
            n_plus_one_queries = {sql: data for sql, data in repeated_queries.items() if data['count'] > 1}

            # Sort N+1 queries by frequency
            sorted_n_plus_one_queries = sorted(n_plus_one_queries.items(),
                                               key=lambda x: x[1]['count'],
                                               reverse=True)[:SQL_NPLUS1_LIMIT]

            # Sort slow queries by execution time
            slow_queries = sorted(sql_queries, key=lambda x: x['time'],
                                  reverse=True)[:SQL_SLOW_LIMIT]

            # Log stack traces and add UUID to headers
            for i, (sql, data) in enumerate(sorted_n_plus_one_queries):
                log_uuid = str(uuid.uuid4())
                header_name = f"{HEADER_PREFIX}_NPLUS1_{i+1}_UUID"
                response[header_name] = log_uuid

                # Log the N+1 query stack trace with UUID
                logger.info(f"N+1 Query {i+1} - UUID: {log_uuid}, SQL: {sql}, Count: {data['count']}, Time: {data['total_time']}ms, Stacktrace: {' | '.join(data['stacktrace'])}")

            for i, query in enumerate(slow_queries):
                log_uuid = str(uuid.uuid4())
                header_name = f"{HEADER_PREFIX}_SLOW_{i+1}_UUID"
                response[header_name] = log_uuid

                # Log the slow query stack trace with UUID
                logger.info(f"Slow Query {i+1} - UUID: {log_uuid}, SQL: {query['sql']}, Time: {query['time']}ms, Stacktrace: {' | '.join(query['stacktrace'])}")

        return response