from rest_framework import serializers
from .models import Plant

class PlantListSerializer(serializers.ModelSerializer):
    """
    Serializer for plant list view (minimal data for performance)
    """
    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'name_urdu',
            'scientific_name',
            'category',
            'care_level',
            'image_url',
            'is_beginner_friendly',
            'is_popular',
        ]


class PlantDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for plant detail view (all data)
    """
    class Meta:
        model = Plant
        fields = [
            'id',
            'perenual_id',
            'name',
            'name_urdu',
            'scientific_name',
            'common_names',
            'description',
            'description_urdu',
            'care_level',
            'water_frequency_days',
            'sunlight',
            'temperature_min',
            'temperature_max',
            'humidity_level',
            'category',
            'image_url',
            'care_tips',
            'is_popular',
            'is_beginner_friendly',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']