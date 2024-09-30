from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from neighborhoods.models import Neighborhood, Borough
from django.contrib.auth.models import User

class NeighborhoodAPITests(APITestCase):

    def setUp(self):
        # Create a user and token for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a test Borough with all required fields
        self.borough = Borough.objects.create(
            name="Test Borough",
            average_rent=1000,
            latitude=52.52,
            longitude=13.4049,
            geometry_coordinates="POINT (13.404954 52.520008)"
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.52,
            longitude=13.404954
        )

    def test_neighborhood_list_api(self):
        url = reverse('neighborhood-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the name and borough are included in the response data
        self.assertIn('name', response.data[0])
        self.assertEqual(response.data[0]['name'], "Test Neighborhood")

    def test_neighborhood_detail_api(self):
        url = reverse('neighborhood-detail', args=[self.neighborhood.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Confirm the correct details are returned
        self.assertEqual(response.data['name'], "Test Neighborhood")
        self.assertEqual(response.data['borough'], self.borough.pk)  # Ensure borough ID is correct

    def test_neighborhood_list_api_unauthenticated(self):
        # Force no authentication and check for permission denied
        self.client.force_authenticate(user=None)
        url = reverse('neighborhood-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
