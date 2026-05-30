from rest_framework import permissions, viewsets

from menuapp.models import Allergen, Category, Ingredient, MenuItem
from restaurants.models import Restaurant
from reviews.models import Review

from .serializers import (
    AllergenSerializer,
    CategorySerializer,
    IngredientSerializer,
    MenuItemSerializer,
    RestaurantSerializer,
    ReviewSerializer,
)


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Restaurant.objects.filter(is_active=True).order_by('venue_type', 'name')
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ('venue_type', 'is_active')
    search_fields = ('name', 'name_tr', 'name_en', 'description')
    ordering_fields = ('name', 'venue_type', 'created_at')


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.select_related('restaurant').order_by(
        'restaurant__name',
        'display_order',
        'name',
    )
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ('restaurant',)
    search_fields = ('name', 'name_tr', 'name_en', 'description')
    ordering_fields = ('display_order', 'name')


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(is_available=True).select_related(
        'restaurant',
        'category',
    ).prefetch_related(
        'allergens',
        'ingredients',
    ).order_by('restaurant__name', 'category__display_order', 'title')
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ('restaurant', 'category', 'is_featured')
    search_fields = ('title', 'title_tr', 'title_en', 'description')
    ordering_fields = ('title', 'price', 'prep_time', 'created_at')


class AllergenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Allergen.objects.order_by('name')
    serializer_class = AllergenSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ('name',)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.order_by('name_en')
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ('name_en', 'name_tr')


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.select_related('restaurant', 'menu_item').order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ('restaurant', 'menu_item', 'rating')
    search_fields = ('customer_name', 'comment')
    ordering_fields = ('rating', 'created_at')
