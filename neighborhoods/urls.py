from django.urls import path
from . import views

urlpatterns = [
    path('', views.neighborhood_list, name='neighborhood_list'),
    
]



   
