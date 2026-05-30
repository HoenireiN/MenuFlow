from rest_framework import serializers

from menuapp.models import Allergen, Category, Ingredient, MenuItem
from restaurants.models import Restaurant
from reviews.models import Review


class RestaurantSerializer(serializers.ModelSerializer):
    is_open_now = serializers.BooleanField(read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            'id',
            'name',
            'name_tr',
            'name_en',
            'slug',
            'venue_type',
            'description',
            'description_tr',
            'description_en',
            'opening_hours',
            'table_count',
            'theme_color',
            'is_active',
            'is_open_now',
        )


class CategorySerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'restaurant',
            'restaurant_name',
            'name',
            'name_tr',
            'name_en',
            'description',
            'description_tr',
            'description_en',
            'display_order',
        )


class AllergenSerializer(serializers.ModelSerializer):
    name_tr = serializers.CharField(read_only=True)
    badge_class = serializers.CharField(read_only=True)

    class Meta:
        model = Allergen
        fields = ('id', 'name', 'name_tr', 'badge_class')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name_en', 'name_tr')


class MenuItemSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    allergens = AllergenSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = (
            'id',
            'restaurant',
            'restaurant_name',
            'category',
            'category_name',
            'title',
            'title_tr',
            'title_en',
            'slug',
            'description',
            'description_tr',
            'description_en',
            'price',
            'image_url',
            'is_available',
            'is_featured',
            'calories',
            'prep_time',
            'allergens',
            'ingredients',
        )

    def get_image_url(self, obj):
        request = self.context.get('request')

        if not obj.image:
            return ''

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url


class ReviewSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    menu_item_title = serializers.CharField(source='menu_item.title', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id',
            'restaurant',
            'restaurant_name',
            'menu_item',
            'menu_item_title',
            'customer_name',
            'rating',
            'comment',
            'created_at',
        )
