from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site path
    path('', include('neighborhoods.urls')),  # Including the URLs from the neighborhoods app
]
