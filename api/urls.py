from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AllergenViewSet,
    CategoryViewSet,
    IngredientViewSet,
    MenuItemViewSet,
    RestaurantViewSet,
    ReviewViewSet,
)


router = DefaultRouter()
router.register('restaurants', RestaurantViewSet, basename='api-restaurants')
router.register('categories', CategoryViewSet, basename='api-categories')
router.register('menu-items', MenuItemViewSet, basename='api-menu-items')
router.register('allergens', AllergenViewSet, basename='api-allergens')
router.register('ingredients', IngredientViewSet, basename='api-ingredients')
router.register('reviews', ReviewViewSet, basename='api-reviews')


urlpatterns = [
    path('', include(router.urls)),
]
