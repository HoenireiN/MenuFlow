# MenuFlow

MenuFlow is a Django hotel dining platform for managing multiple restaurant venues from one dashboard. Guests can browse QR menus, filter menu items, view allergen and ingredient information, add items to a cart, place orders, leave reviews, and save favorites. Owners can manage venues, categories, menu items, orders, QR codes, reviews, favorites, opening state, and menu images.

## Features

- Multi-venue restaurant system: main restaurant, beach bar, lobby cafe, and future venues.
- Owner dashboard with overview analytics, QR codes, venue settings, menu CRUD, categories, orders, reviews, and favorites.
- Guest-facing QR menu pages with bilingual Turkish/English content.
- Cart and order workflow with automatic status progression from pending to on the way to delivered.
- Allergen, ingredient, calorie, preparation time, featured item, and availability metadata.
- Authentication with signup, login, logout, owner dashboard permissions, and guest accounts.
- Search and filtering by allergen, venue, category, availability, featured status, image status, and text search.
- AJAX interactions for favorite toggles, availability toggles, quick ingredient creation, and venue open/paused state.
- REST API powered by Django REST Framework with pagination, search, filtering, and ordering.
- Responsive Bootstrap-based UI with dark/light theme support.
- Seed commands for rich demo menu data and natural-looking reviews.

## Tech Stack

- Python 3.12
- Django 6
- Django REST Framework
- django-filter
- crispy-forms with Bootstrap 5
- SQLite for local development
- Pillow for image uploads
- qrcode for venue QR generation

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Run migrations.

```powershell
python manage.py migrate
```

4. Create an admin or owner user.

```powershell
python manage.py createsuperuser
```

5. Seed demo menus and reviews.

```powershell
python manage.py seed_menu
python manage.py seed_reviews
```

6. Start the development server.

```powershell
python manage.py runserver
```

## Demo URLs

- Home and venue map: `http://127.0.0.1:8000/`
- Owner dashboard: `http://127.0.0.1:8000/dashboard/`
- API root: `http://127.0.0.1:8000/api/`
- Admin: `http://127.0.0.1:8000/admin/`

## REST API

The API is read-only and public for menu browsing integrations.

- `/api/restaurants/`
- `/api/categories/`
- `/api/menu-items/`
- `/api/allergens/`
- `/api/ingredients/`
- `/api/reviews/`

Examples:

```text
/api/menu-items/?search=burger
/api/menu-items/?restaurant=1&ordering=price
/api/reviews/?rating=5
```

API responses are paginated with 12 records per page.

## Architecture

- `accounts`: custom user model, authentication, owner/guest roles.
- `restaurants`: venue model, public venue pages, dashboard views, venue forms.
- `menuapp`: categories, menu items, allergens, ingredients, favorites, carts, orders, seed commands.
- `reviews`: customer review model and form.
- `api`: DRF serializers, viewsets, and router URLs.
- `templates`: public pages, account screens, dashboard screens, and menu/cart UI.

## Data Model Summary

- `Restaurant` owns menu venues and stores opening hours, active state, table count, and theme information.
- `Category` belongs to one restaurant.
- `MenuItem` belongs to one restaurant and category, and has many allergens and ingredients.
- `Favorite` links a user to one menu item with a uniqueness constraint.
- `Order` belongs to a restaurant and can contain many `OrderItem` rows.
- `Review` belongs to a restaurant and optionally a menu item.

## Order Status Automation

Orders start as `pending`. When the longest preparation time among the order items passes, the status becomes `on_the_way`. Five minutes later, the order becomes `delivered`. Cancelled and delivered orders are not overwritten.

## Testing

Run the test suite:

```powershell
python manage.py test
```

The tests cover public menu rendering, cart closed-state handling, order status automation, dashboard permissions, dashboard rendering, API pagination/search, and review validation.

## Deployment Notes

For production, set these environment variables:

```text
DJANGO_SECRET_KEY=replace-with-a-secure-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,.onrender.com
```

Then run:

```powershell
python manage.py collectstatic
python manage.py migrate
```

The included `Procfile` can be used as a starting point for Render-style deployment.

## Bonus Features

- Hotel-style multi-venue map and QR menu system.
- Rich seeded menu with allergens, ingredients, calories, prep time, bilingual copy, and images.
- Natural-looking seeded review data.
- Dynamic owner dashboard with venue-wide analytics and QR image generation.
- Automatic order status progression.
