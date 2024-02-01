from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IDPViewSet,
    EmployeeViewSet,
    HeadStatisticViewSet,
    TaskStatusChangeViewSet,
    CommentIdpViewsSet,
    CommentTaskViewsSet
)

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')
router.register(
    r'employees/(?P<employee_id>\d+)/idps', IDPViewSet, basename='idps'
)
router.register(
    r'head/(?P<head_id>\d+)/statistics', HeadStatisticViewSet,
    basename='head_statistic'
)
router.register(
    r'idps/(?P<idp_id>\d+)/tasks/(?P<task_id>\d+)', TaskStatusChangeViewSet,
    basename='task_status'
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
