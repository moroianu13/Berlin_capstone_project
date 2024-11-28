from django.test import TestCase
from django.core.exceptions import ValidationError
from neighborhoods.models import (
    Lifestyle,
    Borough,
    Neighborhood,
    RentData,
    CrimeData,
    Demographics,
    Amenities,
    Transports,
)


class LifestyleModelTest(TestCase):
    def test_string_representation(self):
        lifestyle = Lifestyle(name="Active")
        self.assertEqual(str(lifestyle), "Active")

    def test_unique_name_constraint(self):
        Lifestyle.objects.create(name="Active")
        lifestyle_duplicate = Lifestyle(name="Active")
        with self.assertRaises(ValidationError):
            lifestyle_duplicate.full_clean()


class BoroughModelTest(TestCase):
    def setUp(self):
        self.borough = Borough(
            name="Test Borough",
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates={},
        )

    def test_string_representation(self):
        self.assertEqual(str(self.borough), "Test Borough")

    def test_slug_generation_on_save(self):
        self.borough.save()
        self.assertEqual(self.borough.slug, "test-borough")

    def test_latitude_validation(self):
        self.borough.latitude = 100  # Invalid latitude
        with self.assertRaises(ValidationError):
            self.borough.full_clean()

    def test_longitude_validation(self):
        self.borough.longitude = 200  # Invalid longitude
        with self.assertRaises(ValidationError):
            self.borough.full_clean()

    def test_unique_name_constraint(self):
        self.borough.save()
        borough_duplicate = Borough(
            name="Test Borough",
            minimum_rent=600,
            latitude=48.8566,
            longitude=2.3522,
            geometry_coordinates={},
        )
        with self.assertRaises(ValidationError):
            borough_duplicate.full_clean()


class NeighborhoodModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates={},
        )
        self.neighborhood = Neighborhood(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )

    def test_string_representation(self):
        self.assertEqual(str(self.neighborhood), "Test Neighborhood")

    def test_slug_generation_on_save(self):
        self.neighborhood.save()
        self.assertEqual(self.neighborhood.slug, "test-neighborhood")

    def test_latitude_validation(self):
        self.neighborhood.latitude = -100  # Invalid latitude
        with self.assertRaises(ValidationError):
            self.neighborhood.full_clean()

    def test_longitude_validation(self):
        self.neighborhood.longitude = -200  # Invalid longitude
        with self.assertRaises(ValidationError):
            self.neighborhood.full_clean()


class RentDataModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates={},
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )
        self.rent_data = RentData(
            neighborhood=self.neighborhood,
            avg_price=1000,
            min_price=800,
            max_price=1200,
            avg_size=50,
            min_size=45,
            max_size=55,
            borough=self.borough,
        )

    def test_string_representation(self):
        self.assertEqual(str(self.rent_data), "Rent Data for Test Neighborhood")


class CrimeDataModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates={},
        )
        self.crime_data = CrimeData.objects.create(
            borough=self.borough,
            total_crimes=100,
            robbery=10,
            total_assaults=20,
            total_thefts=30,
            total_residential_burglary=5,
            total_arson_incidents=2,
            total_vandalism=33,
        )

    def test_string_representation(self):
        self.assertEqual(str(self.crime_data), "Crime Data for Test Borough")

    def test_calculate_percentage_methods(self):
        self.assertEqual(self.crime_data.robbery_percentage, 10.0)
        self.assertEqual(self.crime_data.assaults_percentage, 20.0)
        self.assertEqual(self.crime_data.thefts_percentage, 30.0)
        self.assertEqual(self.crime_data.burglary_percentage, 5.0)
        self.assertEqual(self.crime_data.arson_percentage, 2.0)
        self.assertEqual(self.crime_data.vandalism_percentage, 33.0)

    def test_percentage_with_zero_total_crimes(self):
        self.crime_data.total_crimes = 0
        self.assertEqual(self.crime_data.robbery_percentage, 0.0)


class DemographicsModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates={},
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )
        self.demographics = Demographics(
            borough=self.borough,
            neighborhood=self.neighborhood,
            total=1000,
            germans=800,
            foreigners=200,
            under_6=50,
            six_to_15=100,
            fifteen_to_18=80,
            eighteen_to_27=150,
            twenty_seven_to_45=300,
            forty_five_to_55=150,
            fifty_five_and_more=170,
            eu=50,
            france=10,
            italy=10,
            spain=10,
            poland=10,
            greece=10,
            austria=10,
            romania=10,
            united_kingdom=10,
            former_yougoslavia=10,
            former_soviet_union=10,
            russia=10,
            ukraine=10,
            islamic_countries=50,
            turkey=20,
            iran=10,
            arab_countries_inc_syria=20,
            lebanon=5,
            syria=15,
            vietnam=5,
            usa=5,
            not_clearly_assignable=10,
        )

    def test_string_representation(self):
        self.assertEqual(str(self.demographics), "Demographics for Test Neighborhood")


class AmenitiesModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates={},
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )
        self.amenity = Amenities(
            borough=self.borough,
            neighborhood=self.neighborhood,
            amenity_type="Park",
            name="Central Park",
        )

    def test_string_representation(self):
        self.assertEqual(str(self.amenity), "Amenities in Test Neighborhood")


class TransportsModelTest(TestCase):
    def setUp(self):
        self.borough = Borough.objects.create(
            name="Test Borough",
            minimum_rent=500,
            latitude=52.5200,
            longitude=13.4050,
            geometry_coordinates={},
        )
        self.neighborhood = Neighborhood.objects.create(
            name="Test Neighborhood",
            borough=self.borough,
            latitude=52.5200,
            longitude=13.4050,
        )
        self.transport = Transports(
            borough=self.borough,
            neighborhood=self.neighborhood,
            type="Bus",
            name="Bus 42",
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.transport), "Transport in Test Neighborhood: Bus 42"
        )
