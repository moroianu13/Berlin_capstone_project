from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('borough_list/', views.borough_list, name='borough_list'),
    path('borough_data_api/', views.borough_data_api, name='borough_data_api'),
    path('borough/<slug:borough_slug>/', views.neighborhood_list, name='neighborhood_list'),  # Uses slug
    path('neighborhood_data_api/<slug:borough_slug>/', views.neighborhood_data_api, name='neighborhood_data_api'),  # Slug here too
]