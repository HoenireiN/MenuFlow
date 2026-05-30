from django.db import models
from django.conf import settings
from django.utils.text import slugify
from datetime import datetime


class Restaurant(models.Model):

    VENUE_TYPES = (
        ('restaurant', 'Restaurant'),
        ('cafe', 'Cafe'),
        ('bar', 'Bar'),
        ('beach_club', 'Beach Club'),
        ('lounge', 'Lounge'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=200)

    name_tr = models.CharField(max_length=200, blank=True)

    name_en = models.CharField(max_length=200, blank=True)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    logo = models.ImageField(
        upload_to='restaurant_logos/',
        blank=True,
        null=True
    )

    description = models.TextField()

    description_tr = models.TextField(blank=True)

    description_en = models.TextField(blank=True)

    address = models.CharField(max_length=255)

    phone = models.CharField(max_length=20)

    email = models.EmailField()

    opening_hours = models.CharField(max_length=100)

    opening_time = models.TimeField(blank=True, null=True)

    closing_time = models.TimeField(blank=True, null=True)

    is_manually_open = models.BooleanField(default=True)

    venue_type = models.CharField(
        max_length=30,
        choices=VENUE_TYPES,
        default='restaurant'
    )

    table_count = models.PositiveIntegerField(default=40)

    is_active = models.BooleanField(default=True)

    theme_color = models.CharField(
        max_length=20,
        default='#f59e0b'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def localized_name(self, language):
        if language == 'en':
            return self.name_en or self.name

        return self.name_tr or self.name

    def localized_description(self, language):
        if language == 'en':
            return self.description_en or self.description

        return self.description_tr or self.description

    def is_open_now(self):
        if not self.is_active or not self.is_manually_open:
            return False

        if self.opening_time and self.closing_time:
            now = datetime.now().time()

            if self.opening_time <= self.closing_time:
                return self.opening_time <= now <= self.closing_time

            return now >= self.opening_time or now <= self.closing_time

        hours = (self.opening_hours or '').replace(' ', '')

        if '-' not in hours:
            return None

        opening, closing = hours.split('-', 1)

        try:
            opening_time = datetime.strptime(opening, '%H:%M').time()
            closing_time = datetime.strptime(closing, '%H:%M').time()
        except ValueError:
            return None

        now = datetime.now().time()

        if opening_time <= closing_time:
            return opening_time <= now <= closing_time

        return now >= opening_time or now <= closing_time
