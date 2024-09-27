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


class RentData(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    average_rent = models.FloatField()
    median_rent = models.FloatField()
    min_rent = models.FloatField()
    max_rent = models.FloatField()
    date_collected = models.DateField()

    def __str__(self):
        return f'Rent Data for {self.neighborhood.name} on {self.date_collected}'

# New CrimeData model for crime statistics
class CrimeData(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    crime_rate = models.FloatField()
    crime_type = models.CharField(max_length=50)  # e.g., theft, vandalism
    date_collected = models.DateField()

    def __str__(self):
        return f'Crime Data for {self.neighborhood.name} on {self.date_collected}'

# New Demographics model for population details
class Demographics(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    family_friendly_percentage = models.FloatField()
    foreign_residents_percentage = models.FloatField()
    median_income = models.FloatField()
    age_distribution = models.JSONField()  # e.g., {"0-18": 20, "19-35": 30, "36-60": 25, "60+": 25}

    def __str__(self):
        return f'Demographics for {self.neighborhood.name}'

# New Amenities model for various facilities in neighborhoods
class Amenity(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    amenity_type = models.CharField(max_length=100)  # e.g., "School", "Park", "Hospital", "Metro Station"
    count = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f'{self.amenity_type} - {self.name} in {self.neighborhood.name}'

    def clean(self):
        if not (-90 <= self.latitude <= 90):
            raise ValidationError({'latitude': 'Latitude must be between -90 and 90.'})
        if not (-180 <= self.longitude <= 180):
            raise ValidationError({'longitude': 'Longitude must be between -180 and 180.'})