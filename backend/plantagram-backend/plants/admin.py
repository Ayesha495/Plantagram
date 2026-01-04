from django.contrib import admin
from .models import Plant

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_urdu', 'scientific_name', 'category', 'care_level', 'is_popular', 'is_beginner_friendly', 'created_at']
    list_filter = ['category', 'care_level', 'is_beginner_friendly', 'is_popular']
    search_fields = ['name', 'scientific_name', 'common_names']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'name_urdu',  # ← Added name_urdu here
                'scientific_name', 'common_names', 
                'description', 'description_urdu',  # ← Added description_urdu here
                'image_url', 'perenual_id'
            )
        }),
        ('Care Requirements', {
            'fields': ('care_level', 'water_frequency_days', 'sunlight', 'temperature_min', 'temperature_max', 'humidity_level', 'care_tips')
        }),
        ('Classification', {
            'fields': ('category', 'is_popular', 'is_beginner_friendly')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )