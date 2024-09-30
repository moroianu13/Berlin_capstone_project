from rest_framework import serializers
from .models import Neighborhood , Borough

class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = '__all__'  # You can specify fields explicitly like ['id', 'name', 'borough'] if needed


class BoroughSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borough
        fields = '__all__'