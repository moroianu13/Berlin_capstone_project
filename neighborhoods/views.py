import json
import os
import logging
from collections import Counter
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from .models import Borough, Neighborhood, CrimeData, Demographics, RentData, Amenity
from .serializers import NeighborhoodSerializer, BoroughSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .permissions import IsAdminOrReadOnly  # Import the custom permission
from .forms import CustomUserCreationForm

# Set up logger
logger = logging.getLogger(__name__)

# API Viewsets
class NeighborhoodViewSet(viewsets.ModelViewSet):
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]  # Restrict access to admin for modifying

class BoroughViewSet(viewsets.ModelViewSet):
    queryset = Borough.objects.all()
    serializer_class = BoroughSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]  # Restrict access to admin for modifying

# Home view
def home(request):
    return render(request, 'neighborhoods/home.html')

# List of boroughs with filtering based on rent and lifestyles
def borough_list(request):
    max_rent = request.GET.get('max_rent')
    lifestyles = request.GET.getlist('lifestyle')

    boroughs = Borough.objects.all()

    # Filter by maximum rent if provided
    if max_rent:
        try:
            max_rent_value = float(max_rent)
            boroughs = boroughs.filter(average_rent__lte=max_rent_value)
        except ValueError:
            logger.warning(f"Invalid value for max_rent: {max_rent}")

    # Filter by lifestyles if provided
    if lifestyles:
        boroughs = boroughs.filter(lifestyles__name__in=lifestyles).distinct()

    boroughs_data = [{
        'name': borough.name,
        'average_rent': borough.average_rent,
        'lifestyles': list(borough.lifestyles.values_list('name', flat=True)),
        'latitude': borough.latitude,
        'longitude': borough.longitude,
        'slug': borough.slug
    } for borough in boroughs]

    return render(request, 'neighborhoods/borough_list.html', {'boroughs': boroughs_data})

# View to display neighborhoods within a selected borough
def neighborhood_list(request, borough_slug):
    borough = get_object_or_404(Borough, slug=borough_slug)
    neighborhoods = Neighborhood.objects.filter(borough=borough)

    return render(request, 'neighborhoods/neighborhood_list.html', {
        'borough': borough,
        'neighborhoods': neighborhoods
    })

# Neighborhood detail view with related data
def neighborhood_detail(request, neighborhood_id):
    neighborhood = get_object_or_404(Neighborhood, id=neighborhood_id)
    crime_data = CrimeData.objects.filter(neighborhood=neighborhood).first()
    demographics = Demographics.objects.filter(neighborhood=neighborhood).first()
    rent_data = RentData.objects.filter(neighborhood=neighborhood).first()
    amenities = Amenity.objects.filter(neighborhood=neighborhood)

    amenities_grouped = Counter([a.amenity_type for a in amenities])
    amenities_labels = list(amenities_grouped.keys())
    amenities_counts = list(amenities_grouped.values())

    context = {
        'neighborhood': neighborhood,
        'crime_data': crime_data,
        'demographics': demographics,
        'rent_data': rent_data,
        'amenities': amenities,
        'amenities_labels': json.dumps(amenities_labels),
        'amenities_counts': json.dumps(amenities_counts),
        'age_distribution_json': json.dumps(demographics.age_distribution if demographics else {}),
    }

    return render(request, 'neighborhoods/neighborhood_detail.html', context)

# API view to provide neighborhood data as GeoJSON
def neighborhood_data_api(request, borough_slug):
    borough = get_object_or_404(Borough, slug=borough_slug)

    geojson_file_path = os.path.join(settings.BASE_DIR, 'static', 'geojson', 'berlin_neighborhoods.geojson')
    try:
        with open(geojson_file_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        return JsonResponse({"error": "GeoJSON file not found."}, status=404)

    # Only retrieve neighborhoods linked to the specified borough
    neighborhoods = Neighborhood.objects.filter(borough=borough)
    neighborhood_names = neighborhoods.values_list('name', flat=True)

    # Filter GeoJSON features to match only neighborhoods from the specified borough
    filtered_features = [
        feature for feature in geojson_data['features']
        if feature['properties'].get('name', '').strip().lower() in [name.strip().lower() for name in neighborhood_names]
    ]

    if not filtered_features:
        return JsonResponse({"error": "No neighborhoods found for this borough."}, status=404)

    filtered_geojson = {
        "type": "FeatureCollection",
        "features": filtered_features
    }

    return JsonResponse(filtered_geojson)


# API view to provide borough data with GeoJSON structure
def borough_data_api(request):
    boroughs = Borough.objects.all()

    features = []
    for borough in boroughs:
        lifestyles = list(borough.lifestyles.all().values_list('name', flat=True))

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": borough.geometry_coordinates
            },
            "properties": {
                "name": borough.name,
                "slug": borough.slug,
                "average_rent": borough.average_rent,
                "lifestyles": lifestyles
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return JsonResponse(geojson)

# User registration view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'neighborhoods/register.html', {'form': form})

# User login view
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'neighborhoods/login.html', {'form': form})

# User logout view
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')
