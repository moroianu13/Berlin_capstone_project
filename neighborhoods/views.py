import json
import os
import logging
import yaml
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
from .permissions import IsAdminOrReadOnly
from .forms import CustomUserCreationForm
from django.views.decorators.csrf import csrf_exempt
import random
import requests
import wikipedia
from fuzzywuzzy import fuzz, process

# Load YAML-based website responses
def load_website_responses():
    file_path = os.path.join(settings.BASE_DIR, 'data', 'website_responses.yaml')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Website responses YAML file not found at {file_path}.")
        return {}

# Load YAML-based factual responses
def load_factual_responses():
    file_path = os.path.join(settings.BASE_DIR, 'data', 'factual_responses.yaml')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Factual responses YAML file not found at {file_path}.")
        return {}

# Load website and factual responses from YAML
website_responses = load_website_responses()
factual_responses = load_factual_responses()

# Wikipedia summary fetch
def get_wikipedia_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found for '{query}': {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find any relevant information on that topic."

# Weather data fetching for Berlin
def get_weather_in_berlin():
    try:
        api_key = "your_api_key_here"  # Replace with your actual API key
        city = "Berlin"
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
        response = requests.get(url).json()

        if 'current' in response:
            temp = response['current']['temp_c']
            condition = response['current']['condition']['text']
            humidity = response['current']['humidity']
            wind_speed = response['current']['wind_kph']

            return f"The current temperature in Berlin is {temp}°C with {condition}. Humidity is {humidity}% and wind speed is {wind_speed} km/h."
        else:
            return "Sorry, I couldn't fetch the weather data right now."

    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return "Sorry, there was a problem retrieving the weather data."

# Manage conversation history
conversation_history = {}
user_data = {}

# Fallback responses
fallback_responses = [
    "Did you know that the Eiffel Tower can be 15 cm taller during hot days?",
    "Octopuses have three hearts!",
    "Did you know that honey never spoils?"
]

# Manage conversation history
def manage_conversation_history(session_id, user_message, bot_message):
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    conversation_history[session_id].append(f"User: {user_message}")
    conversation_history[session_id].append(f"Bot: {bot_message}")
    if len(conversation_history[session_id]) > 4:
        conversation_history[session_id] = conversation_history[session_id][-4:]

# Get predefined responses from YAML file
def get_website_response(user_message):
    best_match, score = process.extractOne(user_message, website_responses.keys(), scorer=fuzz.token_set_ratio)
    if score > 70:
        return website_responses[best_match]
    return None

# Check for predefined responses and handle name cases
def get_predefined_response(user_message, session_id):
    user_message = user_message.lower()

    # Handle name introduction
    if "my name is" in user_message:
        user_name = user_message.split("my name is")[-1].strip().capitalize()
        user_data[session_id] = user_name
        return f"Nice to meet you, {user_name}!"

    # Refer to the user's name if known
    if ("what's my name" in user_message or "what is my name" in user_message) and session_id in user_data:
        return f"Your name is {user_data[session_id]}, right?"

    # Check YAML-based website responses
    bot_message = get_website_response(user_message)
    if bot_message:
        return bot_message

    # Check in factual responses
    best_match, score = process.extractOne(user_message, factual_responses.keys(), scorer=fuzz.token_set_ratio)
    if score > 70:
        return factual_responses[best_match]

    return None

# Fallback response generator
def get_fallback_response():
    return random.choice(fallback_responses)

# Chat view to handle chat requests
@csrf_exempt
def chat_view(request):
    session_id = request.session.session_key or request.session.create()

    if request.method == 'POST':
        user_message = request.POST.get('message', '').lower()

        if session_id not in conversation_history:
            conversation_history[session_id] = []

        # First, check for predefined or factual responses
        bot_message = get_predefined_response(user_message, session_id)

        # Handle live weather check if requested
        if "temperature" in user_message and "berlin" in user_message:
            bot_message = get_weather_in_berlin()

        # Use Wikipedia for broader queries if no predefined response
        if not bot_message:
            bot_message = get_wikipedia_summary(user_message)

        # If no relevant Wikipedia result, fallback to a fun fact
        if not bot_message:
            bot_message = get_fallback_response()

        # Manage conversation history
        manage_conversation_history(session_id, user_message, bot_message)

        return JsonResponse({"response": bot_message})

    return render(request, 'neighborhoods/chatbox.html')

# Set up logger
logger = logging.getLogger(__name__)

# API Viewsets
class NeighborhoodViewSet(viewsets.ModelViewSet):
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

class BoroughViewSet(viewsets.ModelViewSet):
    queryset = Borough.objects.all()
    serializer_class = BoroughSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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
            boroughs = boroughs.filter(minimum_rent__lte=max_rent_value)
        except ValueError:
            logger.warning(f"Invalid value for max_rent: {max_rent}")

    # Filter by lifestyles if provided
    if lifestyles:
        boroughs = boroughs.filter(lifestyles__name__in=lifestyles).distinct()

    boroughs_data = [{
        'name': borough.name,
        'minimum_rent': borough.minimum_rent,
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
    borough = neighborhood.borough
    
    # Fetch related crime data using the related borough
    crime_data = CrimeData.objects.filter(borough=borough).first()
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

    neighborhoods = Neighborhood.objects.filter(borough=borough)
    neighborhood_names = neighborhoods.values_list('name', flat=True)

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
                "minimum_rent": borough.minimum_rent,
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
        form = CustomUserCreationForm(request.POST)
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