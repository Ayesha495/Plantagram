from django.db import models

class Plant(models.Model):
    """
    Plant model - stores information about different plant species
    """
    
    # Care level choices
    CARE_LEVEL_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    
    # Sunlight choices
    SUNLIGHT_CHOICES = [
        ('Full Sun', 'Full Sun'),
        ('Partial Sun', 'Partial Sun'),
        ('Indirect Light', 'Indirect Light'),
        ('Low Light', 'Low Light'),
        ('Shade', 'Shade'),
    ]
    
    # Category choices
    CATEGORY_CHOICES = [
        ('Flowering', 'Flowering'),
        ('Foliage', 'Foliage'),
        ('Succulent', 'Succulent'),
        ('Cactus', 'Cactus'),
        ('Herb', 'Herb'),
        ('Vegetable', 'Vegetable'),
        ('Fruit', 'Fruit'),
        ('Tree', 'Tree'),
        ('Vine', 'Vine'),
        ('Fern', 'Fern'),
    ]
    
    # API Reference
    perenual_id = models.IntegerField(unique=True, null=True, blank=True, help_text="Perenual API plant ID")
    
    # Basic information
    name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200, blank=True, null=True)
    common_names = models.TextField(blank=True, null=True, help_text="Comma-separated alternative names")
    description = models.TextField()
    
    # Care information
    care_level = models.CharField(max_length=20, choices=CARE_LEVEL_CHOICES, default='Medium')
    water_frequency_days = models.IntegerField(help_text="How often to water (in days)")
    sunlight = models.CharField(max_length=50, choices=SUNLIGHT_CHOICES)
    
    # Environmental requirements
    temperature_min = models.IntegerField(help_text="Minimum temperature in Celsius")
    temperature_max = models.IntegerField(help_text="Maximum temperature in Celsius")
    humidity_level = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., High, Medium, Low")
    
    # Classification
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Visual
    image_url = models.URLField(blank=True, null=True)
    
    # Additional care tips
    care_tips = models.TextField(blank=True, null=True, help_text="JSON format: tips for caring")
    
    # Popularity flags
    is_popular = models.BooleanField(default=False)
    is_beginner_friendly = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Plant'
        verbose_name_plural = 'Plants'
    
    def __str__(self):
        return self.name