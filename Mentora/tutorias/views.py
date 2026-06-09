from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Tutoria
from .serializers import TutoriaSerializer
from .services import AgendamientoService


class TutoriaListCreateView(APIView):

    def get(self, request):
        tutorias = Tutoria.objects.all()

        serializer = TutoriaSerializer(
            tutorias,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = TutoriaSerializer(
            data=request.data
        )

        if serializer.is_valid():

            try:

                AgendamientoService.validar_conflictos(
                    estudiante=serializer.validated_data["estudiante"],
                    tutor=serializer.validated_data["tutor"],
                    fecha=serializer.validated_data["fecha"],
                    hora=serializer.validated_data["hora"],
                )

                serializer.save()

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            except ValueError as e:

                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )