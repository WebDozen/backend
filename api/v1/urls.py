from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (EmployeeViewSet, HeadStatisticViewSet, IDPCommentViewSet,
                    IDPViewSet, TaskCommentViewSet, TaskStatusChangeViewSet)

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')
router.register(
    r'employees/(?P<employee_id>\d+)/idps', IDPViewSet, basename='idps'
)
router.register(
    'head/statistics', HeadStatisticViewSet, basename='head_statistic'
)
router.register(
    r'idps/(?P<idp_id>\d+)/tasks/(?P<task_id>\d+)', TaskStatusChangeViewSet,
    basename='task_status'
)
router.register(
    r'idp/(?P<idp_id>\d+)/comments', IDPCommentViewSet, basename='idp_comments'
)
router.register(
    r'task/(?P<task_id>\d+)/comments', TaskCommentViewSet,
    basename='task_comments'
)
urlpatterns = [
    path('', include(router.urls))
]
