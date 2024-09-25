from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

# New Lifestyle model
class Lifestyle(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Each lifestyle has a unique name

    def __str__(self):
        return self.name

class Borough(models.Model):
    name = models.CharField(max_length=100, unique=True)
    average_rent = models.FloatField()
    lifestyles = models.ManyToManyField(Lifestyle, blank=True)  # Many-to-many relationship with Lifestyle
    latitude = models.FloatField()
    longitude = models.FloatField()
    geometry_coordinates = models.JSONField()  # For polygon data
    slug = models.SlugField(unique=True, blank=True)  # Added slug field for URLs

    def __str__(self):
        return self.name

    def clean(self):
        # Custom validation for latitude and longitude
        if not (-90 <= self.latitude <= 90):
            raise ValidationError({'latitude': 'Latitude must be between -90 and 90.'})
        if not (-180 <= self.longitude <= 180):
            raise ValidationError({'longitude': 'Longitude must be between -180 and 180.'})

    def save(self, *args, **kwargs):
        # Automatically generate slug if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.name)  # Generates a URL-safe version of the name
        super(Borough, self).save(*args, **kwargs)


class Neighborhood(models.Model):
    name = models.CharField(max_length=100)
    borough = models.ForeignKey(Borough, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

    def clean(self):
        # Custom validation for latitude and longitude
        if not (-90 <= self.latitude <= 90):
            raise ValidationError({'latitude': 'Latitude must be between -90 and 90.'})
        if not (-180 <= self.longitude <= 180):
            raise ValidationError({'longitude': 'Longitude must be between -180 and 180.'})
