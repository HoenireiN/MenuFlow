from django.urls import path

from . import dashboard_views


urlpatterns = [
    path('', dashboard_views.dashboard, name='dashboard'),
    path('qr-code/', dashboard_views.dashboard_qr_code, name='dashboard_qr_code'),
    path('venues/', dashboard_views.dashboard_venues, name='dashboard_venues'),
    path('venues/add/', dashboard_views.venue_create, name='venue_create'),
    path('venues/<int:venue_id>/edit/', dashboard_views.venue_edit, name='venue_edit'),
    path('orders/', dashboard_views.dashboard_orders, name='dashboard_orders'),
    path('orders/<int:order_id>/status/', dashboard_views.update_order_status, name='update_order_status'),
    path('menu/', dashboard_views.dashboard_menu_items, name='dashboard_menu_items'),
    path('menu/add/', dashboard_views.menu_item_create, name='menu_item_create'),
    path('menu/<int:item_id>/edit/', dashboard_views.menu_item_edit, name='menu_item_edit'),
    path('menu/<int:item_id>/delete/', dashboard_views.menu_item_delete, name='menu_item_delete'),
    path('menu/<int:item_id>/toggle/', dashboard_views.toggle_availability, name='toggle_availability'),
    path('ingredients/quick-add/', dashboard_views.quick_add_ingredient, name='quick_add_ingredient'),
    path('categories/', dashboard_views.dashboard_categories, name='dashboard_categories'),
    path('categories/<int:category_id>/delete/', dashboard_views.category_delete, name='category_delete'),
    path('reviews/', dashboard_views.dashboard_reviews, name='dashboard_reviews'),
    path('favorites/', dashboard_views.dashboard_favorites, name='dashboard_favorites'),
    path('settings/', dashboard_views.dashboard_settings, name='dashboard_settings'),
    path('settings/toggle-open/', dashboard_views.toggle_restaurant_open, name='toggle_restaurant_open'),
]
