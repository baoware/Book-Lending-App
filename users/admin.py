from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'role', 'is_librarian', 'is_patron')
    list_filter = ('role',)
    search_fields = ('user__username',)

    # function to display email
    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'

    # allow role to be edited
    list_editable = ('role',)


admin.site.register(UserProfile, UserProfileAdmin)
