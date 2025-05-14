from email.policy import default

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from datetime import datetime, timedelta, time
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    ROLE_CHOICES = [
        ('patron', 'Patron'),
        ('librarian', 'Librarian'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patron')

    full_name = models.CharField(max_length=255, blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Automatically set join date

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='changed_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='changed_user_permissions',
        blank=True
    )

    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user.username} Profile'

    def is_librarian(self):
        return self.role == 'librarian'

    def is_patron(self):
        return self.role == 'patron'

@receiver(post_delete, sender=UserProfile)
def delete_profile_pic_from_s3(sender, instance, **kwargs):
    if instance.profile_pic:
        instance.profile_pic.delete(save=False)

def default_time():
    # default to next wednesday at noon
    now = datetime.now()
    days_ahead = (2 - now.weekday()) % 7
    if days_ahead == 0 and now.time() >= time(12, 0):
        days_ahead = 7
    next_wed = now + timedelta(days=days_ahead)
    return datetime.combine(next_wed.date(), time(12, 0))

class BookRequest(models.Model):
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='requests')
    patron = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='outgoing_requests')
    librarian = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_datetime = models.DateTimeField(default=default_time)

    # notification tracking
    notified = models.BooleanField(default=False)

    # in weeks capped at 2 months
    duration = models.PositiveIntegerField(default=1)

    # automatically calculated by the form
    due_date = models.DateTimeField(blank=True, null=True)

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('waiting', 'Waiting'),
        ('denied', 'Denied'),
        ('expired', 'Expired')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

    def clean(self):
        super().clean()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['book', 'patron'],
                condition=~Q(status__in=['denied', 'expired']),
                name='unique_open_request'
            )
        ]

class CollectionsRequest(models.Model):
    collection = models.ForeignKey('catalog.Collection', on_delete=models.CASCADE, related_name='requests')
    patron = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_view_requests')
    librarian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collection_permission_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    # notification tracking
    notified = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('waiting', 'Waiting'),
        ('denied', 'Denied'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

