from django.test import TestCase
from django.core.exceptions import ValidationError
from neighborhoods.models import Borough, Neighborhood, CrimeData, Demographics, RentData, Amenity

class BoroughModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            average_rent=1000,
            slug="test-borough",
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[13.404954, 52.520008]]]
        )

    def test_borough_creation(self):
        self.assertTrue(isinstance(self.borough, Borough))
        self.assertEqual(self.borough.__str__(), self.borough.name)

    def test_borough_latitude_validation(self):
        self.borough.latitude = 100  # Invalid latitude
        with self.assertRaises(ValidationError):
            self.borough.clean()

    def test_borough_longitude_validation(self):
        self.borough.longitude = 200  # Invalid longitude
        with self.assertRaises(ValidationError):
            self.borough.clean()


class NeighborhoodModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            average_rent=1000,
            slug="test-borough",
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[13.404954, 52.520008]]]
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050
        )

    def test_neighborhood_creation(self):
        self.assertTrue(isinstance(self.neighborhood, Neighborhood))
        self.assertEqual(self.neighborhood.__str__(), self.neighborhood.name)
        self.assertEqual(self.neighborhood.borough.name, "Test Borough")

    def test_neighborhood_latitude_validation(self):
        self.neighborhood.latitude = 100  # Invalid latitude
        with self.assertRaises(ValidationError):
            self.neighborhood.clean()

    def test_neighborhood_longitude_validation(self):
        self.neighborhood.longitude = 200  # Invalid longitude
        with self.assertRaises(ValidationError):
            self.neighborhood.clean()


class CrimeDataModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            average_rent=1000,
            slug="test-borough",
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[13.404954, 52.520008]]]
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050
        )
        self.crime_data = CrimeData.objects.create(
            neighborhood=self.neighborhood,
            crime_type="Burglary",
            crime_rate=2.5,
            date_collected="2023-09-27"
        )

    def test_crime_data_creation(self):
        self.assertTrue(isinstance(self.crime_data, CrimeData))
        self.assertEqual(self.crime_data.neighborhood.name, "Test Neighborhood")
        self.assertEqual(self.crime_data.crime_type, "Burglary")


class DemographicsModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            average_rent=1000,
            slug="test-borough",
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[13.404954, 52.520008]]]
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050
        )
        self.demographics = Demographics.objects.create(
            neighborhood=self.neighborhood,
            family_friendly_percentage=30.5,
            foreign_residents_percentage=20.7,
            median_income=40000,
            age_distribution={"0-18": 20, "19-35": 30, "36-60": 40, "60+": 10}
        )

    def test_demographics_creation(self):
        self.assertTrue(isinstance(self.demographics, Demographics))
        self.assertEqual(self.demographics.neighborhood.name, "Test Neighborhood")
        self.assertEqual(self.demographics.family_friendly_percentage, 30.5)
        self.assertEqual(self.demographics.foreign_residents_percentage, 20.7)


class RentDataModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough 1",
            average_rent=1500,
            slug="test-borough-1",
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[13.404954, 52.520008]]]
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050
        )
        self.rent_data = RentData.objects.create(
            neighborhood=self.neighborhood,
            average_rent=1200,
            median_rent=1000,
            min_rent=800,
            max_rent=1500,
            date_collected="2023-09-27"
        )

    def test_rent_data_creation(self):
        self.assertTrue(isinstance(self.rent_data, RentData))
        self.assertEqual(self.rent_data.neighborhood.name, "Test Neighborhood")
        self.assertEqual(self.rent_data.average_rent, 1200)


class AmenityModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            average_rent=1000,
            slug="test-borough",
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates=[[[13.404954, 52.520008]]]
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050
        )
        self.amenity = Amenity.objects.create(
            neighborhood=self.neighborhood,
            amenity_type="Park",
            name="Test Park",
            count=1,
            latitude=52.5200,
            longitude=13.4050
        )

    def test_amenity_creation(self):
        self.assertTrue(isinstance(self.amenity, Amenity))
        self.assertEqual(self.amenity.neighborhood.name, "Test Neighborhood")
        self.assertEqual(self.amenity.amenity_type, "Park")
        self.assertEqual(self.amenity.name, "Test Park")

    def test_amenity_latitude_validation(self):
        self.amenity.latitude = 100  # Invalid latitude
        with self.assertRaises(ValidationError):
            self.amenity.clean()

    def test_amenity_longitude_validation(self):
        self.amenity.longitude = 200  # Invalid longitude
        with self.assertRaises(ValidationError):
            self.amenity.clean()
