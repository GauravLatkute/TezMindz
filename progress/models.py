from django.db import models
from django.utils import timezone
from accounts.models import StudentProfile


class StudentTopicProgress(models.Model):
    """Tracks the student's complete sequential learning journey for each topic."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="topic_progresses")
    concept = models.ForeignKey("academics.Concept", on_delete=models.CASCADE, related_name="student_topic_progresses")
    
    # 1. Unlocked Status (Topic availability in Chapter)
    is_unlocked = models.BooleanField(default=False, help_text="Whether this topic is accessible to the student")
    
    # 2. Learn Step
    learn_completed = models.BooleanField(default=False)
    learn_completed_at = models.DateTimeField(null=True, blank=True)
    
    # 3. Game Step
    game_unlocked = models.BooleanField(default=False)
    game_completed = models.BooleanField(default=False)
    game_score = models.PositiveIntegerField(default=0)
    game_completed_at = models.DateTimeField(null=True, blank=True)
    
    # 4. Quiz Step
    quiz_unlocked = models.BooleanField(default=False)
    quiz_completed = models.BooleanField(default=False)
    quiz_score = models.PositiveIntegerField(default=0)
    quiz_total_marks = models.PositiveIntegerField(default=0)
    quiz_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Performance & Rewards
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    hints_used = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    coins_earned = models.PositiveIntegerField(default=0)
    mastery_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_mastered = models.BooleanField(default=False)
    
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "concept")
        verbose_name = "Student Topic Progress"
        verbose_name_plural = "Student Topic Progresses"
        ordering = ["concept__order"]

    def __str__(self):
        status = "Mastered" if self.is_mastered else ("Quiz Ready" if self.quiz_unlocked else ("Game Ready" if self.game_unlocked else "In Learn"))
        return f"{self.student.user.username} — {self.concept.name} [{status}]"

    def mark_learn_complete(self, xp=15):
        """Completes the Learn phase and unlocks the Game phase."""
        self.learn_completed = True
        self.learn_completed_at = timezone.now()
        self.game_unlocked = True
        self.xp_earned += xp
        self._calculate_mastery()
        self.save()

    def mark_game_complete(self, score=100, accuracy=100.0, xp=20, coins=10, hints=0):
        """Completes the Game phase and unlocks the Quiz phase."""
        self.game_completed = True
        self.game_completed_at = timezone.now()
        self.game_score = max(self.game_score, score)
        self.quiz_unlocked = True
        self.xp_earned += xp
        self.coins_earned += coins
        self.hints_used += hints
        self._calculate_mastery(new_accuracy=accuracy)
        self.save()

    def mark_quiz_complete(self, score=0, total_marks=0, percentage=0.0, xp=30, coins=15, hints=0):
        """Completes the Quiz phase, recalculates mastery, and marks topic mastered."""
        self.quiz_completed = True
        self.quiz_completed_at = timezone.now()
        self.quiz_score = score
        self.quiz_total_marks = total_marks
        self.xp_earned += xp
        self.coins_earned += coins
        self.hints_used += hints
        self._calculate_mastery(new_accuracy=percentage)
        
        # Consider topic mastered if quiz passed (e.g. >= 60%) or completed
        if percentage >= 60.0 or score > 0:
            self.is_mastered = True
            self.unlock_next_topic()
            
        self.save()

    def _calculate_mastery(self, new_accuracy=None):
        """Computes comprehensive mastery % out of 100."""
        score = 0.0
        if self.learn_completed:
            score += 25.0
        if self.game_completed:
            score += 35.0
        if self.quiz_completed:
            score += 40.0
            
        if new_accuracy is not None:
            if self.accuracy > 0:
                self.accuracy = (float(self.accuracy) + float(new_accuracy)) / 2.0
            else:
                self.accuracy = float(new_accuracy)
                
        self.mastery_percentage = min(score, 100.0)

    def unlock_next_topic(self):
        """Unlocks the next topic in the chapter for this student."""
        next_concept = self.concept.chapter.concepts.filter(
            order__gt=self.concept.order,
            is_active=True
        ).order_by("order").first()
        
        if next_concept:
            tp, created = StudentTopicProgress.objects.get_or_create(
                student=self.student,
                concept=next_concept,
                defaults={"is_unlocked": True}
            )
            if not created and not tp.is_unlocked:
                tp.is_unlocked = True
                tp.save(update_fields=["is_unlocked"])


class ConceptMastery(models.Model):
    """Tracks how well a student has mastered a given Concept/Topic."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="masteries")
    concept = models.ForeignKey("academics.Concept", on_delete=models.CASCADE, related_name="student_masteries")
    mastery_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)   # 0–100
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    attempts_count = models.PositiveIntegerField(default=0)
    completed_games_count = models.PositiveIntegerField(default=0)
    last_attempt_date = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "concept")
        verbose_name_plural = "Concept Masteries"

    def __str__(self):
        return f"{self.student.user.username} — {self.concept.name} ({self.mastery_score}%)"


class LessonProgress(models.Model):
    """Tracks per-lesson completion for each student."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey("learning.Lesson", on_delete=models.CASCADE, related_name="student_progress")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    xp_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "lesson")
        verbose_name_plural = "Lesson Progress Records"

    def __str__(self):
        status = "Done" if self.completed else "In Progress"
        return f"{self.student.user.username} — {self.lesson.title} [{status}]"

    def mark_complete(self, xp=10):
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.xp_earned = xp
            self.save()


class QuizAttempt(models.Model):
    """Records every quiz attempt a student makes."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey("academics.Quiz", on_delete=models.CASCADE, related_name="attempts")
    score = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    time_taken = models.PositiveIntegerField(default=0, help_text="Seconds")
    passed = models.BooleanField(default=False)
    xp_earned = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name_plural = "Quiz Attempts"

    def __str__(self):
        return f"{self.student.user.username} — {self.quiz.title} ({self.percentage}%)"
