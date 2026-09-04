from django.urls import path
from ai.views import (
    AIExplainConceptView,
    AIFeedbackWrongAnswerView,
    AISmartHintView
)

app_name = "ai"

urlpatterns = [
    path("explain/", AIExplainConceptView.as_view(), name="explain"),
    path("feedback/", AIFeedbackWrongAnswerView.as_view(), name="feedback"),
    path("hint/", AISmartHintView.as_view(), name="hint"),
]
