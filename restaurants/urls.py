from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path(
        'language/<str:language>/',
        views.set_language,
        name='set_language'
    ),
    path(
        'restaurant/<slug:slug>/',
        views.restaurant_detail,
        name='restaurant_detail'
    ),
    path(
        'restaurant/<slug:slug>/review/',
        views.submit_review,
        name='submit_review'
    ),
    path(
        'restaurant/<slug:slug>/table/',
        views.set_table,
        name='set_table'
    ),
    path(
        'menu-item/<int:item_id>/detail/',
        views.menu_item_detail_api,
        name='menu_item_detail_api'
    ),
]
