import pytest
from rest_framework import serializers

from tutorias.serializers import AttendanceSerializer


class TestAttendanceSerializer:

    def test_present_status_valid(self):

        serializer = AttendanceSerializer()

        result = serializer.validate_status("PRESENTE")

        assert result == "PRESENTE"

    def test_absent_status_valid(self):

        serializer = AttendanceSerializer()

        result = serializer.validate_status("AUSENTE")

        assert result == "AUSENTE"

    def test_late_status_valid(self):

        serializer = AttendanceSerializer()

        result = serializer.validate_status("TARDE")

        assert result == "TARDE"

    def test_empty_status_invalid(self):

        serializer = AttendanceSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_status("")

    def test_random_status_invalid(self):

        serializer = AttendanceSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_status("XYZ")

    def test_number_status_invalid(self):

        serializer = AttendanceSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_status(123)

    def test_lowercase_status_invalid(self):

        serializer = AttendanceSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_status("presente")

    def test_whitespace_status_invalid(self):

        serializer = AttendanceSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_status(" ")

    def test_null_status_invalid(self):

        serializer = AttendanceSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_status(None)

    def test_long_status_invalid(self):

        serializer = AttendanceSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_status(
                "PRESENTE_AUNQUE_LLEGO_TARDE"
            )