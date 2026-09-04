from rest_framework import serializers
from progress.models import ConceptMastery
from academics.serializers import ConceptSerializer

class ConceptMasterySerializer(serializers.ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = ConceptMastery
        fields = [
            "id",
            "concept",
            "mastery_score",
            "accuracy",
            "attempts_count",
            "completed_games_count",
            "last_attempt_date",
        ]
