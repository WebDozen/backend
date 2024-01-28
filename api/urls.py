"""URL-роутинг приложения API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet

router = DefaultRouter()

router.register(
    r"idps/(?P<ipdId>\d+)/tasks", TaskViewSet, basename="tasks"
)

urlpatterns = [
    path('', include(router.urls))
]
