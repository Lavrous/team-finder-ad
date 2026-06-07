from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile_alias"),
    path("change-password/", views.change_password, name="change_password"),
    path("password-change/", views.change_password, name="change_password_alias"),
    path("list/", views.user_list, name="user_list"),
    path("<int:user_id>/", views.user_details, name="user_details"),
]
