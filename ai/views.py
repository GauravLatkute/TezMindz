from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from academics.models import Concept
from games.models import Question, QuestionOption
from ai.services import AIService

class AIExplainConceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        concept_id = request.data.get("concept_id")
        if not concept_id:
            return Response(
                {
                    "success": False,
                    "message": "Missing concept_id",
                    "errors": {"concept_id": ["This parameter is required."]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            concept = Concept.objects.get(id=concept_id)
        except Concept.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Concept not found",
                    "errors": {"detail": "Concept does not exist."}
                },
                status=status.HTTP_404_NOT_FOUND
            )

        profile = request.user.profile
        explanation = AIService.explain_concept(concept.name, concept.description, profile.student_class)
        
        return Response({
            "success": True,
            "message": "AI concept explanation generated",
            "data": {
                "concept_name": concept.name,
                "explanation": explanation
            }
        })


class AIFeedbackWrongAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question_id = request.data.get("question_id")
        selected_option_id = request.data.get("selected_option_id")

        if not question_id or not selected_option_id:
            return Response(
                {
                    "success": False,
                    "message": "Missing required fields",
                    "errors": {"detail": "question_id and selected_option_id are required."}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            question = Question.objects.get(id=question_id)
            selected_option = QuestionOption.objects.get(id=selected_option_id, question=question)
        except (Question.DoesNotExist, QuestionOption.DoesNotExist):
            return Response(
                {
                    "success": False,
                    "message": "Invalid IDs provided",
                    "errors": {"detail": "Question or selected option does not exist."}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get correct option
        correct_option = QuestionOption.objects.filter(question=question, is_correct=True).first()
        correct_text = correct_option.text if correct_option else "N/A"

        profile = request.user.profile
        feedback = AIService.explain_wrong_answer(
            question.text,
            selected_option.text,
            correct_text,
            profile.student_class
        )

        return Response({
            "success": True,
            "message": "AI diagnostics feedback generated",
            "data": {
                "question_id": question.id,
                "selected_option": selected_option.text,
                "correct_option": correct_text,
                "feedback": feedback
            }
        })


class AISmartHintView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question_id = request.data.get("question_id")
        attempts_count = int(request.data.get("attempts_count", 0))

        if not question_id:
            return Response(
                {
                    "success": False,
                    "message": "Missing question_id",
                    "errors": {"question_id": ["This parameter is required."]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Question not found",
                    "errors": {"detail": "Question does not exist."}
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(question, "legacy_options"):
            options = list(question.legacy_options.values_list("text", flat=True))
        elif hasattr(question, "options"):
            options = list(question.options.values_list("text", flat=True))
        else:
            options = []
        profile = request.user.profile

        hint = AIService.generate_smart_hint(
            question.text,
            options,
            profile.student_class,
            attempts_count
        )

        return Response({
            "success": True,
            "message": "AI hint generated successfully",
            "data": {
                "question_id": question.id,
                "hint": hint
            }
        })
