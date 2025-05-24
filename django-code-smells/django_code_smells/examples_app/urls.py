from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"authors", views.AuthorViewSet)
router.register(r"books", views.BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("examples/n-plus-one/", views.n_plus_one_example, name="n-plus-one-example"),
    path(
        "examples/optimized/",
        views.optimized_query_example,
        name="optimized-query-example",
    ),
    path(
        "examples/expensive/",
        views.expensive_query_example,
        name="expensive-query-example",
    ),
    path("examples/annotation/", views.annotation_example, name="annotation-example"),
    path(
        "examples/database-index/",
        views.database_index_example,
        name="database-index-example",
    ),
    path("examples/raw-sql/", views.raw_sql_example, name="raw-sql-example"),
    path(
        "examples/query-caching/",
        views.query_caching_example,
        name="query-caching-example",
    ),
    path(
        "examples/deferred-loading/",
        views.deferred_loading_example,
        name="deferred-loading-example",
    ),
    path(
        "examples/serializer-optimization/",
        views.serializer_optimization_example,
        name="serializer-optimization-example",
    ),
    path(
        "examples/complex-nested-queries/",
        views.complex_nested_queries_example,
        name="complex-nested-queries-example",
    ),
    path(
        "examples/department-performance-analysis/",
        views.department_performance_analysis_example,
        name="department-performance-analysis-example",
    ),
]
