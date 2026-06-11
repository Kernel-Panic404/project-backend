from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    UserCreateView,
    UserListView,
    UserDetailView,
    UserDeleteView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:user_id>/delete/", UserDeleteView.as_view(), name="user-delete"),
]
