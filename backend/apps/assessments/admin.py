from django.contrib import admin
from .models import Question, Option, Hint, Quiz, QuizQuestion, QuestionResponse, QuizAttempt 

# Register your models here.
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Hint)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizAttempt)
admin.site.register(QuestionResponse)