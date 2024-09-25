import os
import django

# Set up Django settings environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentfinder.settings.py')

# Initialize Django
django.setup()

from neighborhoods.models import Lifestyle

# Create Lifestyle objects
Lifestyle.objects.create(name='family-friendly')
Lifestyle.objects.create(name='cultural')
Lifestyle.objects.create(name='pet-friendly')
Lifestyle.objects.create(name='night-life')
