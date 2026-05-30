release: python manage.py migrate && python manage.py seed_menu && python manage.py seed_reviews
web: gunicorn smartmenu.wsgi:application
