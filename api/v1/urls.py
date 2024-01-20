from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IDPViewSet

router = DefaultRouter()
router.register(
    r"employees/(?P<employee_id>\d+)/idps", IDPViewSet, basename="idps"
)

urlpatterns = [
    path('', include(router.urls))
]
