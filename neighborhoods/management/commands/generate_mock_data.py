from django.core.management.base import BaseCommand
from neighborhoods.models import CrimeData, Demographics, RentData, Amenity, Neighborhood
import random
import datetime

class Command(BaseCommand):
    help = 'Generate mock data for neighborhoods'

    def handle(self, *args, **options):
        # Your mock data generation logic here
        neighborhoods = Neighborhood.objects.all()

        # Example mock data generation
        for neighborhood in neighborhoods:
            RentData.objects.create(
                neighborhood=neighborhood,
                average_rent=random.uniform(500, 1500),
                median_rent=random.uniform(400, 1400),
                min_rent=random.uniform(300, 1300),
                max_rent=random.uniform(600, 1600),
                date_collected=datetime.date.today()
            )
            CrimeData.objects.create(
                neighborhood=neighborhood,
                crime_rate=random.uniform(0, 100),
                crime_type="Theft",
                date_collected=datetime.date.today()
            )
            Demographics.objects.create(
                neighborhood=neighborhood,
                family_friendly_percentage=random.uniform(10, 50),
                foreign_residents_percentage=random.uniform(5, 40),
                median_income=random.uniform(20000, 50000),
                age_distribution={"0-18": 20, "19-35": 30, "36-60": 25, "60+": 25}
            )
            Amenity.objects.create(
                neighborhood=neighborhood,
                amenity_type="School",
                count=random.randint(1, 10),
                name="Sample School",
                latitude=random.uniform(-90, 90),
                longitude=random.uniform(-180, 180)
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated mock data'))
