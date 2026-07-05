from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from usuarios.permissions import IsTutor, IsAdmin

from .models import (
    Questionnaire,
    Question,
    QuestionOption,
    QuestionnaireResult,
    QuestionnaireResponse
)

from .serializers import (
    QuestionnaireSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
    QuestionnaireResultSerializer,
    QuestionnaireResponseSerializer
)


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer

    def get_permissions(self):
        """Cualquiera autenticado puede listar/ver/responder. Solo tutor o admin puede crear/editar/borrar."""
        if self.action in ['list', 'retrieve', 'submit']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), (IsTutor | IsAdmin)()]

    @action(detail=False, methods=['post'])
    def submit(self, request):
        questionnaire_id = request.data.get('questionnaire_id')
        answers = request.data.get('answers', {})
        tutor_id = request.data.get('tutor_id')  # Tutor asociado al resultado

        try:
            questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
        except Questionnaire.DoesNotExist:
            return Response({"error": "Questionnaire not found"}, status=status.HTTP_404_NOT_FOUND)

        student = request.user
        total_raw_score = 0.0
        total_max_score = 0.0

        # Loop through questions of the questionnaire
        questions = Question.objects.filter(questionnaire=questionnaire)

        for q in questions:
            ans_val = answers.get(str(q.id))
            if ans_val is None:
                continue

            response = QuestionnaireResponse(
                questionnaire=questionnaire,
                student=student,
                question=q
            )

            # Determine correct option
            is_correct = False
            max_score = float(q.max_score) if q.max_score is not None else 1.0
            total_max_score += max_score

            if q.question_type in ['multiple_choice', 'boolean']:
                if q.question_type == 'multiple_choice':
                    try:
                        selected_opt = QuestionOption.objects.get(pk=ans_val, question=q)
                        response.selected_option = selected_opt
                        if selected_opt.is_correct:
                            is_correct = True
                    except (QuestionOption.DoesNotExist, ValueError):
                        pass
                elif q.question_type == 'boolean':
                    # Frontend envía True/False; buscar la opción correcta por texto
                    if ans_val is True or str(ans_val).lower() in ['true', 'verdadero', 'si', 'sí']:
                        opt_text = "Verdadero"
                    else:
                        opt_text = "Falso"
                    try:
                        selected_opt = QuestionOption.objects.get(text__iexact=opt_text, question=q)
                        response.selected_option = selected_opt
                        if selected_opt.is_correct:
                            is_correct = True
                    except QuestionOption.DoesNotExist:
                        pass

                response.score = max_score if is_correct else 0.0
                total_raw_score += float(response.score)
            else:
                response.text_response = str(ans_val)
                if q.question_type == 'rating':
                    # rating: el estudiante elige 1-5, se normaliza sobre max_score
                    try:
                        rating_val = float(ans_val)
                        normalized = (rating_val / 5.0) * max_score
                        response.score = round(normalized, 2)
                        total_raw_score += float(response.score)
                    except (ValueError, TypeError):
                        response.score = None
                else:
                    response.score = None

            response.save()

        # Normalizar la nota final a escala de 10
        if total_max_score > 0:
            normalized_score = round((total_raw_score / total_max_score) * 10, 2)
        else:
            normalized_score = 0.0

        # Resolver tutor
        tutor = None
        if tutor_id:
            from usuarios.models import Usuario as UsuarioModel
            try:
                tutor = UsuarioModel.objects.get(pk=tutor_id)
            except UsuarioModel.DoesNotExist:
                pass

        # Save result
        result = QuestionnaireResult.objects.create(
            questionnaire=questionnaire,
            student=student,
            tutor=tutor,
            total_score=normalized_score
        )

        return Response({
            "message": "Questionnaire submitted successfully",
            "result_id": result.id,
            "total_score": normalized_score,
            "total_score_display": f"{normalized_score}/10"
        }, status=status.HTTP_201_CREATED)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), (IsTutor | IsAdmin)()]


class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), (IsTutor | IsAdmin)()]


class QuestionnaireResultViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireResult.objects.all()
    serializer_class = QuestionnaireResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = QuestionnaireResult.objects.all()
        student_id = self.request.query_params.get('student_id')
        questionnaire_id = self.request.query_params.get('questionnaire_id')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if questionnaire_id:
            queryset = queryset.filter(questionnaire_id=questionnaire_id)
            
        return queryset


class QuestionnaireResponseViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireResponse.objects.all()
    serializer_class = QuestionnaireResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = QuestionnaireResponse.objects.all()
        student_id = self.request.query_params.get('student_id')
        questionnaire_id = self.request.query_params.get('questionnaire_id')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if questionnaire_id:
            queryset = queryset.filter(questionnaire_id=questionnaire_id)
            
        return queryset

