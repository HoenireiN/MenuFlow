from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from restaurants.models import Restaurant
from reviews.models import Review

from .models import Category, MenuItem, Order, OrderItem


class MenuFlowCoreTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username='owner',
            password='pass12345',
            role='OWNER',
        )
        self.guest = User.objects.create_user(
            username='guest',
            password='pass12345',
            role='GUEST',
            room_number='204',
        )
        self.restaurant = Restaurant.objects.create(
            owner=self.owner,
            name='Test Restaurant',
            description='A test venue',
            address='Test Street',
            phone='+90 555 000 00 00',
            email='test@example.com',
            opening_hours='00:00 - 23:59',
            opening_time='00:00',
            closing_time='23:59',
            is_active=True,
        )
        self.category = Category.objects.create(
            restaurant=self.restaurant,
            name='Mains',
            display_order=1,
        )
        self.item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            title='Test Burger',
            description='Fresh test burger',
            price=Decimal('250.00'),
            image='menu_items/default.webp',
            prep_time=1,
            is_available=True,
        )

    def test_restaurant_detail_renders_menu_item(self):
        response = self.client.get(reverse('restaurant_detail', args=[self.restaurant.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Burger')

    def test_closed_restaurant_blocks_add_to_cart(self):
        self.restaurant.is_manually_open = False
        self.restaurant.save(update_fields=['is_manually_open'])

        response = self.client.get(
            reverse('add_to_cart', args=[self.restaurant.slug, self.item.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('carts'), None)

    def test_order_status_auto_progresses_to_on_the_way_and_delivered(self):
        order = Order.objects.create(
            guest=self.guest,
            restaurant=self.restaurant,
            total_price=Decimal('250.00'),
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.item,
            title=self.item.title,
            quantity=1,
            unit_price=self.item.price,
            line_total=self.item.price,
        )

        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=2)
        )
        order.refresh_from_db()

        self.assertEqual(order.refresh_status(save=False), 'on_the_way')

        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=7)
        )
        order.refresh_from_db()

        self.assertEqual(order.refresh_status(save=False), 'delivered')

    def test_owner_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_owner_dashboard_renders_after_login(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('dashboard'), HTTP_HOST='localhost')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Overview')

    def test_api_menu_items_are_paginated_and_searchable(self):
        response = self.client.get('/api/menu-items/?search=burger', HTTP_HOST='localhost')

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
        self.assertEqual(response.json()['results'][0]['title'], 'Test Burger')

    def test_review_submission_validates_rating_range(self):
        response = self.client.post(
            reverse('submit_review', args=[self.restaurant.slug]),
            {
                'customer_name': 'Tester',
                'rating': 6,
                'comment': 'Too high',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)
