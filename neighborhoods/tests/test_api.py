from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.conf import settings
import json
import os
from neighborhoods.models import Borough, Neighborhood, Lifestyle

UserModel = get_user_model()


class BoroughAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(
            username='apiuser', password='ComplexPass123', is_staff=True
        )
        self.lifestyle = Lifestyle.objects.create(name='Active')
        self.borough = Borough.objects.create(
            name='Test Borough',
            minimum_rent=1000,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[]]],  # Dummy coordinates
            slug='test-borough',
        )
        self.borough.lifestyles.add(self.lifestyle)

    def test_borough_list_api_unauthenticated(self):
        response = self.client.get(reverse('borough-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borough_list_api_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('borough-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Borough')

    def test_borough_detail_api_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('borough-detail', args=[self.borough.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Borough')

    def test_create_borough_api_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Borough',
            'minimum_rent': 1200,
            'latitude': 52.5200,
            'longitude': 13.4050,
            'geometry_coordinates': [[[13.0, 52.0], [13.1, 52.0], [13.1, 52.1], [13.0, 52.1], [13.0, 52.0]]],
            'slug': 'new-borough',
            'description': 'A new borough for testing.',  # Add a valid description
            'lifestyles': [self.lifestyle.id],
        }
        response = self.client.post(reverse('borough-list'), data, format='json')
        print(response.status_code)  # Debugging output
        print(response.data)         # Debugging output
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borough.objects.count(), 2)
        self.assertEqual(Borough.objects.latest('id').name, 'New Borough')


    def test_create_borough_api_unauthenticated(self):
        data = {
            'name': 'New Borough',
            'minimum_rent': 1200,
            'latitude': 52.5200,
            'longitude': 13.4050,
            'geometry_coordinates': [[[]]],
            'slug': 'new-borough',
            'lifestyles': [self.lifestyle.id],
        }
        response = self.client.post(reverse('borough-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NeighborhoodAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(
            username='apiuser', password='ComplexPass123', is_staff=True
        )
        self.borough = Borough.objects.create(
            name='Test Borough',
            minimum_rent=1000,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[]]],  # Dummy coordinates
            slug='test-borough',
        )
        self.neighborhood = Neighborhood.objects.create(
            name='Test Neighborhood',
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
            slug='test-neighborhood',
        )

    def test_neighborhood_list_api_unauthenticated(self):
        response = self.client.get(reverse('neighborhood-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_neighborhood_list_api_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('neighborhood-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Neighborhood')

    def test_neighborhood_detail_api_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('neighborhood-detail', args=[self.neighborhood.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Neighborhood')

    def test_create_neighborhood_api_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Neighborhood',
            'borough': self.borough.id,
            'latitude': 52.5200,
            'longitude': 13.4050,
            'slug': 'new-neighborhood',
        }
        response = self.client.post(reverse('neighborhood-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Neighborhood.objects.count(), 2)
        self.assertEqual(Neighborhood.objects.latest('id').name, 'New Neighborhood')

    def test_create_neighborhood_api_unauthenticated(self):
        data = {
            'name': 'New Neighborhood',
            'borough': self.borough.id,
            'latitude': 52.5200,
            'longitude': 13.4050,
            'slug': 'new-neighborhood',
        }
        response = self.client.post(reverse('neighborhood-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BoroughDataAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.borough = Borough.objects.create(
            name='Test Borough',
            minimum_rent=1000,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[
                [[[13.0, 52.0], [13.1, 52.0], [13.1, 52.1], [13.0, 52.1], [13.0, 52.0]]]
            ],
            slug='test-borough',
        )

    def test_borough_data_api(self):
        response = self.client.get(reverse('borough_data_api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertEqual(len(data['features']), 1)
        feature = data['features'][0]
        self.assertEqual(feature['properties']['name'], 'Test Borough')
        self.assertEqual(feature['properties']['slug'], 'test-borough')


class NeighborhoodDataAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.borough = Borough.objects.create(
            name='Test Borough',
            slug='test-borough',
            minimum_rent=1000,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[]]],
        )
        self.neighborhood = Neighborhood.objects.create(
            name='Test Neighborhood',
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )
        self.geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Test Neighborhood"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[13.0, 52.0], [13.1, 52.0], [13.1, 52.1], [13.0, 52.1], [13.0, 52.0]]],
                    },
                }
            ],
        }
        geojson_file_path = os.path.join(
            settings.BASE_DIR, 'static', 'geojson', 'berlin_neighborhoods.geojson'
        )
        os.makedirs(os.path.dirname(geojson_file_path), exist_ok=True)
        with open(geojson_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.geojson_data, f)

    def tearDown(self):
        geojson_file_path = os.path.join(
            settings.BASE_DIR, 'static', 'geojson', 'berlin_neighborhoods.geojson'
        )
        if os.path.exists(geojson_file_path):
            os.remove(geojson_file_path)

    def test_neighborhood_data_api(self):
        response = self.client.get(reverse('neighborhood_data_api', args=[self.borough.slug]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertEqual(len(data['features']), 1)
        feature = data['features'][0]
        self.assertEqual(feature['properties']['name'], 'Test Neighborhood')

    def test_neighborhood_data_api_no_geojson(self):
        geojson_file_path = os.path.join(
            settings.BASE_DIR, 'static', 'geojson', 'berlin_neighborhoods.geojson'
        )
        os.remove(geojson_file_path)
        response = self.client.get(reverse('neighborhood_data_api', args=[self.borough.slug]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'GeoJSON file not found.')
