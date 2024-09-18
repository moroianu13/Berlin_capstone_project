from django.shortcuts import render
from .models import Neighborhood

def neighborhood_list(request):
    # Get filter parameters from the request
    max_rent = request.GET.get('max_rent')
    max_crime = request.GET.get('max_crime')
    min_infrastructure = request.GET.get('min_infrastructure')

    # Start with all neighborhoods
    neighborhoods = Neighborhood.objects.all()

    # Apply filters if present
    if max_rent:
        neighborhoods = neighborhoods.filter(rent_price__lte=max_rent)
    if max_crime:
        neighborhoods = neighborhoods.filter(crime_rate__lte=max_crime)
    if min_infrastructure:
        neighborhoods = neighborhoods.filter(infrastructure_score__gte=min_infrastructure)

    return render(request, 'neighborhoods/neighborhood_list.html', {'neighborhoods': neighborhoods})
