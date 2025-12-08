import json
import os
import logging
import yaml
import string
import random
import requests
import wikipedia
from wikipedia import summary, exceptions
from collections import Counter, defaultdict
from django.conf import settings
import google.generativeai as genai
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

# Load YAML-based dialog responses
def load_dialog_responses():
    file_path = os.path.join(settings.BASE_DIR, 'data', 'dialog.yaml')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            dialogs = yaml.safe_load(file)
            if not isinstance(dialogs, dict) or 'dialogs' not in dialogs:
                raise ValueError("Invalid structure: 'dialog.yaml' must contain a 'dialogs' key.")
            if not isinstance(dialogs['dialogs'], list):
                raise ValueError("'dialogs' must be a list.")
            return dialogs
    except FileNotFoundError:
        logging.error(f"Dialog YAML file not found at {file_path}.")
        return {}
    except Exception as e:
        logging.error(f"Error loading dialog.yaml: {e}")
        return {}

# Load YAML responses
website_responses = load_website_responses()
factual_responses = load_factual_responses()
dialog_responses = load_dialog_responses()


def preprocess_query(query):
    # Remove common prefixes
    prefixes = ["what do you know about", "tell me about", "do you know about"]
    for prefix in prefixes:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()
    return query



# Wikipedia summary fetch
def get_wikipedia_summary(query):
    try:
        query = preprocess_query(query)  # Preprocess user query
        # Attempt to fetch a summary for the query
        summary_text = summary(query, sentences=2)
        return summary_text
    except exceptions.DisambiguationError as e:
        # Provide options if there are multiple results
        logging.warning(f"Disambiguation error for '{query}': {e.options}")
        return f"Multiple results found for '{query}': {', '.join(e.options[:3])}. Please specify further."
    except exceptions.PageError:
        # Handle missing pages
        return f"Sorry, I couldn't find any relevant information about '{query}'."
    except Exception as e:
        logging.error(f"Unexpected error in get_wikipedia_summary: {e}")
        return "Sorry, there was a problem retrieving the information."


# Initialize Google Gemini AI
dotenv_path = os.path.join(settings.BASE_DIR, '.env_docker')
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here':
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')  # Using 1.5 for better free tier limits
else:
    gemini_model = None
    logging.warning("Gemini API key not configured. AI chat will use fallback responses.")

# Weather data fetching for Berlin
def get_weather_in_berlin():
    try:
        api_key = os.getenv('WEATHER_API_KEY')
        if not api_key:
            logging.error("Weather API key is missing in the .env_docker file.")
            return "Weather API key is not configured."

        city = "Berlin"
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
        response = requests.get(url)  # Get the raw response first

        # Log the response for debugging
        logging.debug(f"Weather API Response: {response.status_code} {response.text}")

        # Check the HTTP status code
        if response.status_code != 200:
            logging.error(f"Weather API returned an error: {response.status_code} {response.text}")
            return "Sorry, I couldn't fetch the weather data right now."

        # Parse the JSON response
        data = response.json()

        # Extract weather details
        if 'current' in data:
            temp = data['current']['temp_c']
            condition = data['current']['condition']['text']
            humidity = data['current']['humidity']
            wind_speed = data['current']['wind_kph']

            return f"The current temperature in Berlin is {temp}°C with {condition}. Humidity is {humidity}% and wind speed is {wind_speed} km/h."
        else:
            logging.error("Weather data is missing the 'current' key in the response.")
            return "Sorry, I couldn't fetch the weather data right now."

    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException occurred: {e}")
        return "Sorry, there was a problem retrieving the weather data."
    except Exception as e:
        logging.error(f"Unexpected error in get_weather_in_berlin: {e}")
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
    # Initialize session history if it doesn't exist
    if session_id not in conversation_history:
        conversation_history[session_id] = {'state': None, 'messages': []}

    # Append user and bot messages to the 'messages' list
    conversation_history[session_id]['messages'].append(f"User: {user_message}")
    conversation_history[session_id]['messages'].append(f"Bot: {bot_message}")

    # Limit the history to the last 4 messages for simplicity
    if len(conversation_history[session_id]['messages']) > 4:
        conversation_history[session_id]['messages'] = conversation_history[session_id]['messages'][-4:]




# Get responses from dialog.yaml
def get_dialog_response(user_message, session_id):
    # Normalize user input to lowercase
    user_message = user_message.strip().lower()

    if not isinstance(dialog_responses, dict):
        logging.error(f"dialog_responses is not a dictionary: {type(dialog_responses)}")
        return None

    dialogs = dialog_responses.get('dialogs', [])
    if not dialogs:
        logging.error("No dialogs found in dialog_responses.")
        return "Sorry, I couldn't find any information for that query."

    # Exact match prioritization
    for dialog in dialogs:
        if user_message == dialog['user'].strip().lower():
            logging.debug(f"Exact match found: {dialog['user']}")
            if 'next_stage' in dialog:
                conversation_history[session_id]['state'] = dialog.get('next_stage')

            if "{{ weather_response }}" in dialog['bot']:
                weather_data = get_weather_in_berlin()
                if weather_data:
                    logging.info(f"Replacing placeholder with weather data: {weather_data}")
                    return dialog['bot'].replace("{{ weather_response }}", weather_data)
                else:
                    logging.error("Failed to fetch weather data.")
                    return "Sorry, I couldn't fetch the weather data right now."

            return dialog['bot']

    # Partial matching fallback
    for dialog in dialogs:
        if dialog['user'].strip().lower() in user_message:
            logging.debug(f"Partial match found: {dialog['user']}")
            if 'next_stage' in dialog:
                conversation_history[session_id]['state'] = dialog.get('next_stage')

            if "{{ weather_response }}" in dialog['bot']:
                weather_data = get_weather_in_berlin()
                if weather_data:
                    logging.info(f"Replacing placeholder with weather data: {weather_data}")
                    return dialog['bot'].replace("{{ weather_response }}", weather_data)
                else:
                    logging.error("Failed to fetch weather data.")
                    return "Sorry, I couldn't fetch the weather data right now."

            return dialog['bot']

    logging.warning(f"No dialog match found for: {user_message}")
    return None




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



 # Check dialog responses first
    bot_message = get_dialog_response(user_message, session_id)
    if bot_message:
        return bot_message
    
    
   # Check factual responses first
    best_match, score = process.extractOne(user_message, factual_responses.keys(), scorer=fuzz.token_set_ratio)
    if score > 80:  # Increase threshold for higher precision
        return factual_responses[best_match]

    # Check website responses next
    best_match, score = process.extractOne(user_message, website_responses.keys(), scorer=fuzz.token_set_ratio)
    if score > 70:
        return website_responses[best_match]

    return None

# Fallback response generator
def get_fallback_response():
    return random.choice(fallback_responses)

# AI-powered response using Google Gemini
def get_ai_response(user_message, session_id):
    """Generate AI response using Google Gemini with Berlin rental context"""
    if not gemini_model:
        return None
    
    try:
        # Build context about Berlin RentWise
        system_context = """You are a helpful AI assistant for Berlin RentWise, a website that helps people find rental apartments in Berlin. 
        You have access to information about Berlin neighborhoods, boroughs, rental prices, crime statistics, and amenities.
        
        Key features of the website:
        - Search neighborhoods by affordability, family-friendliness, nightlife, and green spaces
        - View crime statistics and demographics for each neighborhood
        - Compare rental prices across different areas
        - Find nearby amenities (parks, schools, hospitals, public transport)
        
        When users ask about neighborhoods, rents, or living in Berlin, provide helpful, conversational responses.
        Keep responses concise (2-3 sentences) and friendly."""
        
        # Get conversation history for context
        history_context = ""
        if session_id in conversation_history:
            recent_messages = conversation_history[session_id]['messages'][-4:]
            history_context = "\n".join(recent_messages)
        
        # Combine context and user message
        full_prompt = f"{system_context}\n\nConversation history:\n{history_context}\n\nUser: {user_message}\n\nAssistant:"
        
        # Generate response
        response = gemini_model.generate_content(full_prompt)
        return response.text.strip()
        
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        return None

# Chat view to handle chat requests
@csrf_exempt
def chat_view(request):
    session_id = request.session.session_key or request.session.create()

    if request.method == 'POST':
       user_message = request.POST.get('message', '').lower().strip(string.punctuation)

    if session_id not in conversation_history:
            conversation_history[session_id] = {'state': None, 'messages': []}


    # Priority 1: Check dialog responses for specific patterns
    bot_message = get_dialog_response(user_message, session_id)
    
    # Priority 2: Check for predefined or factual responses
    if not bot_message:
        bot_message = get_predefined_response(user_message, session_id)

    # Priority 3: Handle live weather check if requested
    if not bot_message and "temperature" in user_message and "berlin" in user_message:
        bot_message = get_weather_in_berlin()

    # Priority 4: Use AI for natural conversation (NEW!)
    if not bot_message:
        bot_message = get_ai_response(user_message, session_id)

    # Priority 5: Use Wikipedia for broader queries if AI not available
    if not bot_message:
        bot_message = get_wikipedia_summary(user_message)

    # Priority 6: If all else fails, fallback to a fun fact
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