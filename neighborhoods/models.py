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
    minimum_rent = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    geometry_coordinates = models.JSONField()  # For polygon data
    slug = models.SlugField(unique=True, blank=True)  # Added slug field for URLs
    lifestyles = models.ManyToManyField(Lifestyle, blank=True)  # Many-to-many relationship with Lifestyle

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
    slug = models.SlugField(unique=True, blank=True, null=True)

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
        super(Neighborhood, self).save(*args, **kwargs)

class RentData(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    avg_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    avg_size = models.FloatField()
    min_size = models.FloatField()
    max_size = models.FloatField()
    borough = models.ForeignKey(Borough, on_delete=models.CASCADE)

    def __str__(self):
        return f'Rent Data for {self.neighborhood.name}'

class Demographics(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    family_friendly_percentage = models.FloatField()
    foreign_residents_percentage = models.FloatField()
    median_income = models.FloatField()
    age_distribution = models.JSONField()  # e.g., {"0-18": 20, "19-35": 30, "36-60": 25, "60+": 25}

    def __str__(self):
        return f'Demographics for {self.neighborhood.name}'

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

class CrimeData(models.Model):
    borough = models.ForeignKey(Borough, on_delete=models.CASCADE)
    total_crimes = models.IntegerField()
    robbery = models.IntegerField()
    total_assaults = models.IntegerField()
    total_thefts = models.IntegerField()
    total_residential_burglary = models.IntegerField()
    total_arson_incidents = models.IntegerField()
    total_vandalism = models.IntegerField()

    def __str__(self):
        return f'Crime Data for {self.borough.name}'

    def calculate_percentage(self, count):
        """
        Calculate the percentage of a specific crime type relative to total crimes.
        If total_crimes is zero, return 0.0%.
        """
        if self.total_crimes > 0:
            return round((count / self.total_crimes) * 100, 1)
        return 0.0

    @property
    def robbery_percentage(self):
        return self.calculate_percentage(self.robbery)

    @property
    def assaults_percentage(self):
        return self.calculate_percentage(self.total_assaults)

    @property
    def thefts_percentage(self):
        return self.calculate_percentage(self.total_thefts)

    @property
    def burglary_percentage(self):
        return self.calculate_percentage(self.total_residential_burglary)

    @property
    def arson_percentage(self):
        return self.calculate_percentage(self.total_arson_incidents)

    @property
    def vandalism_percentage(self):
        return self.calculate_percentage(self.total_vandalism)
