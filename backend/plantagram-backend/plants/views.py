from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Plant
from .serializers import PlantListSerializer, PlantDetailSerializer

class PlantPagination(PageNumberPagination):
    """
    Pagination for plant list (30 plants per page)
    """
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])  # Anyone can view plants
def plant_list(request):
    """
    Get list of all plants with pagination
    
    GET /api/plants/
    GET /api/plants/?page=2
    GET /api/plants/?page_size=50
    
    Query Parameters:
    - page: Page number (default 1)
    - page_size: Results per page (default 30, max 100)
    """
    plants = Plant.objects.all().order_by('name')
    
    # Pagination
    paginator = PlantPagination()
    paginated_plants = paginator.paginate_queryset(plants, request)
    
    serializer = PlantListSerializer(paginated_plants, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def plant_detail(request, plant_id):
    """
    Get detailed information about a specific plant
    
    GET /api/plants/<id>/
    
    Returns:
    - Full plant information including care tips
    """
    try:
        plant = Plant.objects.get(id=plant_id)
    except Plant.DoesNotExist:
        return Response(
            {'error': 'Plant not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = PlantDetailSerializer(plant)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def plant_search(request):
    """
    Search plants by name (English or Urdu)
    
    GET /api/plants/search/?q=rose
    GET /api/plants/search/?q=گلاب
    
    Query Parameters:
    - q: Search query (required)
    """
    query = request.query_params.get('q', '')
    
    if not query:
        return Response(
            {'error': 'Search query parameter "q" is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Search in name, name_urdu, scientific_name, common_names
    plants = Plant.objects.filter(
        Q(name__icontains=query) |
        Q(name_urdu__icontains=query) |
        Q(scientific_name__icontains=query) |
        Q(common_names__icontains=query)
    ).order_by('name')
    
    # Pagination
    paginator = PlantPagination()
    paginated_plants = paginator.paginate_queryset(plants, request)
    
    serializer = PlantListSerializer(paginated_plants, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def plant_filter_by_category(request):
    """
    Filter plants by category
    
    GET /api/plants/filter/?category=Succulent
    GET /api/plants/filter/?category=Flowering
    
    Query Parameters:
    - category: Plant category (required)
    
    Available categories:
    Flowering, Foliage, Succulent, Cactus, Herb, Vegetable, Fruit, Tree, Vine, Fern
    """
    category = request.query_params.get('category', '')
    
    if not category:
        return Response(
            {'error': 'Category parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    plants = Plant.objects.filter(category=category).order_by('name')
    
    if not plants.exists():
        return Response(
            {'message': f'No plants found in category: {category}', 'results': []},
            status=status.HTTP_200_OK
        )
    
    # Pagination
    paginator = PlantPagination()
    paginated_plants = paginator.paginate_queryset(plants, request)
    
    serializer = PlantListSerializer(paginated_plants, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def plant_categories(request):
    """
    Get list of all available plant categories
    
    GET /api/plants/categories/
    
    Returns:
    - List of categories with plant counts
    """
    from django.db.models import Count
    
    categories = Plant.objects.values('category').annotate(
        count=Count('id')
    ).order_by('category')
    
    return Response({
        'categories': list(categories)
    }, status=status.HTTP_200_OK)