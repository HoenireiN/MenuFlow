from django.db import models
from django.conf import settings
from django.db.models import Max
from django.utils import timezone
from django.utils.text import slugify

from restaurants.models import Restaurant


class Category(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    name_tr = models.CharField(max_length=100, blank=True)

    name_en = models.CharField(max_length=100, blank=True)

    description_tr = models.TextField(blank=True)

    description_en = models.TextField(blank=True)

    display_order = models.PositiveIntegerField(default=0)

    description = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ['display_order', 'name']

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


class Allergen(models.Model):

    TRANSLATIONS_TR = {
        'Gluten': 'Gluten',
        'Dairy': 'Süt Ürünü',
        'Nuts': 'Kuruyemiş',
        'Peanuts': 'Yer Fıstığı',
        'Soy': 'Soya',
        'Egg': 'Yumurta',
        'Seafood': 'Deniz Ürünü',
        'Shellfish': 'Kabuklu Deniz Ürünü',
        'Sesame': 'Susam',
        'Mustard': 'Hardal',
        'Celery': 'Kereviz',
        'Sulphites': 'Sülfit',
        'Vegan': 'Vegan',
        'Vegetarian': 'Vejetaryen',
        'Halal': 'Helal',
        'Spicy': 'Acılı',
        'Extra Spicy': 'Çok Acılı',
        'Sugar Free': 'Şekersiz',
        'Lactose Free': 'Laktozsuz',
        'Keto Friendly': 'Keto Uyumlu',
        'High Protein': 'Yüksek Protein',
    }

    BADGE_CLASSES = {
        'Vegan': 'allergen-badge--vegan',
        'Vegetarian': 'allergen-badge--vegetarian',
        'Spicy': 'allergen-badge--spicy',
        'Extra Spicy': 'allergen-badge--extra-spicy',
        'Halal': 'allergen-badge--halal',
        'Gluten': 'allergen-badge--gluten',
        'Dairy': 'allergen-badge--dairy',
        'Seafood': 'allergen-badge--seafood',
        'Shellfish': 'allergen-badge--seafood',
        'Keto Friendly': 'allergen-badge--keto',
        'High Protein': 'allergen-badge--protein',
    }

    name = models.CharField(max_length=100)

    @property
    def badge_class(self):
        return self.BADGE_CLASSES.get(self.name, 'allergen-badge--default')

    def __str__(self):
        return self.name

    @property
    def name_tr(self):
        return self.TRANSLATIONS_TR.get(self.name, self.name)

    def localized_name(self, language):
        if language == 'tr':
            return self.name_tr

        return self.name


class Ingredient(models.Model):

    name_tr = models.CharField(max_length=120)

    name_en = models.CharField(max_length=120)

    class Meta:
        ordering = ['name_en']

    def localized_name(self, language):
        if language == 'en':
            return self.name_en

        return self.name_tr

    def __str__(self):
        return self.name_en


class MenuItem(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)

    title_tr = models.CharField(max_length=200, blank=True)

    title_en = models.CharField(max_length=200, blank=True)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField()

    description_tr = models.TextField(blank=True)

    description_en = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='menu_items/'
    )

    is_available = models.BooleanField(
        default=True
    )

    is_featured = models.BooleanField(
        default=False
    )

    calories = models.IntegerField(
        blank=True,
        null=True
    )

    prep_time = models.IntegerField(
        blank=True,
        null=True
    )

    allergens = models.ManyToManyField(
        Allergen,
        blank=True
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 2

            while MenuItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def localized_title(self, language):
        if language == 'en':
            return self.title_en or self.title

        return self.title_tr or self.title

    def localized_description(self, language):
        if language == 'en':
            return self.description_en or self.description

        return self.description_tr or self.description


class Favorite(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu_item')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.menu_item}'


class Order(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('on_the_way', 'On the way'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orders'
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    table_number = models.PositiveIntegerField(blank=True, null=True)

    room_number = models.CharField(max_length=20, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} - {self.restaurant.name}'

    def estimated_prep_minutes(self):
        prep_time = self.items.aggregate(
            max_prep=Max('menu_item__prep_time')
        )['max_prep']

        return prep_time or 10

    def refresh_status(self, save=True):
        if self.status in ('delivered', 'cancelled'):
            return self.status

        elapsed_minutes = (timezone.now() - self.created_at).total_seconds() / 60
        prep_minutes = self.estimated_prep_minutes()

        if elapsed_minutes >= prep_minutes + 5:
            new_status = 'delivered'
        elif elapsed_minutes >= prep_minutes:
            new_status = 'on_the_way'
        else:
            new_status = self.status if self.status in ('pending', 'preparing', 'ready') else 'pending'

        if new_status != self.status:
            self.status = new_status

            if save:
                self.save(update_fields=['status', 'updated_at'])

        return self.status


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    title = models.CharField(max_length=200)

    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.title}'
