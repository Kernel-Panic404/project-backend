from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    QuestionnaireViewSet,
    QuestionViewSet,
    QuestionOptionViewSet
)

router = DefaultRouter()

router.register(
    r'questionnaires',
    QuestionnaireViewSet,
    basename='questionnaire'
)

router.register(
    r'questions',
    QuestionViewSet,
    basename='question'
)

router.register(
    r'options',
    QuestionOptionViewSet,
    basename='option'
)

urlpatterns = [
    path('', include(router.urls)),
]
