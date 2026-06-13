from rest_framework.permissions import BasePermission


class IsEstudiante(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == "estudiante"
        )


class IsTutor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == "tutor"
        )


class IsProfesor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == "profesor"
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.rol and
            request.user.rol.nombre == "admin"
        )
