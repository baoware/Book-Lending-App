from django.apps import AppConfig
from django.db.models.signals import post_save


class UsersConfig(AppConfig):
    """Configuration for Users App"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """Connect the signal to automatically create a UserProfile when a User is created."""
        # Import signals here to ensure it happens after apps are fully loaded
        import users.signals
