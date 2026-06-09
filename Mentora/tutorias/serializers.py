from rest_framework import serializers
from .models import Tutoria


class TutoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tutoria
        fields = "__all__"