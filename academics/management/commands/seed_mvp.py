from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from learning.models import Lesson
from games.models import GameTemplate, Game, GameLevel, Question, QuestionOption, Hint
from rewards.models import Badge
from accounts.models import StudentProfile

class Command(BaseCommand):
    help = "Seeds initial database records matching the TezMindz MVP Scope."

    def handle(self, *args, **options):
        self.stdout.write("Seeding MVP database records...")

        # 1. Create default Class entries
        class_5, _ = Class.objects.get_or_create(
            grade_number=5,
            defaults={
                "name": "Grade 5",
                "class_label": "Class 5",
                "stage": "Olympiad Challenger",
                "age_group": "Age 10 - 11",
                "category": "middle",
            }
        )

        class_8, _ = Class.objects.get_or_create(
            grade_number=8,
            defaults={
                "name": "Grade 8",
                "class_label": "Class 8",
                "stage": "National Champion",
                "age_group": "Age 13 - 14",
                "category": "senior",
            }
        )

        # 2. Create Subjects
        math, _ = Subject.objects.get_or_create(
            title="Mathematics",
            defaults={
                "subtitle": "Numbers • Logic • Geometry",
                "olympiad_code": "IMO (Maths Olympiad)",
                "icon_type": "math",
                "color_theme": {
                    "bg": "bg-[#FFFBEB]",
                    "border": "border-amber-200/70",
                    "badgeBg": "bg-amber-500",
                    "accentText": "text-amber-700",
                    "buttonBg": "bg-amber-100 hover:bg-amber-200 text-amber-900",
                }
            }
        )

        sci, _ = Subject.objects.get_or_create(
            title="Science",
            defaults={
                "subtitle": "Physics • Chemistry • Biology",
                "olympiad_code": "NSO (Science Olympiad)",
                "icon_type": "science",
                "color_theme": {
                    "bg": "bg-[#ECFDF5]",
                    "border": "border-emerald-200/70",
                    "badgeBg": "bg-emerald-500",
                    "accentText": "text-emerald-700",
                    "buttonBg": "bg-emerald-100 hover:bg-emerald-200 text-emerald-900",
                }
            }
        )

        eng, _ = Subject.objects.get_or_create(
            title="English",
            defaults={
                "subtitle": "Grammar • Vocabulary • Comprehension",
                "olympiad_code": "IEO (English Olympiad)",
                "icon_type": "english",
                "color_theme": {
                    "bg": "bg-[#FFF1F2]",
                    "border": "border-rose-200/70",
                    "badgeBg": "bg-rose-500",
                    "accentText": "text-rose-700",
                    "buttonBg": "bg-rose-100 hover:bg-rose-200 text-rose-900",
                }
            }
        )

        # 3. Connect ClassSubjects
        cs_math, _ = ClassSubject.objects.get_or_create(student_class=class_5, subject=math, defaults={"total_modules": 40})
        ClassSubject.objects.get_or_create(student_class=class_5, subject=sci, defaults={"total_modules": 36})
        ClassSubject.objects.get_or_create(student_class=class_5, subject=eng, defaults={"total_modules": 36})
        
        ClassSubject.objects.get_or_create(student_class=class_8, subject=math, defaults={"total_modules": 68})

        # 4. Create Chapter
        chapter, _ = Chapter.objects.get_or_create(
            class_subject=cs_math,
            name="Fractions",
            defaults={"order": 1}
        )

        # 5. Create Concept
        concept, _ = Concept.objects.get_or_create(
            chapter=chapter,
            name="Understanding Fractions",
            defaults={
                "description": "Fractions represent equal parts of a whole. The top number (numerator) tells us how many parts we have, and the bottom number (denominator) tells us how many equal parts the whole is divided into.",
                "real_world_example": "Think of cutting a round pizza into 8 equal slices. If you eat 3 slices, you have eaten 3/8 of the pizza!",
                "order": 1
            }
        )

        # 6. Create Lesson
        Lesson.objects.get_or_create(
            concept=concept,
            title="Introduction to Numerators & Denominators",
            defaults={
                "content_markdown": (
                    "Welcome to Fractions! 🍕\n\n"
                    "A fraction is written as two numbers separated by a line:\n"
                    "- **Numerator (Top)**: Tells us the count of parts we are talking about.\n"
                    "- **Denominator (Bottom)**: Tells us the total number of equal parts in the whole.\n\n"
                    "Let's look at an example: 3/4\n"
                    "This means we have 3 out of 4 equal slices of a cake.\n"
                    "If the numerator equals the denominator (like 4/4), we have 1 whole cake!"
                ),
                "order": 1
            }
        )

        # 7. Create Game Template
        mcq_template, _ = GameTemplate.objects.get_or_create(
            slug="mcq",
            defaults={
                "name": "Multiple Choice Game",
                "description": "A classic quiz template with multiple options and instant correctness feedback."
            }
        )

        # 8. Create Game & Levels
        game, _ = Game.objects.get_or_create(
            concept=concept,
            template=mcq_template,
            title="Fraction Quest",
            defaults={"config": {"time_limit": 60}}
        )

        level_easy, _ = GameLevel.objects.get_or_create(game=game, difficulty="easy", defaults={"xp_reward": 10, "coin_reward": 5})
        level_med, _ = GameLevel.objects.get_or_create(game=game, difficulty="medium", defaults={"xp_reward": 15, "coin_reward": 7})
        level_hard, _ = GameLevel.objects.get_or_create(game=game, difficulty="hard", defaults={"xp_reward": 20, "coin_reward": 10})

        # 9. Create Questions
        levels = [level_easy, level_med, level_hard]
        for lvl in levels:
            q_obj, created = Question.objects.get_or_create(
                game_level=lvl,
                text="Make 3/4 of the pizza",
                defaults={
                    "explanation": "The denominator is 4, representing 4 equal slices. The numerator is 3, representing 3 slices. Putting 3 slices on the plate makes 3/4."
                }
            )
            if created:
                opts = [
                    {"text": "1/4", "is_correct": False, "order": 1},
                    {"text": "2/4", "is_correct": False, "order": 2},
                    {"text": "3/4", "is_correct": True, "order": 3},
                    {"text": "4/4", "is_correct": False, "order": 4},
                ]
                for opt in opts:
                    QuestionOption.objects.create(
                        question=q_obj,
                        text=opt["text"],
                        is_correct=opt["is_correct"],
                        order=opt["order"]
                    )
                
                hints = [
                    "Think about the total number of equal parts in the whole pizza.",
                    "3/4 means three slices are taken — not two.",
                    "Move slices until the plate shows 3 pieces. That’s 3 out of 4."
                ]
                for idx, hint_text in enumerate(hints):
                    Hint.objects.create(
                        question=q_obj,
                        text=hint_text,
                        order=idx + 1
                    )

        # 10. Seed default Badges
        Badge.objects.get_or_create(name="Math Explorer", defaults={"description": "Master your first Mathematics game", "icon": "📐"})
        Badge.objects.get_or_create(name="Science Explorer", defaults={"description": "Master your first Science game", "icon": "🧪"})
        Badge.objects.get_or_create(name="Word Wizard", defaults={"description": "Master your first English game", "icon": "📚"})

        # 11. Create a default Student account for instant testing
        if not User.objects.filter(username="student").exists():
            user = User.objects.create_user(
                username="student",
                email="student@tezmindz.com",
                password="password123",
                first_name="Tez"
            )
            StudentProfile.objects.create(
                user=user,
                student_class=class_5,
                xp=100,
                coins=50,
                streak=3,
                avatar="🌟"
            )
            self.stdout.write("Created default student account: username='student', password='password123'")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
