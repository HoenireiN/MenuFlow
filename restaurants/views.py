from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.shortcuts import redirect, render, get_object_or_404

from .models import Restaurant
from menuapp.models import Allergen, Favorite, MenuItem, Category
from reviews.forms import ReviewForm
from reviews.models import Review


def get_language(request):
    language = request.session.get('language', 'tr')

    if language not in ('tr', 'en'):
        return 'tr'

    return language


def set_language(request, language):

    if language in ('tr', 'en'):
        request.session['language'] = language

    return redirect(request.META.get('HTTP_REFERER', 'home'))


def home(request):

    restaurants = Restaurant.objects.filter(is_active=True).order_by(
        'venue_type',
        'name'
    )
    venues_by_type = {
        restaurant.venue_type: restaurant
        for restaurant in restaurants
    }
    main_restaurant = venues_by_type.get('restaurant') or restaurants.first()
    beach_bar = venues_by_type.get('beach_club') or restaurants.filter(
        name__icontains='Beach'
    ).first()
    lobby_cafe = venues_by_type.get('cafe') or restaurants.filter(
        name__icontains='Lobby'
    ).first()

    venue_hotspots = [
        {
            'key': 'main_restaurant',
            'label_en': 'Main Restaurant',
            'label_tr': 'Ana Restoran',
            'venue': main_restaurant,
            'x': 55,
            'y': 21,
            'align': 'center',
        },
        {
            'key': 'beach_bar',
            'label_en': 'Beach Bar',
            'label_tr': 'Plaj Barı',
            'venue': beach_bar,
            'x': 86,
            'y': 59,
            'align': 'right',
        },
        {
            'key': 'lobby_cafe',
            'label_en': 'Lobby Cafe',
            'label_tr': 'Lobi Kafe',
            'venue': lobby_cafe,
            'x': 17,
            'y': 58,
            'align': 'left',
        },
    ]

    return render(
        request,
        'home.html',
        {
            'restaurants': restaurants,
            'venue_hotspots': venue_hotspots,
        }
    )


def restaurant_detail(request, slug):

    language = get_language(request)

    restaurant = get_object_or_404(
        Restaurant,
        slug=slug,
        is_active=True
    )
    table_key = f'table_{restaurant.id}'
    table_number = request.session.get(table_key)

    categories = Category.objects.filter(
        restaurant=restaurant
    ).order_by('display_order', 'name')

    items = MenuItem.objects.filter(
        restaurant=restaurant,
        is_available=True
    ).select_related(
        'category'
    ).prefetch_related(
        'allergens',
        'ingredients'
    ).order_by(
        'category__display_order',
        'title'
    )

    allergen_query = request.GET.get('allergen')

    if allergen_query:
        items = items.filter(
            allergens__name__iexact=allergen_query
        ).distinct()

    favorite_item_ids = []

    if request.user.is_authenticated:
        favorite_item_ids = Favorite.objects.filter(
            user=request.user,
            menu_item__restaurant=restaurant
        ).values_list('menu_item_id', flat=True)

    base_items = MenuItem.objects.filter(
        restaurant=restaurant,
        is_available=True
    ).select_related(
        'category'
    ).prefetch_related(
        'allergens'
    )

    chef_items = base_items.filter(
        is_featured=True
    ).order_by(
        'category__display_order',
        '-price'
    )[:8]

    popular_items = base_items.annotate(
        favorite_count=Count('favorites')
    ).order_by(
        '-favorite_count',
        '-is_featured',
        '-price'
    )[:8]

    new_items = base_items.order_by('-created_at')[:8]
    reviews = Review.objects.filter(
        restaurant=restaurant
    ).select_related('menu_item')[:8]
    review_stats = Review.objects.filter(
        restaurant=restaurant
    ).aggregate(
        average_rating=Avg('rating'),
        review_count=Count('id')
    )

    context = {
        'restaurant': restaurant,
        'is_open_now': restaurant.is_open_now(),
        'table_number': table_number,
        'categories': categories,
        'items': items,
        'allergens': Allergen.objects.order_by('name'),
        'chef_items': chef_items,
        'popular_items': popular_items,
        'new_items': new_items,
        'reviews': reviews,
        'review_form': ReviewForm(restaurant=restaurant),
        'average_rating': review_stats['average_rating'],
        'review_count': review_stats['review_count'],
        'language': language,
        'selected_allergen': allergen_query,
        'favorite_item_ids': favorite_item_ids,
    }

    return render(
        request,
        'restaurant_detail.html',
        context
    )


def set_table(request, slug):

    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)

    if request.method == 'POST':
        table_number = request.POST.get('table_number')

        if table_number:
            try:
                table_number_int = int(table_number)
            except ValueError:
                table_number_int = None

            if table_number_int and 1 <= table_number_int <= restaurant.table_count:
                request.session[f'table_{restaurant.id}'] = table_number_int
            else:
                messages.error(request, f'Table number must be between 1 and {restaurant.table_count}.')

    return redirect('restaurant_detail', slug=slug)


def submit_review(request, slug):

    restaurant = get_object_or_404(Restaurant, slug=slug)

    if request.method != 'POST':
        return redirect('restaurant_detail', slug=slug)

    form = ReviewForm(request.POST, restaurant=restaurant)

    if form.is_valid():
        review = form.save(commit=False)
        review.restaurant = restaurant

        if request.user.is_authenticated and not review.customer_name:
            review.customer_name = request.user.username

        review.save()
        messages.success(request, 'Review submitted successfully.')
    else:
        messages.error(request, 'Please check your review form.')

    return redirect('restaurant_detail', slug=slug)


def menu_item_detail_api(request, item_id):

    language = get_language(request)
    item = get_object_or_404(
        MenuItem.objects.select_related(
            'restaurant',
            'category'
        ).prefetch_related(
            'allergens',
            'ingredients'
        ),
        id=item_id
    )

    return JsonResponse({
        'id': item.id,
        'title': item.localized_title(language),
        'description': item.localized_description(language),
        'price': str(item.price),
        'image': item.image.url if item.image else '',
        'prep_time': item.prep_time,
        'calories': item.calories,
        'is_featured': item.is_featured,
        'is_available': item.is_available,
        'category': item.category.localized_name(language),
        'allergens': [
            {
                'name': allergen.localized_name(language),
                'class': allergen.badge_class,
            }
            for allergen in item.allergens.all()
        ],
        'ingredients': [
            ingredient.localized_name(language)
            for ingredient in item.ingredients.all()
        ],
    })
