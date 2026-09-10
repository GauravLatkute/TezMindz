from django.core.management.base import BaseCommand
from django.utils.text import slugify

from academics.models import (
    Class, Subject, ClassSubject, Chapter, Concept,
    Quiz, QuizQuestion, QuizOption
)
from learning.models import Lesson
from games.models import GameTemplate, Game, GameLevel, Question, QuestionOption, Hint


class Command(BaseCommand):
    help = "Idempotently seeds Chapter 1: 'We the Travellers – I' for Class 5 Mathematics with 10 topics."

    def handle(self, *args, **options):
        self.stdout.write("Starting Chapter 1 seeding for Class 5 Mathematics...")

        # ── 1. Get or Create Class 5 ──────────────────────────────────────────
        cls5, created = Class.objects.get_or_create(
            grade_number=5,
            defaults={
                "name": "Grade 5",
                "class_label": "Class 5",
                "slug": "class-5",
                "stage": "Olympiad Challenger",
                "age_group": "Age 10 - 11",
                "category": "middle",
                "description": "Foundational and advanced Olympiad learning curriculum for Class 5.",
                "is_active": True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Class 5."))
        else:
            self.stdout.write("Reusing existing Class 5.")

        # ── 2. Get or Create Mathematics Subject ─────────────────────────────
        math_subj, created = Subject.objects.get_or_create(
            title="Mathematics",
            defaults={
                "subtitle": "Numbers • Logic • Geometry • Problem Solving",
                "olympiad_code": "IMO (International Math Olympiad)",
                "icon_type": "math",
                "color_theme": {
                    "bg": "bg-[#EFF6FF]",
                    "border": "border-blue-200",
                    "badgeBg": "bg-blue-500",
                    "accentText": "text-blue-700",
                    "buttonBg": "bg-blue-100"
                },
                "is_active": True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Mathematics Subject."))
        else:
            self.stdout.write("Reusing existing Mathematics Subject.")

        # ── 3. Connect Class 5 & Mathematics (ClassSubject) ───────────────────
        class_subject, created = ClassSubject.objects.get_or_create(
            student_class=cls5,
            subject=math_subj,
            defaults={"total_modules": 40}
        )

        # ── 4. Create or Update Chapter 1: "We the Travellers – I" ─────────────
        chapter1, created = Chapter.objects.get_or_create(
            class_subject=class_subject,
            order=1,
            defaults={
                "name": "We the Travellers – I",
                "slug": slugify("We the Travellers – I"),
                "description": "Embark on an exciting journey across India exploring large numbers, place values, number names, and practical math challenges.",
                "is_active": True
            }
        )
        if not created and chapter1.name != "We the Travellers – I":
            chapter1.name = "We the Travellers – I"
            chapter1.slug = slugify("We the Travellers – I")
            chapter1.description = "Embark on an exciting journey across India exploring large numbers, place values, number names, and practical math challenges."
            chapter1.save()
            self.stdout.write(self.style.SUCCESS("Updated Chapter 1 name to 'We the Travellers – I'."))
        else:
            self.stdout.write(f"Chapter 1: '{chapter1.name}' verified.")

        # ── 5. Define 10 Topics for Chapter 1 ────────────────────────────────
        topics_data = [
            {
                "order": 1,
                "name": "Reading and Writing Large Numbers",
                "desc": "Understand periods, commas in the Indian Numbering System, and how to read & write 5-digit and 6-digit numbers with ease.",
                "example": "Distance between Delhi and Kanyakumari is 2,750 km; a city stadium holds 1,25,000 spectators.",
                "diff": "easy",
                "time": 15,
                "lesson_title": "Journey into Large Numbers 🚂",
                "lesson_markdown": """# 🚂 Welcome, Young Traveller!

When we travel across our vast country, we encounter very large numbers — train ticket numbers, distances between cities, population of towns, and mountain heights!

---

### 🌟 1. The Indian Numbering System
In India, we organize large numbers into **Periods** separated by commas (`,`). This makes reading and writing them simple and quick!

| Period | Place Values | Example: 4,75,230 |
| :--- | :--- | :--- |
| **Lakhs Period** | Ten Lakhs, Lakhs | **4** Lakhs |
| **Thousands Period** | Ten Thousands, Thousands | **75** Thousands |
| **Ones Period** | Hundreds, Tens, Ones | **230** |

---

### 📍 2. Placing Commas Correctly:
1. The **first comma** comes after **3 digits** from the right (Ones Period).
2. Every subsequent comma comes after every **2 digits** (Thousands, Lakhs, Crores).

**Example:**
- `45230` $\\rightarrow$ **45,230** *(Forty-five thousand two hundred thirty)*
- `375420` $\\rightarrow$ **3,75,420** *(Three lakh seventy-five thousand four hundred twenty)*

---

### 💡 Pro Traveller Tip:
Always read from left to right saying the number followed by its period name! *(e.g., 5,20,000 is 5 Lakh 20 Thousand)*.
"""
            },
            {
                "order": 2,
                "name": "Place Value",
                "desc": "Determine the face value and place value of each digit based on its position in a large number.",
                "example": "In 3,45,670, the place value of 4 is 40,000 (Ten Thousands place).",
                "diff": "easy",
                "time": 15,
                "lesson_title": "Mastering Place Values",
                "lesson_markdown": "Every digit in a number has a Place Value depending on where it sits. Face value is the digit itself, while place value is digit multiplied by its position value."
            },
            {
                "order": 3,
                "name": "Expanded Form and Standard Form",
                "desc": "Break down large numbers into the sum of their place values and rebuild standard numbers from expanded forms.",
                "example": "3,45,200 = 3,00,000 + 40,000 + 5,000 + 200.",
                "diff": "medium",
                "time": 15,
                "lesson_title": "Expanding and Rebuilding Numbers",
                "lesson_markdown": "Expanded form shows the value of each digit added together."
            },
            {
                "order": 4,
                "name": "Number Names",
                "desc": "Convert large numeric figures into words and word descriptions into numeric digits using proper spelling and periods.",
                "example": "'Two Lakh Fifty Thousand Four Hundred' = 2,50,400.",
                "diff": "easy",
                "time": 15,
                "lesson_title": "Writing Words to Numbers",
                "lesson_markdown": "Writing number names using Indian Place Value rules."
            },
            {
                "order": 5,
                "name": "Comparing Large Numbers",
                "desc": "Use greater than (>), less than (<), and equal to (=) signs to compare multi-digit travel distances and values.",
                "example": "Comparing 3,45,200 km and 3,54,200 km by inspecting leftmost digits.",
                "diff": "medium",
                "time": 20,
                "lesson_title": "Comparing Numbers Step by Step",
                "lesson_markdown": "First compare digit count, then compare leftmost digits one by one."
            },
            {
                "order": 6,
                "name": "Ordering Numbers",
                "desc": "Arrange sets of large numbers in Ascending (smallest to largest) and Descending (largest to smallest) order.",
                "example": "Sorting station altitudes from sea level: 1,200m, 2,450m, 3,100m.",
                "diff": "medium",
                "time": 20,
                "lesson_title": "Ascending & Descending Sequences",
                "lesson_markdown": "How to sort travel stats and data points in sequence."
            },
            {
                "order": 7,
                "name": "Making Numbers Using Digits",
                "desc": "Form the greatest and smallest possible numbers using a given set of digits without repetition.",
                "example": "Using digits 4, 0, 7, 2, 9 to form greatest (97,420) and smallest (20,479) 5-digit numbers.",
                "diff": "medium",
                "time": 20,
                "lesson_title": "Crafting the Greatest & Smallest Numbers",
                "lesson_markdown": "Sort digits descending for greatest; ascending for smallest (never start with zero!)."
            },
            {
                "order": 8,
                "name": "Large Numbers in Real Life",
                "desc": "Practical word problems involving fuel consumption, railway passenger counts, and travel expenses.",
                "example": "Calculating total passenger traffic across 3 railway divisions.",
                "diff": "hard",
                "time": 25,
                "lesson_title": "Real-World Travel Math",
                "lesson_markdown": "Solving real life word problems with large numbers."
            },
            {
                "order": 9,
                "name": "Number Patterns and Puzzles",
                "desc": "Discover skip counting rules, number grids, and missing travel sequence codes.",
                "example": "Sequence: 25,000, 50,000, 75,000, [1,00,000].",
                "diff": "hard",
                "time": 20,
                "lesson_title": "Decoding Number Patterns",
                "lesson_markdown": "Finding the step jump difference between consecutive terms."
            },
            {
                "order": 10,
                "name": "Logical Number Challenges",
                "desc": "Olympiad-level critical thinking riddles, mystery numbers, and multi-step deduction puzzles.",
                "example": "'I am a 5-digit number with 7 in Thousands place and 0 in Tens place...'",
                "diff": "hard",
                "time": 25,
                "lesson_title": "Grand Olympiad Finale Challenge",
                "lesson_markdown": "Put all your large number skills to the ultimate test!"
            }
        ]

        # ── 6. Create or Update the 10 Topic Records ─────────────────────────
        topic_objects = {}
        for t_data in topics_data:
            conc, _ = Concept.objects.get_or_create(
                chapter=chapter1,
                order=t_data["order"],
                defaults={
                    "name": t_data["name"],
                    "slug": slugify(t_data["name"]),
                    "description": t_data["desc"],
                    "real_world_example": t_data["example"],
                    "difficulty": t_data["diff"],
                    "estimated_time": t_data["time"],
                    "is_active": True
                }
            )
            # Update name/desc if changed
            if conc.name != t_data["name"] or conc.description != t_data["desc"]:
                conc.name = t_data["name"]
                conc.description = t_data["desc"]
                conc.real_world_example = t_data["example"]
                conc.difficulty = t_data["diff"]
                conc.estimated_time = t_data["time"]
                conc.save()

            topic_objects[t_data["order"]] = conc

            # Create or update Lesson
            lesson, created_l = Lesson.objects.get_or_create(
                concept=conc,
                order=1,
                defaults={
                    "title": t_data["lesson_title"],
                    "content_markdown": t_data["lesson_markdown"]
                }
            )
            if not created_l:
                lesson.title = t_data["lesson_title"]
                lesson.content_markdown = t_data["lesson_markdown"]
                lesson.save()

        self.stdout.write(self.style.SUCCESS(f"All 10 Topics created for Chapter 1: '{chapter1.name}'."))

        # ── 7. Setup Topic 1: Easy Game ("Number Builder") ────────────────────
        topic1 = topic_objects[1]
        
        game_tmpl, _ = GameTemplate.objects.get_or_create(
            slug="number_builder",
            defaults={
                "name": "Number Builder Game",
                "description": "Place digits into correct place value slots (Lakhs, Thousands, Ones) to build the target large number."
            }
        )

        game1, _ = Game.objects.get_or_create(
            concept=topic1,
            title="Number Builder",
            defaults={
                "template": game_tmpl,
                "slug": "number-builder",
                "game_path": "class_5/mathematics/chapter_01_large_numbers/topic_01_reading_writing_numbers/number_builder",
                "game_type": "number_builder",
                "config": {
                    "game_type": "NUMBER_BUILDER",
                    "time_limit": 60,
                    "target_number": 375420,
                    "target_word": "Three Lakh Seventy-Five Thousand Four Hundred Twenty"
                }
            }
        )
        game1.slug = "number-builder"
        game1.game_path = "class_5/mathematics/chapter_01_large_numbers/topic_01_reading_writing_numbers/number_builder"
        game1.game_type = "number_builder"
        game1.save()
        game_level1, _ = GameLevel.objects.get_or_create(
            game=game1,
            difficulty="easy",
            defaults={"xp_reward": 20, "coin_reward": 10}
        )

        # Game Question & Options for Number Builder
        g_q1, _ = Question.objects.get_or_create(
            game_level=game_level1,
            text="Build the number: Three Lakh Seventy-Five Thousand Four Hundred Twenty",
            defaults={"explanation": "In Indian system: 3 in Lakhs, 7 in Ten Thousands, 5 in Thousands, 4 in Hundreds, 2 in Tens, 0 in Ones = 3,75,420."}
        )
        QuestionOption.objects.get_or_create(question=g_q1, order=1, defaults={"text": "3,75,420", "is_correct": True})
        QuestionOption.objects.get_or_create(question=g_q1, order=2, defaults={"text": "37,542", "is_correct": False})
        QuestionOption.objects.get_or_create(question=g_q1, order=3, defaults={"text": "3,07,542", "is_correct": False})
        QuestionOption.objects.get_or_create(question=g_q1, order=4, defaults={"text": "37,50,420", "is_correct": False})

        Hint.objects.get_or_create(question=g_q1, order=1, defaults={"text": "Look at the highest period: Three Lakh means 3 comes before the first comma."})
        Hint.objects.get_or_create(question=g_q1, order=2, defaults={"text": "Next is Seventy-Five Thousand, which is written as 75."})
        Hint.objects.get_or_create(question=g_q1, order=3, defaults={"text": "Combine 3 + 75 + 420 = 3,75,420."})

        self.stdout.write(self.style.SUCCESS("Topic 1 'Number Builder' game created."))

        # ── 8. Setup Topic 1: Quiz ───────────────────────────────────────────
        quiz1, _ = Quiz.objects.get_or_create(
            concept=topic1,
            title="Reading & Writing Large Numbers Quiz",
            defaults={
                "description": "Test your mastery of periods, commas, and large number reading in real-life travel situations.",
                "difficulty": "easy",
                "time_limit": 10,
                "passing_percentage": 60,
                "xp_reward": 30,
                "is_active": True
            }
        )

        quiz_questions_data = [
            {
                "order": 1,
                "text": "In the Indian Numbering System, where does the FIRST comma from the right go?",
                "marks": 1,
                "explanation": "The first comma is placed after 3 digits from the right to mark the Ones period (Hundreds, Tens, Ones).",
                "options": [
                    ("After 2 digits", False),
                    ("After 3 digits", True),
                    ("After 4 digits", False),
                    ("After 5 digits", False),
                ]
            },
            {
                "order": 2,
                "text": "True or False: The number 4,50,230 is read as 'Four Lakh Fifty Thousand Two Hundred Thirty'.",
                "marks": 1,
                "explanation": "True! 4 is in the Lakhs place, 50 in the Thousands place, and 230 in the Ones place.",
                "options": [
                    ("True", True),
                    ("False", False),
                ]
            },
            {
                "order": 3,
                "text": "A train travels a total distance of 25700 km in one month. How should this number be written with proper commas?",
                "marks": 1,
                "explanation": "Starting from the right, count 3 digits (700) and place a comma: 25,700.",
                "options": [
                    ("2,5700", False),
                    ("25,700", True),
                    ("257,00", False),
                    ("25,70,0", False),
                ]
            },
            {
                "order": 4,
                "text": "Which of the following numbers correctly represents 'Six Lakh Five Thousand Four Hundred Twenty'?",
                "marks": 1,
                "explanation": "6 Lakhs = 6, 05 Thousands = 05, 420 Ones = 6,05,420.",
                "options": [
                    ("6,50,420", False),
                    ("6,05,420", True),
                    ("65,042", False),
                    ("6,00,542", False),
                ]
            }
        ]

        for q_data in quiz_questions_data:
            qq, _ = QuizQuestion.objects.get_or_create(
                quiz=quiz1,
                display_order=q_data["order"],
                defaults={
                    "question_text": q_data["text"],
                    "marks": q_data["marks"],
                    "explanation": q_data["explanation"]
                }
            )
            for opt_idx, (opt_text, is_corr) in enumerate(q_data["options"], 1):
                QuizOption.objects.get_or_create(
                    question=qq,
                    order=opt_idx,
                    defaults={
                        "option_text": opt_text,
                        "is_correct": is_corr
                    }
                )

        self.stdout.write(self.style.SUCCESS("Topic 1 Quiz with 4 questions created."))

        # ── 9. Setup Quizzes for Topics 2 to 10 ──────────────────────────────
        all_topics_quizzes = [
            (2, "Place Value Mastery Quiz", [
                ("In the number 4,75,230, what is the PLACE VALUE of the digit 7?", [("70,000 (Ten-Thousands)", True), ("7,000 (Thousands)", False), ("700 (Hundreds)", False), ("7 Lakhs", False)]),
                ("What is the FACE VALUE of the digit 5 in 3,52,100?", [("5", True), ("50,000", False), ("5,000", False), ("500", False)]),
            ]),
            (3, "Expanded Form and Standard Form Quiz", [
                ("What is the standard form of 3,00,000 + 40,000 + 5,000 + 200 + 10?", [("3,45,210", True), ("34,521", False), ("3,04,521", False), ("3,45,021", False)]),
                ("What is the expanded form of 52,040?", [("50,000 + 2,000 + 40", True), ("50,000 + 200 + 40", False), ("5,000 + 200 + 40", False), ("50,000 + 20 + 4", False)]),
            ]),
            (4, "Number Names Quiz", [
                ("How do you write 2,50,400 in words?", [("Two Lakh Fifty Thousand Four Hundred", True), ("Twenty-Five Thousand Four Hundred", False), ("Two Lakh Five Thousand Four Hundred", False), ("Two Million Fifty Thousand", False)]),
                ("Which digits represent 'Eight Lakh Four Thousand Two Hundred'?", [("8,04,200", True), ("8,40,200", False), ("84,200", False), ("8,00,420", False)]),
            ]),
            (5, "Comparing Large Numbers Quiz", [
                ("Which symbol correctly compares: 3,45,200 ___ 3,54,200?", [("< (Less than)", True), ("> (Greater than)", False), ("= (Equal to)", False), ("None", False)]),
                ("Which number is the largest?", [("6,52,100", True), ("6,25,100", False), ("5,62,100", False), ("6,51,999", False)]),
            ]),
            (6, "Ordering Numbers Quiz", [
                ("Arrange in Ascending order: 45,000, 23,000, 67,000", [("23,000, 45,000, 67,000", True), ("67,000, 45,000, 23,000", False), ("45,000, 23,000, 67,000", False), ("23,000, 67,000, 45,000", False)]),
            ]),
            (7, "Making Numbers Using Digits Quiz", [
                ("Using digits 7, 5, 2, 0, 9 once each, what is the GREATEST 5-digit number?", [("97,520", True), ("97,502", False), ("95,720", False), ("79,520", False)]),
                ("Using digits 4, 1, 8, 3 once each, what is the SMALLEST 4-digit number?", [("1,348", True), ("1,438", False), ("1,843", False), ("3,148", False)]),
            ]),
            (8, "Large Numbers in Real Life Quiz", [
                ("A train ticket costs ₹ 450. How much do 100 tickets cost?", [("₹ 45,000", True), ("₹ 4,500", False), ("₹ 4,50,000", False), ("₹ 450", False)]),
            ]),
            (9, "Number Patterns and Puzzles Quiz", [
                ("What comes next: 10,000, 25,000, 40,000, ___?", [("55,000 (+15,000 each step)", True), ("50,000", False), ("60,000", False), ("45,000", False)]),
            ]),
            (10, "Logical Number Challenges Quiz", [
                ("I am a 5-digit number with 7 in Thousands place and 0 in Tens place. Which number could I be?", [("47,205", True), ("74,205", False), ("42,705", False), ("47,025", False)]),
            ]),
        ]

        for t_order, q_title, q_list in all_topics_quizzes:
            if t_order in topic_objects:
                t_conc = topic_objects[t_order]
                t_quiz, _ = Quiz.objects.get_or_create(
                    concept=t_conc,
                    title=q_title,
                    defaults={
                        "description": f"Test your mastery of {t_conc.name}.",
                        "difficulty": "medium",
                        "time_limit": 10,
                        "passing_percentage": 60,
                        "xp_reward": 30,
                        "is_active": True
                    }
                )
                for q_idx, (q_txt, opts) in enumerate(q_list, 1):
                    t_qq, _ = QuizQuestion.objects.get_or_create(
                        quiz=t_quiz,
                        display_order=q_idx,
                        defaults={"question_text": q_txt, "marks": 1, "explanation": "Apply the Indian place value rules."}
                    )
                    for o_idx, (o_txt, o_corr) in enumerate(opts, 1):
                        QuizOption.objects.get_or_create(
                            question=t_qq,
                            order=o_idx,
                            defaults={"option_text": o_txt, "is_correct": o_corr}
                        )

        self.stdout.write(self.style.SUCCESS("All Chapter 1 Topic Quizzes & Questions created!"))
        self.stdout.write(self.style.SUCCESS("Chapter 1: 'We the Travellers – I' is completely seeded and ready!"))
