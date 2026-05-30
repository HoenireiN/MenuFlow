from django.db import models

from restaurants.models import Restaurant
from menuapp.models import MenuItem


class Review(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True
    )

    customer_name = models.CharField(max_length=120)

    rating = models.PositiveSmallIntegerField(default=5)

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer_name} - {self.rating}/5'
