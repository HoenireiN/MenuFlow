from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from menuapp.forms import CategoryForm, MenuItemForm
from menuapp.models import Category, Favorite, Ingredient, MenuItem, Order
from reviews.models import Review

from .forms import VenueForm
from .models import Restaurant


DEFAULT_IMAGE = 'menu_items/default.webp'


def get_owner_restaurant(user):

    return Restaurant.objects.filter(owner=user).first()


def get_owner_venues(user):
    return Restaurant.objects.filter(owner=user).order_by('venue_type', 'name')


def owner_required(view_func):

    @login_required
    def wrapper(request, *args, **kwargs):
        restaurant = get_owner_restaurant(request.user)

        if not restaurant and not request.user.is_staff:
            messages.error(request, 'Only restaurant owners can access dashboard.')
            return redirect('home')

        if not restaurant:
            messages.error(request, 'Create a restaurant before using the dashboard.')
            return redirect('home')

        request.owner_restaurant = restaurant
        return view_func(request, *args, **kwargs)

    return wrapper


def dashboard_context(request, active):

    restaurant = request.owner_restaurant
    venues = get_owner_venues(request.user)
    items = MenuItem.objects.filter(restaurant__in=venues)

    return {
        'restaurant': restaurant,
        'venues': venues,
        'active_nav': active,
        'total_menu_items': items.count(),
        'available_items': items.filter(is_available=True).count(),
        'featured_items': items.filter(is_featured=True).count(),
        'total_categories': Category.objects.filter(restaurant__in=venues).count(),
        'total_reviews': Review.objects.filter(restaurant__in=venues).count(),
        'total_favorites': Favorite.objects.filter(
            menu_item__restaurant__in=venues
        ).count(),
    }


@owner_required
def dashboard(request):

    context = dashboard_context(request, 'overview')
    venues = get_owner_venues(request.user)
    items = MenuItem.objects.filter(restaurant__in=venues)

    context['recent_items'] = items.select_related('restaurant', 'category').order_by('-created_at')[:8]
    context['average_price'] = items.aggregate(avg=Avg('price'))['avg'] or 0
    context['average_rating'] = Review.objects.filter(
        restaurant__in=venues
    ).aggregate(avg=Avg('rating'))['avg'] or 0
    context['top_favorite_items'] = items.annotate(
        favorite_count=Count('favorites')
    ).order_by('-favorite_count', '-is_featured')[:5]
    context['missing_image_items'] = items.filter(
        image=DEFAULT_IMAGE
    ).select_related('restaurant', 'category').order_by('restaurant__name', 'category__display_order', 'title')
    context['custom_image_count'] = items.exclude(image=DEFAULT_IMAGE).count()
    context['missing_image_count'] = context['missing_image_items'].count()
    context['venue_stats'] = []

    for venue in venues:
        venue_items = items.filter(restaurant=venue)
        category_stats = Category.objects.filter(restaurant=venue).annotate(
            item_count=Count('menuitem')
        ).order_by('display_order', 'name')

        context['venue_stats'].append({
            'venue': venue,
            'is_open_now': venue.is_open_now(),
            'item_count': venue_items.count(),
            'review_count': Review.objects.filter(restaurant=venue).count(),
            'average_rating': Review.objects.filter(restaurant=venue).aggregate(avg=Avg('rating'))['avg'] or 0,
            'qr_url': request.build_absolute_uri(reverse('restaurant_detail', args=[venue.slug])),
            'qr_image_url': f"{reverse('dashboard_qr_code')}?venue={venue.id}",
            'category_stats': category_stats,
        })

    return render(request, 'dashboard/overview.html', context)


@owner_required
def dashboard_qr_code(request):

    import qrcode

    venue = get_object_or_404(Restaurant, id=request.GET.get('venue', request.owner_restaurant.id), owner=request.user)
    restaurant_url = request.build_absolute_uri(reverse('restaurant_detail', args=[venue.slug]))
    image = qrcode.make(restaurant_url)
    response = HttpResponse(content_type='image/png')

    if request.GET.get('download') == '1':
        response['Content-Disposition'] = (
            f'attachment; filename="{venue.slug}-qr.png"'
        )

    image.save(response, 'PNG')

    return response


@owner_required
def dashboard_menu_items(request):

    venues = get_owner_venues(request.user)
    items = MenuItem.objects.filter(
        restaurant__in=venues
    ).select_related('restaurant', 'category').prefetch_related('allergens', 'ingredients')

    venue_query = request.GET.get('venue')
    search_query = request.GET.get('search', '').strip()
    category_query = request.GET.get('category')
    availability_query = request.GET.get('availability')
    featured_query = request.GET.get('featured')
    image_query = request.GET.get('image')
    sort_query = request.GET.get('sort', 'category')

    if venue_query:
        items = items.filter(restaurant_id=venue_query)

    if search_query:
        items = items.filter(
            title__icontains=search_query
        ) | items.filter(
            title_tr__icontains=search_query
        ) | items.filter(
            title_en__icontains=search_query
        )

    if category_query:
        items = items.filter(category_id=category_query)

    if availability_query == 'available':
        items = items.filter(is_available=True)
    elif availability_query == 'sold_out':
        items = items.filter(is_available=False)

    if featured_query == 'featured':
        items = items.filter(is_featured=True)
    elif featured_query == 'standard':
        items = items.filter(is_featured=False)

    if image_query == 'custom':
        items = items.exclude(image=DEFAULT_IMAGE)
    elif image_query == 'missing':
        items = items.filter(image=DEFAULT_IMAGE)

    ordering = {
        'category': ('restaurant__name', 'category__display_order', 'title'),
        'title': ('title',),
        'price_asc': ('price',),
        'price_desc': ('-price',),
        'prep_asc': ('prep_time',),
        'prep_desc': ('-prep_time',),
        'newest': ('-created_at',),
        'oldest': ('created_at',),
    }.get(sort_query, ('category__display_order', 'title'))

    context = dashboard_context(request, 'menu_items')
    context['items'] = items.distinct().order_by(*ordering)
    context['categories'] = Category.objects.filter(
        restaurant__in=venues
    ).select_related('restaurant').order_by('restaurant__name', 'display_order', 'name')
    context['filters'] = {
        'venue': venue_query,
        'search': search_query,
        'category': category_query,
        'availability': availability_query,
        'featured': featured_query,
        'image': image_query,
        'sort': sort_query,
    }

    return render(request, 'dashboard/menu_items.html', context)


@owner_required
def menu_item_create(request):

    venues = get_owner_venues(request.user)

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, venues=venues)

        if form.is_valid():
            item = form.save(commit=False)

            if not item.image:
                item.image = DEFAULT_IMAGE

            item.save()
            form.save_m2m()
            messages.success(request, 'Menu item created successfully.')
            return redirect('dashboard_menu_items')
    else:
        selected_venue = venues.filter(id=request.GET.get('venue')).first() or request.owner_restaurant
        form = MenuItemForm(restaurant=selected_venue, venues=venues)

    context = dashboard_context(request, 'menu_items')
    context.update({'form': form, 'page_title': 'Add Menu Item'})
    return render(request, 'dashboard/menu_item_form.html', context)


@owner_required
def menu_item_edit(request, item_id):

    venues = get_owner_venues(request.user)
    item = get_object_or_404(MenuItem, id=item_id, restaurant__in=venues)

    if request.method == 'POST':
        form = MenuItemForm(
            request.POST,
            request.FILES,
            instance=item,
            venues=venues
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully.')
            return redirect('dashboard_menu_items')
    else:
        form = MenuItemForm(instance=item, restaurant=item.restaurant, venues=venues)

    context = dashboard_context(request, 'menu_items')
    context.update({'form': form, 'page_title': 'Edit Menu Item'})
    return render(request, 'dashboard/menu_item_form.html', context)


@owner_required
def menu_item_delete(request, item_id):

    item = get_object_or_404(
        MenuItem,
        id=item_id,
        restaurant__owner=request.user
    )

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted successfully.')
        return redirect('dashboard_menu_items')

    context = dashboard_context(request, 'menu_items')
    context['item'] = item
    return render(request, 'dashboard/menu_item_confirm_delete.html', context)


@owner_required
def toggle_availability(request, item_id):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    item = get_object_or_404(
        MenuItem,
        id=item_id,
        restaurant__owner=request.user
    )
    item.is_available = not item.is_available
    item.save(update_fields=['is_available'])

    return JsonResponse({
        'is_available': item.is_available,
        'label': 'Available' if item.is_available else 'Sold Out'
    })


@owner_required
def quick_add_ingredient(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    name_en = request.POST.get('name_en', '').strip()
    name_tr = request.POST.get('name_tr', '').strip() or name_en

    if not name_en:
        return JsonResponse({'error': 'Ingredient name is required'}, status=400)

    ingredient, created = Ingredient.objects.get_or_create(
        name_en=name_en,
        defaults={
            'name_tr': name_tr,
        }
    )

    if not created and name_tr and ingredient.name_tr != name_tr:
        ingredient.name_tr = name_tr
        ingredient.save(update_fields=['name_tr'])

    return JsonResponse({
        'id': ingredient.id,
        'name_en': ingredient.name_en,
        'name_tr': ingredient.name_tr,
        'label': f'{ingredient.name_en} / {ingredient.name_tr}',
    })


@owner_required
def dashboard_categories(request):

    venues = get_owner_venues(request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST, venues=venues)

        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('dashboard_categories')
    else:
        form = CategoryForm(venues=venues)

    context = dashboard_context(request, 'categories')
    context['categories'] = Category.objects.filter(
        restaurant__in=venues
    ).select_related('restaurant').order_by('restaurant__name', 'display_order', 'name')
    context['form'] = form
    return render(request, 'dashboard/categories.html', context)


@owner_required
def category_delete(request, category_id):

    category = get_object_or_404(
        Category,
        id=category_id,
        restaurant__owner=request.user
    )

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')

    return redirect('dashboard_categories')


@owner_required
def dashboard_reviews(request):

    venues = get_owner_venues(request.user)
    venue_query = request.GET.get('venue')
    reviews = Review.objects.filter(restaurant__in=venues).select_related(
        'restaurant',
        'menu_item',
    )

    if venue_query:
        reviews = reviews.filter(restaurant_id=venue_query)

    context = dashboard_context(request, 'reviews')
    context['reviews'] = reviews
    context['filters'] = {'venue': venue_query}

    return render(request, 'dashboard/reviews.html', context)


@owner_required
def dashboard_favorites(request):

    venues = get_owner_venues(request.user)
    venue_query = request.GET.get('venue')
    favorites = Favorite.objects.filter(
        menu_item__restaurant__in=venues
    ).select_related('user', 'menu_item', 'menu_item__restaurant', 'menu_item__category')

    if venue_query:
        favorites = favorites.filter(menu_item__restaurant_id=venue_query)

    context = dashboard_context(request, 'favorites')
    context['favorites'] = favorites
    context['filters'] = {'venue': venue_query}

    return render(request, 'dashboard/favorites.html', context)


@owner_required
def dashboard_settings(request):

    context = dashboard_context(request, 'settings')
    context['venue_settings'] = [
        {
            'venue': venue,
            'is_open_now': venue.is_open_now(),
        }
        for venue in get_owner_venues(request.user)
    ]
    return render(request, 'dashboard/settings.html', context)


@owner_required
def dashboard_venues(request):

    context = dashboard_context(request, 'venues')
    context['venues'] = Restaurant.objects.filter(
        owner=request.user
    ).order_by('venue_type', 'name')

    return render(request, 'dashboard/venues.html', context)


@owner_required
def venue_create(request):

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)

        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user
            venue.save()
            messages.success(request, 'Venue created successfully.')
            return redirect('dashboard_venues')
    else:
        form = VenueForm()

    context = dashboard_context(request, 'venues')
    context.update({'form': form, 'page_title': 'Create Venue'})
    return render(request, 'dashboard/venue_form.html', context)


@owner_required
def venue_edit(request, venue_id):

    venue = get_object_or_404(Restaurant, id=venue_id, owner=request.user)

    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)

        if form.is_valid():
            form.save()
            messages.success(request, 'Venue updated successfully.')
            return redirect('dashboard_venues')
    else:
        form = VenueForm(instance=venue)

    context = dashboard_context(request, 'venues')
    context.update({'form': form, 'page_title': 'Edit Venue'})
    return render(request, 'dashboard/venue_form.html', context)


@owner_required
def dashboard_orders(request):

    venues = get_owner_venues(request.user)
    orders = Order.objects.filter(
        restaurant__in=venues
    ).select_related('restaurant', 'guest').prefetch_related('items')

    for order in orders:
        order.refresh_status()

    context = dashboard_context(request, 'orders')
    context['orders'] = orders
    return render(request, 'dashboard/orders.html', context)


@owner_required
def update_order_status(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        restaurant__owner=request.user
    )

    if request.method == 'POST':
        status = request.POST.get('status')

        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'Order status updated.')

    return redirect('dashboard_orders')


@owner_required
def toggle_restaurant_open(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    restaurant = get_object_or_404(
        Restaurant,
        id=request.POST.get('venue_id', request.owner_restaurant.id),
        owner=request.user,
    )
    restaurant.is_manually_open = not restaurant.is_manually_open
    restaurant.save(update_fields=['is_manually_open'])

    return JsonResponse({
        'is_open': restaurant.is_manually_open,
        'label': 'Open' if restaurant.is_manually_open else 'Closed',
    })
