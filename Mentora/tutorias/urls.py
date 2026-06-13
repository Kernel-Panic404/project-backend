from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationListView,
    SubjectViewSet,
    TutorAvailabilityViewSet,
    AvailabilityExceptionViewSet,
    TutoringSessionViewSet,
    TutoringParticipationViewSet,
    TutorSubjectViewSet,
    SessionRecordViewSet,
    AttendanceViewSet,
    StudentHistoryView,
    GenerateReminderView,
)

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet)
router.register(r"availability", TutorAvailabilityViewSet)
router.register(r"availability-exceptions", AvailabilityExceptionViewSet)
router.register(r"sessions", TutoringSessionViewSet)
router.register(r"participations", TutoringParticipationViewSet)
router.register(r"tutor-subjects", TutorSubjectViewSet)
router.register(r"session-records", SessionRecordViewSet)
router.register(r"attendance", AttendanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("history/student/<int:student_id>/", StudentHistoryView.as_view(), name="student-history"),
    path("reminders/generate/", GenerateReminderView.as_view(), name="generate-reminders"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
]
