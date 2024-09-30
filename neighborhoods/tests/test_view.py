from django.test import TestCase
from django.urls import reverse
from neighborhoods.models import Neighborhood, Borough, Demographics

class NeighborhoodViewTests(TestCase):

    def setUp(self):
        # Create a test Borough with all required fields
        self.borough = Borough.objects.create(
            name="Test Borough",
            geometry_coordinates={"type": "Point", "coordinates": [13.404954, 52.520008]},  # Use JSON format for geometry_coordinates
            average_rent=1000,  # Set average_rent
            latitude=52.52,     # Set latitude
            longitude=13.4049   # Set longitude
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.52,
            longitude=13.404954
        )
        
        # Create Demographics instance for the neighborhood to prevent NoneType errors
        self.demographics = Demographics.objects.create(
            neighborhood=self.neighborhood,
            family_friendly_percentage=60.0,
            foreign_residents_percentage=20.0,
            median_income=40000.0,
            age_distribution={"0-18": 20, "19-35": 30, "36-60": 25, "60+": 25}
        )

    def test_neighborhood_list_view(self):
        # Use the borough slug in reverse()
        url = reverse('neighborhood_list', args=[self.borough.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'neighborhoods/neighborhood_list.html')  # Use the correct template name
        self.assertIn('neighborhoods', response.context)

    def test_neighborhood_detail_view(self):
        # Use the neighborhood ID instead of slug in reverse()
        url = reverse('neighborhood_detail', args=[self.neighborhood.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'neighborhoods/neighborhood_detail.html')  # Corrected template path
        self.assertIn('neighborhood', response.context)


class BoroughViewTests(TestCase):

    def setUp(self):
        # Create some test Boroughs with all required fields
        self.borough1 = Borough.objects.create(
            name='Borough1',
            average_rent=1000,  # Ensure 'average_rent' is set
            latitude=52.5200,   # Set latitude
            longitude=13.4049,  # Set longitude
            geometry_coordinates={"type": "Point", "coordinates": [13.404954, 52.520008]},  # Use JSON format
        )
        self.borough2 = Borough.objects.create(
            name="Test Borough 2",
            average_rent=1200,  # Ensure 'average_rent' is set
            latitude=52.5210,   # Set latitude
            longitude=13.4059,  # Set longitude
            geometry_coordinates={"type": "Point", "coordinates": [13.405954, 52.521008]},  # Use JSON format
        )

    def test_borough_list_view(self):
        url = reverse('borough_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'neighborhoods/borough_list.html')  # Use the correct template path
        self.assertIn('boroughs', response.context)
        self.assertContains(response, self.borough1.name)
        self.assertContains(response, self.borough2.name)
