from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IDPViewSet,
    EmployeeViewSet,
    HeadStatisticViewSet,
    TaskStatusChangeViewSet
)

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')
router.register(
    r'employees/(?P<employee_id>\d+)/idps', IDPViewSet, basename='idps'
)
router.register(
    'head/statistics', HeadStatisticViewSet,
    basename='head_statistic'
)
router.register(
    r'idps/(?P<idp_id>\d+)/tasks/(?P<task_id>\d+)', TaskStatusChangeViewSet,
    basename='task_status'
)
urlpatterns = [
    path('', include(router.urls))
]
