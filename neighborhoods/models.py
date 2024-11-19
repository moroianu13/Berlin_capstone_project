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
    borough = models.ForeignKey(Borough, on_delete=models.CASCADE)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE)
    total = models.IntegerField()
    germans = models.IntegerField()
    foreigners = models.IntegerField()
    under_6 = models.IntegerField()
    six_to_15 = models.IntegerField()
    fifteen_to_18 = models.IntegerField()
    eighteen_to_27 = models.IntegerField()
    twenty_seven_to_45 = models.IntegerField()
    forty_five_to_55 = models.IntegerField()
    fifty_five_and_more = models.IntegerField()
    eu = models.IntegerField()
    france = models.IntegerField()
    italy = models.IntegerField()
    spain = models.IntegerField()
    poland = models.IntegerField()
    greece = models.IntegerField()
    austria = models.IntegerField()
    romania = models.IntegerField()
    united_kingdom = models.IntegerField()
    former_yougoslavia = models.IntegerField()
    former_soviet_union = models.IntegerField()
    russia = models.IntegerField()
    ukraine = models.IntegerField()
    islamic_countries = models.IntegerField()
    turkey = models.IntegerField()
    iran = models.IntegerField()
    arab_countries_inc_syria = models.IntegerField()
    lebanon = models.IntegerField()
    syria = models.IntegerField()
    vietnam = models.IntegerField()
    usa = models.IntegerField()
    not_clearly_assignable = models.IntegerField()

    def __str__(self):
        return f'Demographics for {self.neighborhood.name}'
    
class CrimeData(models.Model):
    borough = models.ForeignKey(Borough, on_delete=models.CASCADE)
    total_crimes = models.IntegerField()
    roberry = models.IntegerField()
    total_assaults = models.IntegerField()
    total_thefts = models.IntegerField()
    total_residential_burglary = models.IntegerField()
    total_arson_incidents = models.IntegerField()
    total_vandalism = models.IntegerField()

    def __str__(self):
        return f'Crime Data for {self.borough.name}'