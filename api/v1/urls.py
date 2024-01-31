"""URL-роутинг приложения API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, CommentTaskViewsSet, CommentIdpViewsSet

router = DefaultRouter()

router.register(
    r"idps/(?P<idpId>\d+)/tasks", TaskViewSet, basename="tasks"
)
router.register(
    r"idp/(?P<idp_id>d+)/comments", CommentIdpViewsSet, basename="comments"
)
router.register(
    r"tasks/(?P<task_id>d+)/comments", CommentTaskViewsSet, basename="comments"
)

urlpatterns = [
    path('', include(router.urls))
]
