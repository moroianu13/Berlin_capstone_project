from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import NeighborhoodViewSet
from django.contrib.auth import views as auth_views
from rest_framework import permissions 
from rest_framework.authentication import TokenAuthentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Initialize the DefaultRouter for the API endpoints
router = DefaultRouter()
router.register(r'neighborhoods', NeighborhoodViewSet, basename='neighborhood')

# Schema view for API documentation using drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="RentFinder API",
        default_version='v1',
        description="Comprehensive API documentation for the RentFinder project. Find detailed information about all endpoints and their usage.",
        terms_of_service="https://www.rentfinder.com/terms/",  # Replace with your actual terms of service URL or remove
        contact=openapi.Contact(email="das.project.berlin@gmail.com"),  # Replace with actual support or contact emaildas12345?
        license=openapi.License(name="MIT License"),  # Change if your project has a different license
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # Change to IsAuthenticated if you want to restrict access
    authentication_classes=[TokenAuthentication],
)

# Define URL patterns for the Django project
urlpatterns = [
    path('', views.home, name='home'),
    path('borough_list/', views.borough_list, name='borough_list'),
    path('borough_data_api/', views.borough_data_api, name='borough_data_api'),
    path('borough/<slug:borough_slug>/', views.neighborhood_list, name='neighborhood_list'),  # Uses slug for borough
    path('neighborhood_data_api/<slug:borough_slug>/', views.neighborhood_data_api, name='neighborhood_data_api'),  # Slug for neighborhoods data
    path('neighborhood/<int:neighborhood_id>/', views.neighborhood_detail, name='neighborhood_detail'),

    # Auth-related paths for login and logout
    path('login/', auth_views.LoginView.as_view(template_name='neighborhoods/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='neighborhoods/logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    # API Documentation paths (Swagger and ReDoc)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Include API router URLs for the NeighborhoodViewSet
    path('', include(router.urls)),
]
