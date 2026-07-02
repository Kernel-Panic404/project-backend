from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Usuarios y autenticación
    path("api/usuarios/", include("usuarios.urls")),

    # Tutorías
    path("api/tutorias/", include("tutorias.urls")),

    # Cuestionarios
    path("api/cuestionarios/", include("cuestionarios.urls")),
]
