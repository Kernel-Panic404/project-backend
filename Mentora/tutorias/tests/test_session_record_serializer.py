import pytest
from rest_framework import serializers

from tutorias.serializers import SessionRecordSerializer


class TestSessionRecordSerializer:

    def test_grade_valid(self):

        serializer = SessionRecordSerializer()

        result = serializer.validate_grade(4.5)

        assert result == 4.5
    
    def test_grade_below_minimum(self):

        serializer = SessionRecordSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_grade(0.5)
    
    def test_grade_above_maximum(self):

        serializer = SessionRecordSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_grade(5.5)

    def test_observation_valid(self):

        serializer = SessionRecordSerializer()

        text = "Buen desempeño en la tutoría"

        result = serializer.validate_observations(text)

        assert result == text
    
    def test_observation_too_long(self):

        serializer = SessionRecordSerializer()

        text = "a" * 1001

        with pytest.raises(serializers.ValidationError):
            serializer.validate_observations(text)
    
    def test_grade_negative(self):

        serializer = SessionRecordSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_grade(-2.5)

    def test_grade_extremely_large(self):

        serializer = SessionRecordSerializer()

        with pytest.raises(serializers.ValidationError):
            serializer.validate_grade(999999)
    
    def test_observation_exactly_1000_characters(self):

        serializer = SessionRecordSerializer()

        text = "a" * 1000

        result = serializer.validate_observations(text)

        assert result == text

    def test_grade_equal_maximum(self):

        serializer = SessionRecordSerializer()

        result = serializer.validate_grade(5.0)

        assert result == 5.0
    
    def test_grade_equal_minimum(self):

        serializer = SessionRecordSerializer()

        result = serializer.validate_grade(1.0)

        assert result == 1.0