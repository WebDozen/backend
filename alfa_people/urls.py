from django.contrib import admin
from django.urls import include, path


VERSION_API = '1'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
