from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from allauth.account.signals import user_signed_up


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for new users who are not staff or superusers."""
    if created and not instance.is_staff and not instance.is_superuser:
        UserProfile.objects.create(user=instance)


@receiver(user_signed_up)
def populate_profile(request, user, **kwargs):
    """
    Triggered when a new user signs up via Allauth (social signup).
    It extracts extra data from the social account and creates
    (or updates) a UserProfile.
    """
    full_name = ""
    # Check if sociallogin extra data is provided (Google)
    sociallogin = kwargs.get('sociallogin')
    if sociallogin:
        extra_data = sociallogin.account.extra_data
        # For Google, the full name is typically under 'name'
        full_name = extra_data.get('name', '')
    else:
        full_name = ''  # Fallback if not using a social provider

    # Use get_or_create to avoid duplicate creation.
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'role': 'patron',      # Default role for regular users
            'full_name': full_name,
            # join_date is automatically set via auto_now_add
        }
    )
    if not created:
        # Optionally update full_name if the profile already existed.
        profile.full_name = full_name
        profile.save()
