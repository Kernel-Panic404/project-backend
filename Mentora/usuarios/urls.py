from django.urls import path
from .views import HolaMundoView, UsuarioListView, UsuarioDetailView

urlpatterns = [
    path("hola-mundo/", HolaMundoView.as_view(), name="hola-mundo"),
    path("", UsuarioListView.as_view(), name="usuario-list"),
    path("<int:usuario_id>/", UsuarioDetailView.as_view(), name="usuario-detail"),
]
