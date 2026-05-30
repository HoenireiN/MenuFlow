from django.contrib import admin
from django.utils.html import format_html

from .models import Allergen, Category, Ingredient, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'restaurant',
        'display_order',
    )
    list_filter = (
        'restaurant',
    )
    search_fields = (
        'name',
        'name_tr',
        'name_en',
        'restaurant__name',
    )
    ordering = (
        'display_order',
        'name',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('restaurant')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    list_display = (
        'image_thumbnail',
        'title',
        'category',
        'restaurant',
        'price',
        'is_available',
        'is_featured',
        'prep_time',
        'created_at',
    )
    list_filter = (
        'category',
        'restaurant',
        'is_featured',
        'is_available',
        'created_at',
    )
    search_fields = (
        'title',
        'title_tr',
        'title_en',
        'description',
        'description_tr',
        'description_en',
        'category__name',
        'category__name_tr',
        'category__name_en',
        'restaurant__name',
        'restaurant__name_tr',
        'restaurant__name_en',
    )
    ordering = (
        'category__display_order',
        'title',
    )
    list_select_related = (
        'category',
        'restaurant',
    )
    list_per_page = 50
    date_hierarchy = 'created_at'
    autocomplete_fields = (
        'category',
        'restaurant',
        'allergens',
        'ingredients',
    )
    readonly_fields = (
        'image_preview',
        'created_at',
    )
    actions = (
        'mark_as_featured',
        'remove_featured',
        'mark_available',
        'mark_unavailable',
    )

    fieldsets = (
        ('Core Information', {
            'fields': (
                'restaurant',
                'category',
                'title',
                'title_tr',
                'title_en',
                'slug',
            )
        }),
        ('Descriptions', {
            'fields': (
                'description',
                'description_tr',
                'description_en',
            )
        }),
        ('Pricing & Media', {
            'fields': (
                'price',
                'image',
                'image_preview',
            )
        }),
        ('Menu Metadata', {
            'fields': (
                'is_available',
                'is_featured',
                'calories',
                'prep_time',
                'allergens',
                'ingredients',
                'created_at',
            )
        }),
    )

    @admin.display(description='Image')
    def image_thumbnail(self, obj):
        if not obj.image:
            return '-'

        return format_html(
            '<img src="{}" style="width:54px;height:54px;object-fit:cover;border-radius:10px;" />',
            obj.image.url
        )

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if not obj or not obj.image:
            return 'No image uploaded.'

        return format_html(
            '<img src="{}" style="max-width:260px;max-height:180px;object-fit:contain;border-radius:14px;background:#111827;padding:10px;" />',
            obj.image.url
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category',
            'restaurant',
        ).prefetch_related(
            'allergens',
            'ingredients',
        )

    @admin.action(description='Mark selected items as featured')
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} menu items marked as featured.')

    @admin.action(description='Remove featured from selected items')
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} menu items removed from featured.')

    @admin.action(description='Mark selected items as available')
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} menu items marked as available.')

    @admin.action(description='Mark selected items as unavailable')
    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} menu items marked as unavailable.')


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):

    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'name_en',
        'name_tr',
    )
    search_fields = (
        'name_en',
        'name_tr',
    )
    ordering = ('name_en',)
