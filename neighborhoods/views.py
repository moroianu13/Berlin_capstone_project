import json
import os
import logging
import yaml
import string
import random
import requests
import wikipedia
from collections import Counter, defaultdict
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q ,Sum, Count 
from .models import Borough, Neighborhood, CrimeData, Demographics, RentData, Amenities, Transports
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
from dotenv import load_dotenv
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
load_dotenv()
def get_weather_in_berlin():
    try:
        api_key = os.getenv('WEATHER_API_KEY')  # Replace with your actual API key
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
       user_message = request.POST.get('message', '').lower().strip(string.punctuation)

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
from django.db.models import F, FloatField

def neighborhood_list(request, borough_slug):
    # Get the borough based on slug
    borough = get_object_or_404(Borough, slug=borough_slug)
    
    # Query all neighborhoods in the borough
    neighborhoods = Neighborhood.objects.filter(borough=borough)

    # Total crimes for all of Berlin
    total_crimes_berlin = CrimeData.objects.aggregate(total_crimes=Sum('total_crimes'))['total_crimes'] or 0

    # Total crimes for the current borough
    crime_data = CrimeData.objects.filter(borough=borough).aggregate(
        total_crimes=Sum('total_crimes'),
        total_robbery=Sum('robbery'),
        total_assaults=Sum('total_assaults'),
        total_thefts=Sum('total_thefts'),
        total_residential_burglary=Sum('total_residential_burglary'),
        total_arson_incidents=Sum('total_arson_incidents'),
        total_vandalism=Sum('total_vandalism'),
    )
    total_crimes_borough = crime_data.get('total_crimes', 0)

    # Calculate crime percentages for the current borough
    total_crimes = crime_data.get('total_crimes') or 0
    if total_crimes > 0:
        crime_percentages = {
            'robbery': round((crime_data.get('total_robbery', 0) / total_crimes) * 100, 1),
            'assaults': round((crime_data.get('total_assaults', 0) / total_crimes) * 100, 1),
            'thefts': round((crime_data.get('total_thefts', 0) / total_crimes) * 100, 1),
            'burglary': round((crime_data.get('total_residential_burglary', 0) / total_crimes) * 100, 1),
            'arson': round((crime_data.get('total_arson_incidents', 0) / total_crimes) * 100, 1),
            'vandalism': round((crime_data.get('total_vandalism', 0) / total_crimes) * 100, 1),
        }
    else:
        crime_percentages = {key: 0.0 for key in ['robbery', 'assaults', 'thefts', 'burglary', 'arson', 'vandalism']}

    # Total crimes for each borough
    borough_crime_totals = CrimeData.objects.values('borough__name').annotate(
        total_crimes=Sum('total_crimes')
    )

    # Aggregate amenities data for the current borough
    amenities = Amenities.objects.filter(borough=borough)
    amenity_counts = amenities.values('amenity_type').annotate(count=Count('amenity_type'))

    # Calculate total and percentages for amenities
    total_amenities = sum(item['count'] for item in amenity_counts)
    if total_amenities > 0:
        amenity_percentages = {
            item['amenity_type']: round((item['count'] / total_amenities) * 100, 1)
            for item in amenity_counts
        }
    else:
        amenity_percentages = {item['amenity_type']: 0.0 for item in amenity_counts}

    context = {
        'borough': borough,
        'neighborhoods': neighborhoods,
        'crime_data': crime_data,
        'crime_percentages': crime_percentages,
        'amenity_percentages': amenity_percentages,
        'total_crimes_berlin': total_crimes_berlin,
        'total_crimes_borough': total_crimes_borough,
        'borough_crime_totals': borough_crime_totals,
    }

    return render(request, 'neighborhoods/neighborhood_list.html', context)

# Neighborhood detail view with related data
def neighborhood_detail(request, neighborhood_id):
    # Fetch the neighborhood and borough data
    neighborhood = get_object_or_404(Neighborhood, id=neighborhood_id)
    borough = neighborhood.borough

    # Related data - fetching demographics and rent data for the neighborhood
    demographics = Demographics.objects.filter(neighborhood=neighborhood).first()
    rent_data = RentData.objects.filter(neighborhood=neighborhood).first()
    transport_stations = Transports.objects.filter(neighborhood=neighborhood)
    
    # Group transport data by station name and collect all available types
    transport_data = defaultdict(list)
    for transport in transport_stations:
        transport_data[transport.name].append(transport.type)
        
        
      
      
    # Create dictionaries for ethnic distribution and age distribution
    ethnic_distribution = {}
    age_distribution = {}

    if demographics:
        # Update ethnic distribution based on actual fields in demographics model
        ethnic_distribution = {
            'germans': getattr(demographics, 'germans', 0),  # Replace with correct field names
            'turkey': getattr(demographics, 'turkey', 0),  # Replace with correct field names
            'poland': getattr(demographics, 'poland', 0),  # Replace with correct field names
            'other_percentage': getattr(demographics, 'other_percentage', 0)  # Replace with correct field names
        }

        # Update age distribution fields
        age_distribution = {
            'under_6': getattr(demographics, 'under_6', 0),
            'six_to_15': getattr(demographics, 'six_to_15', 0),
            'fifteen_to_18': getattr(demographics, 'fifteen_to_18', 0),
            'eighteen_to_27': getattr(demographics, 'eighteen_to_27', 0),
            'twenty_seven_to_45': getattr(demographics, 'twenty_seven_to_45', 0),
            'forty_five_to_55': getattr(demographics, 'forty_five_to_55', 0),
            'fifty_five_and_more': getattr(demographics, 'fifty_five_and_more', 0)
        }
        
        
    

    # Aggregate amenities data for the neighborhood
    amenities = Amenities.objects.filter(neighborhood=neighborhood)
    amenity_counts = amenities.values('amenity_type').annotate(count=Count('amenity_type'))

    # Extract labels and counts for the pie chart
    amenities_data = {item['amenity_type']: item['count'] for item in amenity_counts}

    # Context dictionary to pass data to the template
    context = {
        'neighborhood': neighborhood,
        'borough': borough,
        'demographics': demographics,
        'rent_data': rent_data,
        'ethnic_distribution_json': json.dumps(ethnic_distribution),  # JSON format for ethnic distribution
        'age_distribution_json': json.dumps(age_distribution),        # JSON format for age distribution
        'amenities_data_json': json.dumps(amenities_data),            # JSON format for amenities data
        'transport_data': dict(transport_data)                        # Grouped transport data by station name
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
dlogger = logging.getLogger(__name__)

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect('home')
                else:
                    messages.error(request, "Your account is inactive. Please contact support.")
            else:
                messages.error(request, "Invalid username or password.")
                logger.warning(f"Login attempt failed for username: {username}")
        else:
            messages.error(request, "Invalid form submission.")
            logger.warning("Invalid form data submitted during login.")
    else:
        form = AuthenticationForm()

    return render(request, 'neighborhoods/login.html', {'form': form})

# User logout view
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')