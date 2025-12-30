from django.db import models
from django.contrib.auth.models import AbstractUser
    

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    language_preference = models.CharField(max_length=10, default='en')
    # Gamification fields

    streak_count = models.IntegerField(default=0)
    total_petal_points = models.IntegerField(default=0)
    league = models.CharField(
        max_length=20, 
        default='Bronze',
        choices=[
            ('Bronze', 'Bronze'),
            ('Silver', 'Silver'),
            ('Gold', 'Gold'),
            ('Platinum', 'Platinum'),
            ('Emerald', 'Emerald'),
            ('Ruby', 'Ruby'),
            ('Diamond', 'Diamond'),
        ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
