# Technical Documentation

## Design Goals

MenuFlow is designed as a multi-venue hotel dining system. The same owner can manage multiple venues, while guests interact with each venue through its own QR menu.

## Main Request Flow

1. A guest opens the home page and selects a venue.
2. `restaurants.views.restaurant_detail` loads categories, available menu items, allergens, reviews, featured items, popular items, and new items.
3. The guest can add available items to a session-backed cart.
4. `menuapp.views.confirm_order` persists an `Order` and related `OrderItem` rows.
5. Dashboards and guest pages call `Order.refresh_status()` to move orders through time-based statuses.

## Dashboard Scope

Dashboard views are owner-scoped. Queries use `restaurant__owner=request.user` or `restaurant__in=get_owner_venues(request.user)` to prevent owners from editing another owner's venues or menu items.

## Query Efficiency

- Menu and dashboard queries use `select_related` for `restaurant` and `category` relationships.
- Many-to-many relationships like allergens and ingredients use `prefetch_related`.
- Dashboard aggregates use ORM `Count` and `Avg` instead of Python loops where practical.
- API list endpoints are paginated to avoid returning large responses.

## Validation and Data Integrity

- `MenuItem.save()` generates unique slugs.
- `Favorite` uses a unique `(user, menu_item)` constraint.
- `MenuItemForm.clean()` prevents assigning a category from a different venue.
- `ReviewForm.clean_rating()` restricts ratings to 1-5.
- Cart and order views verify venue activity and item availability.

## API Layer

The `api` app exposes read-only viewsets for restaurants, categories, menu items, allergens, ingredients, and reviews. The API supports filtering, search, ordering, and pagination through DRF and django-filter.

## Deployment Configuration

Settings read `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS` from environment variables. Static assets are collected into `STATIC_ROOT`, and the included `Procfile` starts the app through Gunicorn.
