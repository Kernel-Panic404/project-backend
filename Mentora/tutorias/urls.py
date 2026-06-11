from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet,
    TutorAvailabilityViewSet,
    AvailabilityExceptionViewSet,
    TutoringSessionViewSet,
    TutoringParticipationViewSet,
    TutorSubjectViewSet,
)

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet)
router.register(r"availability", TutorAvailabilityViewSet)
router.register(r"availability-exceptions", AvailabilityExceptionViewSet)
router.register(r"sessions", TutoringSessionViewSet)
router.register(r"participations", TutoringParticipationViewSet)
router.register(r"tutor-subjects", TutorSubjectViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
