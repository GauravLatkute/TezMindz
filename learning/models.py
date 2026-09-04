from django.db import models
from academics.models import Concept

class Lesson(models.Model):
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content_markdown = models.TextField()
    illustration_url = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ("concept", "order")

    def __str__(self):
        return f"{self.concept.name} - Lesson {self.order}: {self.title}"
