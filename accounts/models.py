from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('OWNER', 'Restaurant Owner'),
        ('CUSTOMER', 'Customer'),
        ('GUEST', 'Hotel Guest'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER'
    )

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    full_name = models.CharField(max_length=160, blank=True, default='')

    room_number = models.CharField(max_length=20, blank=True, default='')

    is_active_stay = models.BooleanField(default=False)

    current_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.username
