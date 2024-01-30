from django.urls import path, include

from alfa_people.urls import VERSION_API


urlpatterns = [
    path(f'v{VERSION_API}/', include(f'api.v{VERSION_API}.urls')),
]
