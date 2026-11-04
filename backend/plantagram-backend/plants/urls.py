from django.urls import path
from . import views

urlpatterns = [
    # Plant list
    path('', views.plant_list, name='plant-list'),
    
    # Plant detail
    path('<int:plant_id>/', views.plant_detail, name='plant-detail'),
    
    # Search
    path('search/', views.plant_search, name='plant-search'),
    
    # Filter by category
    path('filter/', views.plant_filter_by_category, name='plant-filter'),
    
    # Categories list
    path('categories/', views.plant_categories, name='plant-categories'),
]