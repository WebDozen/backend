from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IDPViewSet, EmployeeViewSet, HeadStatisticViewSet, EmployeeStatisticViewSet

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')
router.register(
    r"employees/(?P<employee_id>\d+)/idps", IDPViewSet, basename="idps"
)
router.register(
    r'head/(?P<head_id>\d+)/statistics', HeadStatisticViewSet, 
    basename='head_statistic'
)
router.register(
    r'employees/(?P<employee_id>\d+)/statistics', EmployeeStatisticViewSet,
    basename='employee_statistic'
)
urlpatterns = [
    path('', include(router.urls))
]
