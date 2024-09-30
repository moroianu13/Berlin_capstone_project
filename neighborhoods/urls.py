from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import NeighborhoodViewSet
from django.urls import include

router = DefaultRouter()
router.register(r'neighborhoods', NeighborhoodViewSet, basename='neighborhood')


urlpatterns = [
    path('', views.home, name='home'),
    path('borough_list/', views.borough_list, name='borough_list'),
    path('borough_data_api/', views.borough_data_api, name='borough_data_api'),
    path('borough/<slug:borough_slug>/', views.neighborhood_list, name='neighborhood_list'),  # Uses slug
    path('neighborhood_data_api/<slug:borough_slug>/', views.neighborhood_data_api, name='neighborhood_data_api'),  # Slug here too
    path('neighborhood/<int:neighborhood_id>/', views.neighborhood_detail, name='neighborhood_detail'),
    path('', include(router.urls)),
]

# Add the router URLs to your urlpatterns
urlpatterns += router.urls