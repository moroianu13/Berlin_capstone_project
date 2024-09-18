from django.db import models

# Create your models here.


class Neighborhood(models.Model):
    name = models.CharField(max_length=255)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    crime_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    foreign_population_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    infrastructure_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)  # For latitude
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)  # For longitude

    def __str__(self):
        return self.name

class Bezirke(models.Model):
    name = models.CharField(max_length=255)
    population = models.IntegerField(null=True, blank=True)
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Area in square km
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name