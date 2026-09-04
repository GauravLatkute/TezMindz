from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify

from academics.models import (
    Class, Subject, ClassSubject, Chapter, Concept,
    Quiz, QuizQuestion, QuizOption, DailyChallenge
)
from learning.models import Lesson
from games.models import GameTemplate, Game, GameLevel, Question, QuestionOption, Hint
from rewards.models import Badge, Achievement, DailyMission
from accounts.models import StudentProfile


class Command(BaseCommand):
    help = "Seeds comprehensive, class-specific curriculum for Classes 1 through 8."

    def handle(self, *args, **options):
        self.stdout.write("Starting curriculum database seed...")

        # ── 1. Create Game Template ──────────────────────────────────────────
        mcq_template, _ = GameTemplate.objects.get_or_create(
            slug="mcq",
            defaults={
                "name": "Multiple Choice Game",
                "description": "Interactive quiz game with visual feedback."
            }
        )

        # ── 2. Create Platform Achievements ──────────────────────────────────
        achievements_data = [
            {"name": "First Step", "desc": "Complete your first lesson", "icon": "🌱", "type": "first_lesson", "val": 1, "xp": 25, "coins": 10},
            {"name": "Quiz Master", "desc": "Pass your first quiz with flying colors", "icon": "🎓", "type": "first_quiz", "val": 1, "xp": 35, "coins": 15},
            {"name": "Game On", "desc": "Play and complete your first educational game", "icon": "🎮", "type": "first_game", "val": 1, "xp": 30, "coins": 15},
            {"name": "Consistent Scholar", "desc": "Maintain a 3-day learning streak", "icon": "🔥", "type": "streak_days", "val": 3, "xp": 50, "coins": 25},
            {"name": "Week Warrior", "desc": "Keep a 7-day continuous streak", "icon": "⚡", "type": "streak_days", "val": 7, "xp": 100, "coins": 50},
            {"name": "Knowledge Collector", "desc": "Complete 5 distinct lessons", "icon": "📚", "type": "lessons_completed", "val": 5, "xp": 75, "coins": 30},
            {"name": "XP Millionaire", "desc": "Accumulate over 500 total XP", "icon": "💎", "type": "xp_total", "val": 500, "xp": 150, "coins": 75},
        ]
        for a in achievements_data:
            Achievement.objects.get_or_create(
                name=a["name"],
                defaults={
                    "description": a["desc"],
                    "icon": a["icon"],
                    "condition_type": a["type"],
                    "condition_value": a["val"],
                    "xp_reward": a["xp"],
                    "coin_reward": a["coins"],
                    "is_active": True
                }
            )

        # ── 3. Subjects Definition ───────────────────────────────────────────
        subjects_data = {
            "math": {
                "title": "Mathematics",
                "subtitle": "Numbers • Logic • Problem Solving",
                "olympiad": "IMO (International Math Olympiad)",
                "icon": "math",
                "color": {"bg": "bg-[#FFFBEB]", "border": "border-amber-200/70", "badgeBg": "bg-amber-500", "accentText": "text-amber-700", "buttonBg": "bg-amber-100"}
            },
            "science": {
                "title": "Science",
                "subtitle": "Physics • Chemistry • Biology",
                "olympiad": "NSO (National Science Olympiad)",
                "icon": "science",
                "color": {"bg": "bg-[#ECFDF5]", "border": "border-emerald-200/70", "badgeBg": "bg-emerald-500", "accentText": "text-emerald-700", "buttonBg": "bg-emerald-100"}
            },
            "english": {
                "title": "English",
                "subtitle": "Grammar • Comprehension • Vocabulary",
                "olympiad": "IEO (International English Olympiad)",
                "icon": "english",
                "color": {"bg": "bg-[#FFF1F2]", "border": "border-rose-200/70", "badgeBg": "bg-rose-500", "accentText": "text-rose-700", "buttonBg": "bg-rose-100"}
            }
        }

        subj_objects = {}
        for k, v in subjects_data.items():
            subj_obj, _ = Subject.objects.get_or_create(
                title=v["title"],
                defaults={
                    "subtitle": v["subtitle"],
                    "olympiad_code": v["olympiad"],
                    "icon_type": v["icon"],
                    "color_theme": v["color"],
                    "is_active": True
                }
            )
            subj_objects[k] = subj_obj

        # ── 4. Curriculum Definition per Class ────────────────────────────────
        curriculum = {
            5: {
                "stage": "Olympiad Challenger", "age": "Age 10 - 11", "category": "middle",
                "subjects": {
                    "math": [
                        {
                            "chapter": "Fractions & Decimals",
                            "order": 1,
                            "desc": "Understanding parts of wholes, equivalence, and arithmetic with decimals.",
                            "concepts": [
                                {
                                    "name": "Understanding Fractions",
                                    "order": 1,
                                    "diff": "easy",
                                    "time": 15,
                                    "desc": "Fractions represent equal parts of a whole with a numerator and denominator.",
                                    "example": "Sharing 3 slices of an 8-slice pizza gives each person 3/8 of the whole pizza.",
                                    "lesson": "Welcome to Fractions! 🍕\n\nA fraction has two key parts:\n- Numerator (top): Number of pieces we have.\n- Denominator (bottom): Total number of equal pieces in the whole.\n\nExample: 3/4 means 3 parts out of 4 total parts.",
                                    "quiz": {
                                        "title": "Fractions Basics Quiz",
                                        "questions": [
                                            {
                                                "text": "What does the denominator in 3/5 represent?",
                                                "marks": 1,
                                                "options": [
                                                    ("The number of parts taken", False),
                                                    ("The total number of equal parts", True),
                                                    ("The multiplier", False),
                                                    ("None of the above", False)
                                                ]
                                            },
                                            {
                                                "text": "Which fraction is equivalent to 1/2?",
                                                "marks": 1,
                                                "options": [
                                                    ("2/4", True),
                                                    ("3/5", False),
                                                    ("2/6", False),
                                                    ("4/10", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Fraction Quest"
                                },
                                {
                                    "name": "Adding & Subtracting Fractions",
                                    "order": 2,
                                    "diff": "medium",
                                    "time": 20,
                                    "desc": "How to add and subtract fractions with common and uncommon denominators.",
                                    "example": "1/4 of an apple + 2/4 of an apple equals 3/4 of an apple.",
                                    "lesson": "Adding like fractions is simple:\nKeep the denominator the same and add the numerators!\n\n1/5 + 2/5 = (1+2)/5 = 3/5.",
                                    "quiz": {
                                        "title": "Fraction Arithmetic Quiz",
                                        "questions": [
                                            {
                                                "text": "What is 2/7 + 3/7?",
                                                "marks": 1,
                                                "options": [
                                                    ("5/14", False),
                                                    ("5/7", True),
                                                    ("6/7", False),
                                                    ("1/7", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Fraction Addition Blitz"
                                }
                            ]
                        },
                        {
                            "chapter": "Factors & Multiples",
                            "order": 2,
                            "desc": "Prime numbers, HCF, LCM and divisibility rules.",
                            "concepts": [
                                {
                                    "name": "Prime and Composite Numbers",
                                    "order": 1,
                                    "diff": "easy",
                                    "time": 15,
                                    "desc": "Prime numbers only have two factors: 1 and itself.",
                                    "example": "7 is prime because only 1 × 7 = 7. 6 is composite because 2 × 3 = 6.",
                                    "lesson": "A Prime Number is a whole number greater than 1 whose only factors are 1 and itself.\nExamples: 2, 3, 5, 7, 11, 13.\n\nNote: 2 is the only even prime number!",
                                    "quiz": {
                                        "title": "Prime Numbers Quiz",
                                        "questions": [
                                            {
                                                "text": "Which of the following is a prime number?",
                                                "marks": 1,
                                                "options": [
                                                    ("9", False),
                                                    ("15", False),
                                                    ("19", True),
                                                    ("21", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Prime Number Pop"
                                }
                            ]
                        }
                    ],
                    "science": [
                        {
                            "chapter": "Plants & Photosynthesis",
                            "order": 1,
                            "desc": "How green plants make food using sunlight, water, and carbon dioxide.",
                            "concepts": [
                                {
                                    "name": "The Photosynthesis Process",
                                    "order": 1,
                                    "diff": "medium",
                                    "time": 15,
                                    "desc": "Chlorophyll in leaves captures sunlight to convert water and CO2 into glucose and oxygen.",
                                    "example": "Plants are like solar-powered food factories for our ecosystem.",
                                    "lesson": "Photosynthesis is the process by which green plants make food.\n\nFormula:\nCarbon Dioxide + Water + Sunlight → Glucose (Sugar) + Oxygen.\n\nChlorophyll is the green pigment in leaves that traps sunlight.",
                                    "quiz": {
                                        "title": "Photosynthesis Quiz",
                                        "questions": [
                                            {
                                                "text": "What gas do plants release during photosynthesis?",
                                                "marks": 1,
                                                "options": [
                                                    ("Carbon Dioxide", False),
                                                    ("Oxygen", True),
                                                    ("Nitrogen", False),
                                                    ("Hydrogen", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Leaf Factory Quest"
                                }
                            ]
                        }
                    ],
                    "english": [
                        {
                            "chapter": "Parts of Speech & Grammar",
                            "order": 1,
                            "desc": "Mastering nouns, pronouns, verbs, adjectives and adverbs.",
                            "concepts": [
                                {
                                    "name": "Nouns and Pronouns",
                                    "order": 1,
                                    "diff": "easy",
                                    "time": 15,
                                    "desc": "Nouns name people, places, things, or ideas. Pronouns replace nouns.",
                                    "example": "Instead of saying 'Riya ran because Riya was late', we say 'Riya ran because she was late.'",
                                    "lesson": "Nouns name people, places, things or ideas.\nPronouns (he, she, it, they, we) replace nouns to avoid repetition.\n\nTypes of Nouns:\n1. Proper (London, Alex)\n2. Common (city, boy)\n3. Collective (flock, team)\n4. Abstract (honesty, courage)",
                                    "quiz": {
                                        "title": "Nouns and Pronouns Quiz",
                                        "questions": [
                                            {
                                                "text": "Identify the pronoun: 'The dog wagged its tail happily.'",
                                                "marks": 1,
                                                "options": [
                                                    ("dog", False),
                                                    ("wagged", False),
                                                    ("its", True),
                                                    ("happily", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Grammar Explorer"
                                }
                            ]
                        }
                    ]
                }
            },
            7: {
                "stage": "Advanced Scholar", "age": "Age 12 - 13", "category": "senior",
                "subjects": {
                    "math": [
                        {
                            "chapter": "Algebraic Expressions",
                            "order": 1,
                            "desc": "Variables, constants, coefficients, and operations on algebraic terms.",
                            "concepts": [
                                {
                                    "name": "Terms, Coefficients & Variables",
                                    "order": 1,
                                    "diff": "medium",
                                    "time": 20,
                                    "desc": "An algebraic expression is formed from variables and constants using arithmetic operations.",
                                    "example": "In 3x + 5, x is the variable, 3 is the numerical coefficient, and 5 is the constant.",
                                    "lesson": "In Algebra:\n- Variable: A symbol having different numerical values (e.g., x, y, z).\n- Constant: A symbol having a fixed numerical value (e.g., 7, -3).\n- Term: A product of factors. In 4xy, 4 is coefficient, x and y are variables.",
                                    "quiz": {
                                        "title": "Algebra Basics Quiz",
                                        "questions": [
                                            {
                                                "text": "In the term -7xy^2, what is the numerical coefficient?",
                                                "marks": 1,
                                                "options": [
                                                    ("7", False),
                                                    ("-7", True),
                                                    ("xy", False),
                                                    ("-1", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Algebra Balance Battle"
                                }
                            ]
                        }
                    ],
                    "science": [
                        {
                            "chapter": "Acids, Bases & Salts",
                            "order": 1,
                            "desc": "Chemical properties of sour and bitter substances and indicators.",
                            "concepts": [
                                {
                                    "name": "Indicators and pH Basics",
                                    "order": 1,
                                    "diff": "hard",
                                    "time": 25,
                                    "desc": "Litmus paper, turmeric, and phenolphthalein change color in acidic and basic solutions.",
                                    "example": "Lemon juice turns blue litmus red because it contains citric acid.",
                                    "lesson": "Acids are sour in taste and turn blue litmus red.\nBases are bitter in taste, feel soapy to touch, and turn red litmus blue.\n\nNeutralisation Reaction:\nAcid + Base → Salt + Water + Heat.",
                                    "quiz": {
                                        "title": "Acids & Bases Quiz",
                                        "questions": [
                                            {
                                                "text": "What happens when blue litmus is dipped into lemon juice?",
                                                "marks": 1,
                                                "options": [
                                                    ("It turns green", False),
                                                    ("It turns red", True),
                                                    ("It remains blue", False),
                                                    ("It turns colorless", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Chemical Color Mixer"
                                }
                            ]
                        }
                    ],
                    "english": [
                        {
                            "chapter": "Active and Passive Voice",
                            "order": 1,
                            "desc": "Transforming sentences between active and passive forms.",
                            "concepts": [
                                {
                                    "name": "Rules of Voice Transformation",
                                    "order": 1,
                                    "diff": "medium",
                                    "time": 20,
                                    "desc": "In active voice, the subject performs the action. In passive voice, the subject receives the action.",
                                    "example": "'The chef cooked the meal' → 'The meal was cooked by the chef.'",
                                    "lesson": "Active Voice: Subject + Verb + Object.\nPassive Voice: Object + Helping Verb + Past Participle (V3) + by + Subject.\n\nExample:\nActive: The cat chased the mouse.\nPassive: The mouse was chased by the cat.",
                                    "quiz": {
                                        "title": "Voice Transformation Quiz",
                                        "questions": [
                                            {
                                                "text": "Convert to Passive: 'Shakespeare wrote Hamlet.'",
                                                "marks": 1,
                                                "options": [
                                                    ("Hamlet was written by Shakespeare.", True),
                                                    ("Hamlet is written by Shakespeare.", False),
                                                    ("Shakespeare was written by Hamlet.", False),
                                                    ("Hamlet had been written by Shakespeare.", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": "Voice Master"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        # ── 5. Populate Curriculum ───────────────────────────────────────────
        today = date.today()

        for grade_num in range(1, 9):
            cls_label = f"Class {grade_num}"
            stage_name = "Primary Explorer" if grade_num <= 4 else ("Olympiad Challenger" if grade_num <= 6 else "National Champion")
            cat = "primary" if grade_num <= 4 else ("middle" if grade_num <= 6 else "senior")

            cls_obj, _ = Class.objects.get_or_create(
                grade_number=grade_num,
                defaults={
                    "name": f"Grade {grade_num}",
                    "class_label": cls_label,
                    "slug": f"class-{grade_num}",
                    "stage": stage_name,
                    "age_group": f"Age {5 + grade_num} - {6 + grade_num}",
                    "category": cat,
                    "is_active": True
                }
            )

            # Daily Challenge per class for today
            DailyChallenge.objects.get_or_create(
                student_class=cls_obj,
                date=today,
                defaults={
                    "title": f"{cls_label} Daily Mind Challenge",
                    "description": f"Solve today's 5 quick questions on {cls_label} topics to earn double XP.",
                    "difficulty": "medium",
                    "xp_reward": 50,
                    "coin_reward": 25,
                    "is_active": True
                }
            )

            # Link 3 core subjects
            for sk, s_obj in subj_objects.items():
                cs_obj, _ = ClassSubject.objects.get_or_create(
                    student_class=cls_obj,
                    subject=s_obj,
                    defaults={"total_modules": 30 + grade_num * 5}
                )

                # Check if specific curriculum defined for this grade and subject
                grade_curr = curriculum.get(grade_num, {}).get("subjects", {}).get(sk, [])
                if not grade_curr:
                    # Provide default placeholder chapter & concept so every class has playable content
                    grade_curr = [
                        {
                            "chapter": f"{s_obj.title} Fundamentals",
                            "order": 1,
                            "desc": f"Core concepts of {s_obj.title} for {cls_label}.",
                            "concepts": [
                                {
                                    "name": f"{s_obj.title} Key Principles",
                                    "order": 1,
                                    "diff": "easy",
                                    "time": 15,
                                    "desc": f"Essential foundation principles of {s_obj.title} at {cls_label} level.",
                                    "example": f"Real-world application for {cls_label} learners.",
                                    "lesson": f"Welcome to {cls_label} {s_obj.title}!\n\nThis foundational unit covers key rules and practical examples.",
                                    "quiz": {
                                        "title": f"{s_obj.title} Quick Quiz",
                                        "questions": [
                                            {
                                                "text": f"What is a primary principle of {cls_label} {s_obj.title}?",
                                                "marks": 1,
                                                "options": [
                                                    ("Accuracy and practice", True),
                                                    ("Guessing quickly", False),
                                                    ("Skipping steps", False),
                                                    ("None of the above", False)
                                                ]
                                            }
                                        ]
                                    },
                                    "game": f"{cls_label} {s_obj.title} Challenge"
                                }
                            ]
                        }
                    ]

                for ch_data in grade_curr:
                    ch_obj, _ = Chapter.objects.get_or_create(
                        class_subject=cs_obj,
                        order=ch_data["order"],
                        defaults={
                            "name": ch_data["chapter"],
                            "description": ch_data["desc"],
                            "slug": slugify(ch_data["chapter"]),
                            "is_active": True
                        }
                    )

                    for c_data in ch_data["concepts"]:
                        conc_obj, _ = Concept.objects.get_or_create(
                            chapter=ch_obj,
                            order=c_data["order"],
                            defaults={
                                "name": c_data["name"],
                                "slug": slugify(c_data["name"]),
                                "description": c_data["desc"],
                                "real_world_example": c_data["example"],
                                "difficulty": c_data["diff"],
                                "estimated_time": c_data["time"],
                                "is_active": True
                            }
                        )

                        # Lesson
                        Lesson.objects.get_or_create(
                            concept=conc_obj,
                            order=1,
                            defaults={
                                "title": f"Introduction to {conc_obj.name}",
                                "content_markdown": c_data["lesson"]
                            }
                        )

                        # Quiz
                        q_info = c_data.get("quiz")
                        if q_info:
                            quiz_obj, _ = Quiz.objects.get_or_create(
                                concept=conc_obj,
                                title=q_info["title"],
                                defaults={
                                    "description": f"Standard test for {conc_obj.name}",
                                    "difficulty": c_data["diff"],
                                    "time_limit": 10,
                                    "passing_percentage": 60,
                                    "xp_reward": 25,
                                    "is_active": True
                                }
                            )

                            for q_idx, q_item in enumerate(q_info["questions"], 1):
                                qq_obj, _ = QuizQuestion.objects.get_or_create(
                                    quiz=quiz_obj,
                                    display_order=q_idx,
                                    defaults={
                                        "question_text": q_item["text"],
                                        "marks": q_item["marks"],
                                        "explanation": "Review the core lesson to understand the underlying reasoning."
                                    }
                                )

                                for opt_idx, (opt_text, is_corr) in enumerate(q_item["options"], 1):
                                    QuizOption.objects.get_or_create(
                                        question=qq_obj,
                                        order=opt_idx,
                                        defaults={
                                            "option_text": opt_text,
                                            "is_correct": is_corr
                                        }
                                    )

                        # Game
                        game_title = c_data.get("game", f"{conc_obj.name} Game")
                        game_obj, _ = Game.objects.get_or_create(
                            concept=conc_obj,
                            title=game_title,
                            defaults={
                                "template": mcq_template,
                                "config": {"time_limit": 60}
                            }
                        )
                        GameLevel.objects.get_or_create(game=game_obj, difficulty="easy", defaults={"xp_reward": 10, "coin_reward": 5})
                        GameLevel.objects.get_or_create(game=game_obj, difficulty="medium", defaults={"xp_reward": 15, "coin_reward": 7})
                        GameLevel.objects.get_or_create(game=game_obj, difficulty="hard", defaults={"xp_reward": 20, "coin_reward": 10})

        self.stdout.write(self.style.SUCCESS("All curriculum, chapters, concepts, lessons, quizzes, and games seeded successfully!"))
