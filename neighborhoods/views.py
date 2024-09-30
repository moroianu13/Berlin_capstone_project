import json
import os
import logging
from collections import Counter
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Borough, Neighborhood,  CrimeData, Demographics, RentData, Amenity
from .serializers import NeighborhoodSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class NeighborhoodViewSet(viewsets.ModelViewSet):
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access the API

class NeighborhoodViewSet(viewsets.ModelViewSet):
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    
    
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'neighborhoods/home.html')

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
        'slug': borough.slug  # Including slug for the links in the template
    } for borough in boroughs]

    return render(request, 'neighborhoods/borough_list.html', {
        'boroughs': boroughs_data
    })


# View to display neighborhoods within a selected borough
def neighborhood_list(request, borough_slug):
    # Get the borough object based on the slug
    borough = get_object_or_404(Borough, slug=borough_slug)

    # Retrieve neighborhoods linked to this borough
    neighborhoods = Neighborhood.objects.filter(borough=borough)

    return render(request, 'neighborhoods/neighborhood_list.html', {
        'borough': borough,
        'neighborhoods': neighborhoods
    })

def neighborhood_detail(request, neighborhood_id):
    neighborhood = get_object_or_404(Neighborhood, id=neighborhood_id)
    crime_data = CrimeData.objects.filter(neighborhood=neighborhood).first()
    demographics = Demographics.objects.filter(neighborhood=neighborhood).first()
    rent_data = RentData.objects.filter(neighborhood=neighborhood).first()
    amenities = Amenity.objects.filter(neighborhood=neighborhood)
    
    # Group and count amenities by type
    amenities_grouped = Counter([a.amenity_type for a in amenities])
    amenities_labels = list(amenities_grouped.keys())
    amenities_counts = list(amenities_grouped.values())

    # Debugging: Print statements to verify data
    print(f"Crime Data: {crime_data}")
    print(f"Demographics: {demographics}")
    print(f"Rent Data: {rent_data}")
    print(f"Amenities: {amenities}")

    context = {
        'neighborhood': neighborhood,
        'crime_data': crime_data,
        'demographics': demographics,
        'rent_data': rent_data,
        'amenities': amenities,
        'amenities_labels': json.dumps(amenities_labels),  # Pass labels as JSON
        'amenities_counts': json.dumps(amenities_counts),  # Pass counts as JSON
        'age_distribution_json': json.dumps(demographics.age_distribution),  # Convert to JSON here
    }
    if demographics:
        context['age_distribution'] = json.dumps(demographics.age_distribution)
    print(context)

    return render(request, 'neighborhoods/neighborhood_detail.html', context)

    
    
# API view to provide borough data with filtering (for use in JavaScript)
def neighborhood_data_api(request, borough_slug):
    # Get the borough object based on the slug, or return 404 if not found
    borough = get_object_or_404(Borough, slug=borough_slug)

    # Load the static GeoJSON file
    geojson_file_path = os.path.join(settings.BASE_DIR, 'static', 'geojson', 'berlin_neighborhoods.geojson')

    try:
        with open(geojson_file_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        return JsonResponse({"error": "GeoJSON file not found."}, status=404)

    # Get the neighborhood names from the database for the given borough
    neighborhoods = Neighborhood.objects.filter(borough=borough)
    neighborhood_names = neighborhoods.values_list('name', flat=True)

    # Filter the GeoJSON data based on the neighborhood names
    filtered_features = []
    for feature in geojson_data['features']:
        if feature['properties'].get('name') in neighborhood_names:
            filtered_features.append(feature)

    # If no features are found, return an error
    if not filtered_features:
        return JsonResponse({"error": "No neighborhoods found for this borough."}, status=404)

    filtered_geojson = {
        "type": "FeatureCollection",
        "features": filtered_features
    }

    return JsonResponse(filtered_geojson)




# View to provide borough data with filtering (for use in JavaScript)
def borough_data_api(request):
    boroughs = Borough.objects.all()

    features = []
    for borough in boroughs:
        # Retrieve associated lifestyles from the ManyToManyField
        lifestyles = list(borough.lifestyles.all().values_list('name', flat=True))

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": borough.geometry_coordinates  # Assuming borough has polygons stored
            },
            "properties": {
                "name": borough.name,
                "slug": borough.slug,  # Include slug in the properties
                "average_rent": borough.average_rent,
                "lifestyles": lifestyles  # Include lifestyles in the properties
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return JsonResponse(geojson)


