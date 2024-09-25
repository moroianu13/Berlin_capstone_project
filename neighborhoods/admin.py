from django.contrib import admin
from .models import Borough, Neighborhood

# Custom admin class for Borough
class BoroughAdmin(admin.ModelAdmin):
    list_display = ('name', 'average_rent', 'latitude', 'longitude')  # Display these fields in the list view
    search_fields = ('name',)  # Enable search by name
    list_filter = ('average_rent',)  # Enable filtering by average rent

# Custom admin class for Neighborhood
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'borough', 'latitude', 'longitude')  # Display these fields in the list view
    search_fields = ('name', 'borough__name')  # Enable search by neighborhood name or borough name
    list_filter = ('borough',)  # Enable filtering by borough

# Register models with custom admin classes
admin.site.register(Borough, BoroughAdmin)
admin.site.register(Neighborhood, NeighborhoodAdmin)
