from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from neighborhoods.models import ( Borough, Neighborhood, CrimeData, Amenities,Lifestyle,
)
from neighborhoods.views import manage_conversation_history, conversation_history
from unittest.mock import patch

UserModel = get_user_model()

class ChatViewTest(TestCase):
    @patch('neighborhoods.views.get_weather_in_berlin')
    @patch('neighborhoods.views.get_wikipedia_summary')
    @patch('neighborhoods.views.get_dialog_response')
    def test_chat_view_post(self, mock_dialog_response, mock_wikipedia, mock_weather):
        # Test dialog response (has priority over predefined)
        mock_dialog_response.return_value = "Hi there! How can I help you today?"
        response = self.client.post(reverse('chat_view'), {'message': 'Hi'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())
        self.assertEqual(response.json()['response'], "Hi there! How can I help you today?")
        mock_dialog_response.assert_called_once_with('hi', None)

        # Test weather response
        mock_dialog_response.return_value = None
        mock_weather.return_value = "It's sunny in Berlin."
        response = self.client.post(reverse('chat_view'), {'message': 'What is the temperature in Berlin?'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())
        self.assertEqual(response.json()['response'], "It's sunny in Berlin.")
        mock_weather.assert_called_once()

        # Test Wikipedia response (when dialog, predefined, weather, and AI all return None)
        mock_dialog_response.return_value = None
        with patch('neighborhoods.views.get_predefined_response', return_value=None), \
             patch('neighborhoods.views.get_ai_response', return_value=None):
            mock_wikipedia.return_value = "Berlin is the capital of Germany."
            response = self.client.post(reverse('chat_view'), {'message': 'Tell me about Berlin.'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json())
            self.assertEqual(response.json()['response'], "Berlin is the capital of Germany.")

    def test_chat_view_fallback_response(self):
        with patch('neighborhoods.views.get_dialog_response', return_value=None), \
             patch('neighborhoods.views.get_predefined_response', return_value=None), \
             patch('neighborhoods.views.get_weather_in_berlin', return_value=None), \
             patch('neighborhoods.views.get_ai_response', return_value=None), \
             patch('neighborhoods.views.get_wikipedia_summary', return_value=None):
            response = self.client.post(reverse('chat_view'), {'message': 'Unanswerable query'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('response', response.json())
            self.assertIn(response.json()['response'], [
                "Did you know that the Eiffel Tower can be 15 cm taller during hot days?",
                "Octopuses have three hearts!",
                "Did you know that honey never spoils?"
            ])

    def test_manage_conversation_history(self):
        session_id = 'test_session'
        user_message = 'Hello'
        bot_message = 'Hi there!'
        conversation_history.clear()

        manage_conversation_history(session_id, user_message, bot_message)
        print(conversation_history)
        self.assertIn(session_id, conversation_history)
        self.assertEqual(len(conversation_history[session_id]['messages']), 2)
        self.assertEqual(conversation_history[session_id]['messages'][0], f"User: {user_message}")
        self.assertEqual(conversation_history[session_id]['messages'][1], f"Bot: {bot_message}")

        manage_conversation_history(session_id, "How are you?", "I'm fine.")
        manage_conversation_history(session_id, "What's your name?", "I'm ChatBot.")
        manage_conversation_history(session_id, "Tell me a fact.", "Octopuses have three hearts.")
        
        # Check the conversation length - should be 4 messages (last 4 due to history limit)
        self.assertEqual(len(conversation_history[session_id]['messages']), 4)
        # The first 4 messages (Hello exchange) were removed, only last 2 exchanges remain
        self.assertEqual(conversation_history[session_id]['messages'][0], "User: What's your name?")
        self.assertEqual(conversation_history[session_id]['messages'][1], "Bot: I'm ChatBot.")
        self.assertEqual(conversation_history[session_id]['messages'][2], "User: Tell me a fact.")
        self.assertEqual(conversation_history[session_id]['messages'][3], "Bot: Octopuses have three hearts.")


class BoroughListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.lifestyle1 = Lifestyle.objects.create(name='Active')
        self.lifestyle2 = Lifestyle.objects.create(name='Quiet')

        self.borough1 = Borough.objects.create(
            name='Borough One',
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[],
            slug='borough-one',
        )
        self.borough1.lifestyles.add(self.lifestyle1)

        self.borough2 = Borough.objects.create(
            name='Borough Two',
            minimum_rent=700,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[],
            slug='borough-two',
        )
        self.borough2.lifestyles.add(self.lifestyle2)

    def test_borough_list_view(self):
        response = self.client.get(reverse('borough_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'neighborhoods/borough_list.html')
        self.assertEqual(len(response.context['boroughs']), 2)

    def test_borough_list_with_max_rent(self):
        response = self.client.get(reverse('borough_list'), {'max_rent': 600})
        self.assertEqual(len(response.context['boroughs']), 1)
        self.assertEqual(response.context['boroughs'][0]['name'], 'Borough One')

    def test_borough_list_invalid_max_rent(self):
        response = self.client.get(reverse('borough_list'), {'max_rent': 'invalid'})
        self.assertEqual(len(response.context['boroughs']), 2)

    def test_borough_list_no_boroughs(self):
        Borough.objects.all().delete()
        response = self.client.get(reverse('borough_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['boroughs']), 0)

    def test_borough_list_multiple_lifestyles(self):
        response = self.client.get(reverse('borough_list'), {'lifestyle': ['Active', 'Quiet']})
        self.assertEqual(len(response.context['boroughs']), 2)


class NeighborhoodListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.borough = Borough.objects.create(
            name='Borough One',
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[],
            slug='borough-one',
        )
        self.neighborhood1 = Neighborhood.objects.create(
            name='Neighborhood One',
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )
        self.neighborhood2 = Neighborhood.objects.create(
            name='Neighborhood Two',
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )
        self.crime_data = CrimeData.objects.create(
            borough=self.borough,
            total_crimes=100,
            robbery=10,
            total_assaults=20,
            total_thefts=30,
            total_residential_burglary=15,
            total_arson_incidents=5,
            total_vandalism=20,
        )
        Amenities.objects.create(
            borough=self.borough,
            neighborhood=self.neighborhood1,
            amenity_type='Park',
            name='Central Park',
        )

    def test_neighborhood_list_view(self):
        response = self.client.get(reverse('neighborhood_list', args=[self.borough.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'neighborhoods/neighborhood_list.html')
        self.assertEqual(len(response.context['neighborhoods']), 2)
        self.assertEqual(response.context['borough'], self.borough)

    def test_crime_data_aggregation(self):
        response = self.client.get(reverse('neighborhood_list', args=[self.borough.slug]))
        crime_percentages = response.context['crime_percentages']
        self.assertEqual(crime_percentages['robbery'], 10.0)
        self.assertEqual(crime_percentages['assaults'], 20.0)
        self.assertEqual(crime_percentages['thefts'], 30.0)
        self.assertEqual(crime_percentages['burglary'], 15.0)
        self.assertEqual(crime_percentages['arson'], 5.0)
        self.assertEqual(crime_percentages['vandalism'], 20.0)

    def test_amenity_data_aggregation(self):
        response = self.client.get(reverse('neighborhood_list', args=[self.borough.slug]))
        amenity_percentages = response.context['amenity_percentages']
        self.assertEqual(amenity_percentages['Park'], 100.0)

    def test_neighborhood_list_no_neighborhoods(self):
        Neighborhood.objects.all().delete()
        response = self.client.get(reverse('neighborhood_list', args=[self.borough.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['neighborhoods']), 0)

    def test_neighborhood_list_invalid_borough_slug(self):
        response = self.client.get(reverse('neighborhood_list', args=['invalid-slug']))
        self.assertEqual(response.status_code, 404)
