from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    QuestionnaireViewSet,
    QuestionViewSet,
    QuestionOptionViewSet,
    QuestionnaireResultViewSet,
    QuestionnaireResponseViewSet
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

router.register(
    r'results',
    QuestionnaireResultViewSet,
    basename='result'
)

router.register(
    r'responses',
    QuestionnaireResponseViewSet,
    basename='response'
)

urlpatterns = [
    path('', include(router.urls)),
]
