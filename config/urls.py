from django.urls import path, include
from panel.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('panel.urls')),
]
