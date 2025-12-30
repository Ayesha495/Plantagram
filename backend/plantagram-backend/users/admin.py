from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
   """
   Custom admin panel for User model
   """
   list_display = ('email', 'username', 'streak_count', 'total_petal_points', 'league', 'is_staff', 'is_active', 'created_at')
   list_filter = ('is_staff', 'is_active', 'league')
   search_fields = ('email', 'username')
   ordering = ('-created_at',)

   #Fields to display when editting a user
   fieldsets = BaseUserAdmin.fieldsets + (
      ("Plantagram Info", {'fields': ('profile_picture', 'location', 'language_preference')}),
        ("Gamification", {'fields': ('streak_count', 'total_petal_points', 'league')}),
    )