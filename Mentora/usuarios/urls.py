from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    UsuarioCreateView,
    UsuarioListView,
    UsuarioDetailView,
    UsuarioDeleteView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UsuarioCreateView.as_view(), name="register"),
    path("", UsuarioListView.as_view(), name="usuario-list"),
    path("<int:usuario_id>/", UsuarioDetailView.as_view(), name="usuario-detail"),
    path("<int:usuario_id>/delete/", UsuarioDeleteView.as_view(), name="usuario-delete"),
]
