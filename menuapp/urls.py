from django.urls import path

from . import views


urlpatterns = [
    path('cart/<slug:slug>/', views.cart_page, name='cart_page'),
    path('cart/<slug:slug>/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/<slug:slug>/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/<slug:slug>/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/<slug:slug>/clear/', views.clear_cart, name='clear_cart'),
    path('cart/<slug:slug>/confirm/', views.confirm_order, name='confirm_order'),
    path('guest/dashboard/', views.guest_dashboard, name='guest_dashboard'),
    path(
        'favorites/',
        views.favorites_page,
        name='favorites'
    ),
    path(
        'favorites/toggle/<int:item_id>/',
        views.toggle_favorite,
        name='toggle_favorite'
    ),
]
