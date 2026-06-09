from django.urls import path
from .views import TutoriaListCreateView


urlpatterns = [
    path(
        "",
        TutoriaListCreateView.as_view(),
        name="tutoria-list"
    ),
]