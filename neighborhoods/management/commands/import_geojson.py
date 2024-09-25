import json
from django.core.management.base import BaseCommand
from neighborhoods.models import Neighborhood

class Command(BaseCommand):
    help = 'Import neighborhood data from GeoJSON'

    def handle(self, *args, **kwargs):
        with open('static/geojson/berlin_neighborhoods.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for feature in data['features']:
            neighborhood_name = feature['properties']['name']  # No encoding/decoding necessary

            try:
                # Find neighborhood in the database
                neighborhood = Neighborhood.objects.get(name=neighborhood_name)
                
                # Extract the first point from the Polygon or MultiPolygon coordinates
                if feature['geometry']['type'] == 'Polygon':
                    first_coordinate = feature['geometry']['coordinates'][0][0]  # First point of the polygon
                elif feature['geometry']['type'] == 'MultiPolygon':
                    first_coordinate = feature['geometry']['coordinates'][0][0][0]  # First point of the first polygon
                
                # Update latitude and longitude with the extracted point
                neighborhood.latitude = first_coordinate[1]  # Latitude (2nd element)
                neighborhood.longitude = first_coordinate[0]  # Longitude (1st element)
                
                neighborhood.save()
                self.stdout.write(self.style.SUCCESS(f'Updated neighborhood: {neighborhood_name}'))
            except Neighborhood.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Neighborhood not found in DB: {neighborhood_name}'))

        self.stdout.write(self.style.SUCCESS('Import completed successfully'))
