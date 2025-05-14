from django.urls import path

from . import views
from .views import dashboard

app_name = "users"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("resources/", views.resources, name="resources"),
    path("browseGuest/", views.browseGuest, name="browseGuest"),
    path("help_page/", views.helpPage, name="help_page"),
    path("manage_patrons/", views.manage_patrons, name="manage_patrons"),
    path("patron_search/", views.patron_search, name="patron_search"),
]