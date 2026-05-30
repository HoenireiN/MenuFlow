from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal

from restaurants.models import Restaurant
from .models import Favorite, MenuItem, Order, OrderItem


def get_cart(request, restaurant_id):
    carts = request.session.setdefault('carts', {})
    return carts.setdefault(str(restaurant_id), {})


def save_cart(request, restaurant_id, cart):
    carts = request.session.setdefault('carts', {})
    carts[str(restaurant_id)] = cart
    request.session.modified = True


def cart_summary(restaurant, cart):
    item_ids = [int(item_id) for item_id in cart]
    items = MenuItem.objects.filter(
        id__in=item_ids,
        restaurant=restaurant
    ).select_related('category')
    rows = []
    total = Decimal('0')

    for item in items:
        quantity = int(cart.get(str(item.id), 0))
        line_total = item.price * quantity
        total += line_total
        rows.append({
            'item': item,
            'quantity': quantity,
            'line_total': line_total,
        })

    return rows, total


def cart_page(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    cart = get_cart(request, restaurant.id)
    rows, total = cart_summary(restaurant, cart)

    return render(request, 'menuapp/cart.html', {
        'restaurant': restaurant,
        'rows': rows,
        'total': total,
        'table_number': request.session.get(f'table_{restaurant.id}'),
    })


def add_to_cart(request, slug, item_id):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)

    if not restaurant.is_open_now():
        messages.error(request, 'This venue is currently closed.')
        return redirect('restaurant_detail', slug=slug)

    item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant, is_available=True)
    cart = get_cart(request, restaurant.id)
    cart[str(item.id)] = int(cart.get(str(item.id), 0)) + 1
    save_cart(request, restaurant.id, cart)
    messages.success(request, f'{item.title} added to cart.')
    return redirect('restaurant_detail', slug=slug)


def update_cart_item(request, slug, item_id):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    cart = get_cart(request, restaurant.id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart.pop(str(item_id), None)
    else:
        cart[str(item_id)] = quantity

    save_cart(request, restaurant.id, cart)
    return redirect('cart_page', slug=slug)


def remove_cart_item(request, slug, item_id):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    cart = get_cart(request, restaurant.id)
    cart.pop(str(item_id), None)
    save_cart(request, restaurant.id, cart)
    return redirect('cart_page', slug=slug)


def clear_cart(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    save_cart(request, restaurant.id, {})
    return redirect('cart_page', slug=slug)


def confirm_order(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)

    if not restaurant.is_open_now():
        messages.error(request, 'This venue is currently closed.')
        return redirect('cart_page', slug=slug)

    cart = get_cart(request, restaurant.id)
    rows, total = cart_summary(restaurant, cart)

    if not rows:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_page', slug=slug)

    order = Order.objects.create(
        guest=request.user if request.user.is_authenticated else None,
        restaurant=restaurant,
        table_number=request.session.get(f'table_{restaurant.id}'),
        room_number=request.user.room_number if request.user.is_authenticated else '',
        total_price=total,
    )

    for row in rows:
        OrderItem.objects.create(
            order=order,
            menu_item=row['item'],
            title=row['item'].title,
            quantity=row['quantity'],
            unit_price=row['item'].price,
            line_total=row['line_total'],
        )

    if request.user.is_authenticated:
        request.user.current_balance += total
        request.user.save(update_fields=['current_balance'])

    save_cart(request, restaurant.id, {})
    messages.success(request, f'Order #{order.id} placed successfully.')

    if request.user.is_authenticated:
        return redirect('guest_dashboard')

    return redirect('restaurant_detail', slug=slug)


@login_required
def guest_dashboard(request):
    orders = Order.objects.filter(guest=request.user).select_related('restaurant').prefetch_related('items')

    for order in orders:
        order.refresh_status()

    return render(request, 'menuapp/guest_dashboard.html', {
        'orders': orders,
    })


@login_required
def favorites_page(request):

    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related(
        'menu_item',
        'menu_item__restaurant',
        'menu_item__category'
    )

    return render(
        request,
        'menuapp/favorites.html',
        {
            'favorites': favorites
        }
    )


@login_required
def toggle_favorite(request, item_id):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    item = get_object_or_404(MenuItem, id=item_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        menu_item=item
    )

    if not created:
        favorite.delete()

    return JsonResponse({
        'favorited': created,
        'favorites_count': item.favorites.count()
    })
