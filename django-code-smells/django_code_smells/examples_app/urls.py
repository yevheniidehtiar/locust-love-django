from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'books', views.BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('examples/n-plus-one/', views.n_plus_one_example, name='n-plus-one-example'),
    path('examples/optimized/', views.optimized_query_example, name='optimized-query-example'),
    path('examples/expensive/', views.expensive_query_example, name='expensive-query-example'),
]