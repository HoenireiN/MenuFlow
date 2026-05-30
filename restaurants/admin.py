from django.contrib import admin

from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'owner',
        'email',
        'phone',
        'created_at',
    )
    search_fields = (
        'name',
        'name_tr',
        'name_en',
        'description',
        'owner__username',
        'email',
    )
    list_filter = (
        'created_at',
    )
    ordering = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')
