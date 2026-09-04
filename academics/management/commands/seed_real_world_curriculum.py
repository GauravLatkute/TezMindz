from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from academics.models import (
    Class, Subject, ClassSubject, Chapter, Concept,
    Quiz, QuizQuestion, QuizOption, DailyChallenge
)
from learning.models import Lesson
from games.models import GameTemplate, Game, GameLevel, Question, QuestionOption, Hint
from rewards.models import Badge, Achievement


class Command(BaseCommand):
    help = "Seeds authentic, high-quality NCERT & Olympiad curriculum for Class 5 across Mathematics, Science, and English."

    def handle(self, *args, **options):
        self.stdout.write("Starting authentic real-world curriculum database seed...")

        # ── 1. Game Template ─────────────────────────────────────────────────
        house_template, _ = GameTemplate.objects.get_or_create(
            slug="house_builder",
            defaults={
                "name": "Dream House Builder",
                "description": "3D Interactive construction RPG teaching mathematics and number sense."
            }
        )
        mcq_template, _ = GameTemplate.objects.get_or_create(
            slug="mcq",
            defaults={
                "name": "Multiple Choice Quest",
                "description": "Interactive topic challenge game."
            }
        )

        # ── 2. Platform Badges & Achievements ────────────────────────────────
        badges_data = [
            ("Math Explorer", "Mastered 5 Mathematics topics", "🔢"),
            ("Science Explorer", "Completed 5 Science experiments", "🧪"),
            ("Word Wizard", "Mastered 5 English grammar missions", "📖"),
            ("Number Champion", "Completed Dream House Builder 3D", "🏛️"),
            ("Streak Master", "Maintained a 7-day learning streak", "🔥"),
        ]
        for name, desc, icon in badges_data:
            Badge.objects.get_or_create(
                name=name,
                defaults={"description": desc, "icon": icon, "criteria": {"points": 100}}
            )

        achievements_data = [
            {"name": "First Step", "desc": "Complete your first lesson", "icon": "🌱", "type": "first_lesson", "val": 1, "xp": 25, "coins": 10},
            {"name": "Quiz Master", "desc": "Pass your first quiz with flying colors", "icon": "🎓", "type": "first_quiz", "val": 1, "xp": 35, "coins": 15},
            {"name": "Game On", "desc": "Play and complete your first educational game", "icon": "🎮", "type": "first_game", "val": 1, "xp": 30, "coins": 15},
            {"name": "Architect of Mind", "desc": "Complete Dream House Builder 3D Game", "icon": "🏰", "type": "game_complete", "val": 1, "xp": 100, "coins": 50},
            {"name": "Consistent Scholar", "desc": "Maintain a 3-day learning streak", "icon": "🔥", "type": "streak_days", "val": 3, "xp": 50, "coins": 25},
            {"name": "Week Warrior", "desc": "Keep a 7-day continuous streak", "icon": "⚡", "type": "streak_days", "val": 7, "xp": 100, "coins": 50},
            {"name": "Knowledge Collector", "desc": "Complete 5 distinct lessons", "icon": "📚", "type": "lessons_completed", "val": 5, "xp": 75, "coins": 30},
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

        # ── 3. Class 5 Setup ─────────────────────────────────────────────────
        cls5, _ = Class.objects.get_or_create(
            grade_number=5,
            defaults={
                "name": "Grade 5",
                "class_label": "Class 5",
                "slug": "class-5",
                "stage": "Olympiad Challenger",
                "age_group": "Age 10 - 11",
                "category": "middle",
                "description": "NCERT & Olympiad curriculum for Class 5.",
                "is_active": True
            }
        )

        # ── 4. Subjects Definition ───────────────────────────────────────────
        subjects_config = [
            {
                "title": "Mathematics",
                "subtitle": "Numbers • Logic • Geometry • Problem Solving",
                "olympiad": "IMO (Maths Olympiad)",
                "icon": "math",
                "color": {"bg": "bg-[#EFF6FF]", "border": "border-blue-200", "badgeBg": "bg-blue-500", "accentText": "text-blue-700", "buttonBg": "bg-blue-100"},
                "chapters": [
                    {
                        "order": 1,
                        "name": "We the Travellers – I",
                        "desc": "Journey across India exploring 5-digit, 6-digit & 7-digit numbers, Indian place values, expanded form, comparing distances, and budget math.",
                        "concepts": [
                            {
                                "order": 1, "name": "Reading and Writing Large Numbers", "diff": "easy", "time": 15,
                                "desc": "Understand periods and commas in the Indian Numbering System to read and write up to 7-digit numbers.",
                                "example": "A train ticket cost is ₹2,50,000 for a luxury school excursion; the distance between Delhi and Kanyakumari is 2,750 km.",
                                "lesson_title": "Journey into Large Numbers 🚂",
                                "lesson_md": "# 🚂 Welcome, Young Traveller!\n\nIn India, we read large numbers using **Periods** separated by commas:\n- **Ones Period**: 3 digits (Hundreds, Tens, Ones)\n- **Thousands Period**: 2 digits (Ten-Thousands, Thousands)\n- **Lakhs Period**: 2 digits (Ten-Lakhs, Lakhs)\n\n### Example:\n`2,50,000` is read as **Two Lakh Fifty Thousand**.",
                                "quiz": {
                                    "title": "Large Numbers Reading Quiz",
                                    "questions": [
                                        ("How is 2,50,000 written in words in the Indian Number System?", "Two Lakh Fifty Thousand", ["Twenty-Five Thousand", "Two Thousand Five Hundred", "Twenty-Five Lakh"]),
                                        ("Where does the first comma from right go in the Indian System?", "After 3 digits (Hundreds)", ["After 2 digits", "After 4 digits", "After 1 digit"]),
                                        ("How many thousands make 1 Lakh?", "100 Thousands", ["10 Thousands", "1,000 Thousands", "50 Thousands"]),
                                        ("Read 3,75,420: How many lakhs are there?", "3 Lakhs", ["37 Lakhs", "75 Lakhs", "30 Lakhs"])
                                    ]
                                }
                            },
                            {
                                "order": 2, "name": "Place Value & Face Value", "diff": "medium", "time": 15,
                                "desc": "Determine the place value (position-based) and face value (actual digit value) of digits in large numbers.",
                                "example": "In 3,75,420, the face value of 7 is 7, but its place value is 7 × 10,000 = 70,000.",
                                "lesson_title": "Place Value Power 🔍",
                                "lesson_md": "# 🔍 Place Value vs Face Value\n\n- **Face Value**: The value of the digit itself (always stays the same).\n- **Place Value**: `Digit × Value of its place`.\n\nIn `4,52,380`:\n- Place value of `5` = `5 × 10,000 = 50,000` (Ten-Thousands place).\n- Face value of `5` = `5`.",
                                "quiz": {
                                    "title": "Place Value Master Quiz",
                                    "questions": [
                                        ("What is the place value of 5 in 2,50,000?", "50,000 (Ten-Thousands)", ["5,000 (Thousands)", "500 (Hundreds)", "5 Lakhs"]),
                                        ("What is the face value of 8 in 3,85,120?", "8", ["80,000", "8,000", "800"]),
                                        ("In 9,08,105, which place has the digit 0?", "Ten-Thousands", ["Thousands", "Hundreds", "Lakhs"]),
                                        ("What is the value of 3 in the Lakhs place?", "3,00,000", ["30,000", "3,000", "300"])
                                    ]
                                }
                            },
                            {
                                "order": 3, "name": "Expanded Form and Standard Form", "diff": "medium", "time": 15,
                                "desc": "Break numbers into sums of their place values and assemble expanded numbers into standard numerals.",
                                "example": "3,45,670 = 3,00,000 + 40,000 + 5,000 + 600 + 70 + 0.",
                                "lesson_title": "Expanding Numbers 📦",
                                "lesson_md": "# 📦 Expanding Numbers\n\nWriting a number as the sum of the place values of all its digits is called its **Expanded Form**.\n\n`4,25,300` = `4,00,000 + 20,000 + 5,000 + 300 + 0 + 0`.",
                                "quiz": {
                                    "title": "Expanded Form Quiz",
                                    "questions": [
                                        ("What is the standard numeral for 5,00,000 + 20,000 + 3,000 + 400 + 50 + 6?", "5,23,456", ["5,20,345", "52,345", "5,23,056"]),
                                        ("What is the expanded form of 3,25,000?", "3,00,000 + 20,000 + 5,000", ["30,000 + 2,000 + 500", "3,00,000 + 2,000 + 500", "3,00,000 + 25,000"]),
                                        ("In standard form, what is 8 Lakhs + 4 Thousands + 2 Ones?", "8,04,002", ["8,40,002", "8,04,200", "84,002"])
                                    ]
                                }
                            },
                            {
                                "order": 4, "name": "Comparing and Ordering Large Numbers", "diff": "medium", "time": 15,
                                "desc": "Compare distances, city populations, and project budgets using <, >, and = operators, and arrange numbers in ascending/descending order.",
                                "example": "Supplier A quotes ₹3,12,000 and Supplier B quotes ₹2,45,000. Since 3 Lakhs > 2 Lakhs, Supplier A is more expensive.",
                                "lesson_title": "Comparing Magnitudes ⚖️",
                                "lesson_md": "# ⚖️ Comparing Large Numbers\n\n1. Count digits: The number with more digits is greater.\n2. If digit count is equal: Compare digits from left to right (highest place value first).",
                                "quiz": {
                                    "title": "Comparing Numbers Quiz",
                                    "questions": [
                                        ("Which comparison statement is correct?", "3,12,000 > 2,45,000", ["3,12,000 < 2,45,000", "3,12,000 = 2,45,000", "2,45,000 > 3,12,000"]),
                                        ("Which number is the largest?", "5,72,000", ["5,27,000", "5,07,200", "5,70,200"]),
                                        ("Arrange ascending (smallest to largest): 4,10,000; 2,80,000; 5,00,000", "2,80,000 < 4,10,000 < 5,00,000", ["5,00,000 < 4,10,000 < 2,80,000", "4,10,000 < 2,80,000 < 5,00,000"])
                                    ]
                                }
                            },
                            {
                                "order": 5, "name": "Real-World Budgeting & Estimation", "diff": "hard", "time": 20,
                                "desc": "Calculate totals, verify expenses, and manage budgets in realistic multi-step construction and travel projects.",
                                "example": "Building expenses: Land ₹2,50,000 + Foundation ₹1,25,000 + Walls ₹3,10,000 + Roof ₹1,50,000 = Total ₹8,35,000.",
                                "lesson_title": "Architect Budget Master 🏗️",
                                "lesson_md": "# 🏗️ Real-World Budget Estimation\n\nWhen planning big projects like building a dream house or planning train travel across India, we sum all category expenses to find the master budget.",
                                "quiz": {
                                    "title": "Budget Calculation Quiz",
                                    "questions": [
                                        ("What is ₹2,50,000 + ₹1,25,000 + ₹3,10,000 + ₹1,50,000?", "₹8,35,000", ["₹7,35,000", "₹8,45,000", "₹9,35,000"]),
                                        ("If budget is ₹10,00,000 and you spend ₹6,50,000, how much remains?", "₹3,50,000", ["₹4,50,000", "₹3,00,000", "₹2,50,000"]),
                                        ("Round 4,78,920 to the nearest Lakh:", "5,00,000", ["4,00,000", "4,80,000", "4,70,000"])
                                    ]
                                }
                            }
                        ]
                    },
                    {
                        "order": 2,
                        "name": "Shapes & Angles",
                        "desc": "Explore geometry, right angles (90°), acute & obtuse angles, clock hand angles, protractors, and symmetric patterns.",
                        "concepts": [
                            {
                                "order": 1, "name": "Right, Acute and Obtuse Angles", "diff": "easy", "time": 15,
                                "desc": "Classify angles based on 90° (L-shape Right Angle), smaller than 90° (Acute), and greater than 90° (Obtuse).",
                                "example": "The corner of a book is a Right Angle (90°); open scissors make an Acute Angle; a reclining chair makes an Obtuse Angle.",
                                "lesson_title": "Discovering Angles 📐",
                                "lesson_md": "# 📐 Types of Angles\n\n- **Right Angle**: Exactly $90^\\circ$ (an 'L' shape).\n- **Acute Angle**: Less than $90^\\circ$ (sharp, pointy).\n- **Obtuse Angle**: Greater than $90^\\circ$ but less than $180^\\circ$ (wide open).\n- **Straight Angle**: Exactly $180^\\circ$ (a flat line).",
                                "quiz": {
                                    "title": "Angles Classification Quiz",
                                    "questions": [
                                        ("What type of angle measures exactly 90 degrees?", "Right Angle", ["Acute Angle", "Obtuse Angle", "Reflex Angle"]),
                                        ("An angle measuring 45 degrees is called:", "Acute Angle", ["Right Angle", "Obtuse Angle", "Straight Angle"]),
                                        ("What angle do clock hands make at 3:00 PM?", "Right Angle (90°)", ["Acute Angle", "Obtuse Angle", "Straight Angle"]),
                                        ("An angle of 135 degrees is classified as:", "Obtuse Angle", ["Acute Angle", "Right Angle", "Straight Angle"])
                                    ]
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Science",
                "subtitle": "Physics • Chemistry • Biology • Life Systems",
                "olympiad": "NSO (Science Olympiad)",
                "icon": "science",
                "color": {"bg": "bg-[#ECFDF5]", "border": "border-emerald-200", "badgeBg": "bg-emerald-500", "accentText": "text-emerald-700", "buttonBg": "bg-emerald-100"},
                "chapters": [
                    {
                        "order": 1,
                        "name": "Plants & Photosynthesis",
                        "desc": "Discover how green plants produce energy through chloroplasts, sunlight, carbon dioxide, and water transport.",
                        "concepts": [
                            {
                                "order": 1, "name": "The Photosynthesis Process", "diff": "easy", "time": 15,
                                "desc": "Learn how leaves act as food factories by converting Sunlight + Water + CO2 into Glucose and Oxygen.",
                                "example": "Green leaves absorb sunlight using chlorophyll and release fresh oxygen for all living beings to breathe.",
                                "lesson_title": "Leaf Food Factory 🍃",
                                "lesson_md": "# 🍃 The Photosynthesis Miracle\n\nGreen plants are autotrophs — they make their own food through **Photosynthesis**:\n\n$$\\text{Carbon Dioxide (CO}_2\\text{)} + \\text{Water (H}_2\\text{O)} + \\text{Sunlight} \\xrightarrow{\\text{Chlorophyll}} \\text{Glucose (Food)} + \\text{Oxygen (O}_2\\text{)}$$\n\n### Key Components:\n1. **Chlorophyll**: Green pigment in chloroplasts that captures light energy.\n2. **Stomata**: Tiny pores on the underside of leaves for gas exchange.\n3. **Xylem**: Tubes carrying water from roots to leaves.",
                                "quiz": {
                                    "title": "Photosynthesis Discovery Quiz",
                                    "questions": [
                                        ("Which gas is absorbed by green leaves during photosynthesis?", "Carbon Dioxide (CO2)", ["Oxygen", "Nitrogen", "Helium"]),
                                        ("What is the green pigment in plant leaves called?", "Chlorophyll", ["Carotene", "Hemoglobin", "Melanin"]),
                                        ("What are the microscopic pores on leaves called?", "Stomata", ["Xylem", "Phloem", "Chloroplast"]),
                                        ("Which gas is released into the atmosphere as a byproduct of photosynthesis?", "Oxygen (O2)", ["Carbon Dioxide", "Methane", "Hydrogen"])
                                    ]
                                }
                            },
                            {
                                "order": 2, "name": "Plant Transport: Xylem and Phloem", "diff": "medium", "time": 15,
                                "desc": "Understand how vascular tissues carry water upwards and distribute glucose food throughout the plant.",
                                "example": "Roots pull moisture and minerals from the soil and xylem vessels transport them up to the highest leaves of a tree.",
                                "lesson_title": "Vascular Highway of Plants 🌿",
                                "lesson_md": "# 🌿 Xylem vs Phloem\n\n- **Xylem**: Transports **water and dissolved minerals** from roots up to leaves (one-way upward flow).\n- **Phloem**: Transports **prepared glucose food** from leaves to all growing parts of the plant (two-way flow).",
                                "quiz": {
                                    "title": "Plant Vascular System Quiz",
                                    "questions": [
                                        ("Which plant tissue transports water from roots to leaves?", "Xylem", ["Phloem", "Stomata", "Chlorophyll"]),
                                        ("Which tissue carries glucose food produced in leaves to other plant parts?", "Phloem", ["Xylem", "Epidermis", "Root cap"]),
                                        ("Water absorption from soil happens mainly through:", "Root hairs", ["Leaf veins", "Bark", "Flower petals"])
                                    ]
                                }
                            }
                        ]
                    },
                    {
                        "order": 2,
                        "name": "Animal Habitats & Adaptations",
                        "desc": "Explore structural and behavioral adaptations of animals in desert, aquatic, polar, and rainforest ecosystems.",
                        "concepts": [
                            {
                                "order": 1, "name": "Desert and Polar Adaptations", "diff": "medium", "time": 15,
                                "desc": "Examine how camels survive in arid sands with humps and polar bears stay warm in arctic freezing temperatures.",
                                "example": "Camels have wide padded feet to walk on sand without sinking; polar bears have thick blubber fat for insulation.",
                                "lesson_title": "Survival in Extreme Biomes 🐪",
                                "lesson_md": "# 🐪 Animal Adaptations\n\nAdaptations are special features that help living organisms survive in their environments.\n\n### Desert (Camel):\n- Hump stores fat for energy.\n- Long eyelashes keep out blown sand.\n- Wide padded feet prevent sinking in sand.\n\n### Polar (Polar Bear):\n- Thick layer of fat (blubber) for warmth.\n- White fur for camouflage on snow.",
                                "quiz": {
                                    "title": "Habitats & Adaptations Quiz",
                                    "questions": [
                                        ("What helps camels walk easily on loose desert sand?", "Broad padded feet", ["Hooves", "Claws", "Flippers"]),
                                        ("The thick layer of insulating fat under polar bear skin is called:", "Blubber", ["Keratin", "Chitin", "Gills"]),
                                        ("Fish breathe underwater using specialized organs called:", "Gills", ["Lungs", "Trachea", "Spiracles"])
                                    ]
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "title": "English",
                "subtitle": "Grammar • Vocabulary • Reading • Writing",
                "olympiad": "IEO (English Olympiad)",
                "icon": "english",
                "color": {"bg": "bg-[#FDF2F8]", "border": "border-rose-200", "badgeBg": "bg-rose-500", "accentText": "text-rose-700", "buttonBg": "bg-rose-100"},
                "chapters": [
                    {
                        "order": 1,
                        "name": "Parts of Speech & Grammar Mastery",
                        "desc": "Master nouns (proper, common, collective, abstract), pronouns, action verbs, adjectives, and adverbs.",
                        "concepts": [
                            {
                                "order": 1, "name": "Nouns and Pronouns", "diff": "easy", "time": 15,
                                "desc": "Identify types of nouns and use pronouns to replace repetitive nouns in well-crafted sentences.",
                                "example": "Rohan lost his book. He searched everywhere until he found it in the library.",
                                "lesson_title": "Naming Words & Stand-ins 📚",
                                "lesson_md": "# 📚 Nouns and Pronouns\n\n- **Noun**: Names a person, place, animal, thing, or idea (e.g., *Aarav*, *Taj Mahal*, *happiness*, *flock*).\n- **Pronoun**: A word used in place of a noun (e.g., *he*, *she*, *it*, *they*, *we*).\n\n### Types of Nouns:\n1. **Proper Noun**: Specific name (*India*, *Mumbai*).\n2. **Common Noun**: General name (*city*, *country*).\n3. **Collective Noun**: Group name (*a pride of lions*, *a bouquet of flowers*).\n4. **Abstract Noun**: Feeling/Quality (*bravery*, *honesty*).",
                                "quiz": {
                                    "title": "Nouns & Pronouns Master Quiz",
                                    "questions": [
                                        ("Which word is an Abstract Noun?", "Courage", ["Elephant", "Delhi", "Table"]),
                                        ("Identify the Collective Noun: 'A flock of birds flew across the sky.'", "Flock", ["Birds", "Flew", "Sky"]),
                                        ("Choose the correct pronoun: 'Priya is studying because ____ has an exam tomorrow.'", "she", ["he", "it", "they"]),
                                        ("Which word is a Proper Noun?", "Himalayas", ["Mountain", "River", "Peak"])
                                    ]
                                }
                            },
                            {
                                "order": 2, "name": "Action Verbs and Tenses", "diff": "medium", "time": 15,
                                "desc": "Master present, past, and future action verbs and subject-verb agreement in dynamic sentences.",
                                "example": "The train arrives at 6 PM (Present); It arrived yesterday (Past); It will arrive tomorrow (Future).",
                                "lesson_title": "Verbs in Motion ⚡",
                                "lesson_md": "# ⚡ Action Verbs and Tenses\n\nVerbs express actions or states of being:\n- **Simple Present**: Habits and facts (*She reads daily*).\n- **Simple Past**: Completed actions (*She read yesterday*).\n- **Simple Future**: Future events (*She will read tomorrow*).",
                                "quiz": {
                                    "title": "Verbs & Tenses Quiz",
                                    "questions": [
                                        ("Choose the past tense of 'run':", "Ran", ["Running", "Runs", "Runned"]),
                                        ("Which sentence is in Simple Future Tense?", "We will visit the science museum tomorrow.", ["We visited the museum.", "We are visiting the museum.", "We visit the museum."]),
                                        ("Select the correct verb: 'The boys ____ playing football in the field.'", "are", ["is", "was", "has"])
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        ]

        # ── 5. Build Class 5 Curriculum Database Records ─────────────────────
        for s_cfg in subjects_config:
            subj_obj, _ = Subject.objects.get_or_create(
                title=s_cfg["title"],
                defaults={
                    "subtitle": s_cfg["subtitle"],
                    "olympiad_code": s_cfg["olympiad"],
                    "icon_type": s_cfg["icon"],
                    "color_theme": s_cfg["color"],
                    "is_active": True
                }
            )

            cs_obj, _ = ClassSubject.objects.get_or_create(
                student_class=cls5,
                subject=subj_obj,
                defaults={"total_modules": 40}
            )

            for ch_cfg in s_cfg["chapters"]:
                ch_obj, _ = Chapter.objects.get_or_create(
                    class_subject=cs_obj,
                    order=ch_cfg["order"],
                    defaults={
                        "name": ch_cfg["name"],
                        "slug": slugify(ch_cfg["name"]),
                        "description": ch_cfg["desc"],
                        "is_active": True
                    }
                )

                for c_cfg in ch_cfg["concepts"]:
                    c_obj, _ = Concept.objects.get_or_create(
                        chapter=ch_obj,
                        order=c_cfg["order"],
                        defaults={
                            "name": c_cfg["name"],
                            "slug": slugify(c_cfg["name"]),
                            "description": c_cfg["desc"],
                            "real_world_example": c_cfg["example"],
                            "difficulty": c_cfg["diff"],
                            "estimated_time": c_cfg["time"],
                            "is_active": True
                        }
                    )

                    # Create Lesson
                    Lesson.objects.get_or_create(
                        concept=c_obj,
                        order=1,
                        defaults={
                            "title": c_cfg["lesson_title"],
                            "content_markdown": c_cfg["lesson_md"]
                        }
                    )

                    # Create Quiz & Questions
                    q_data = c_cfg.get("quiz")
                    if q_data:
                        quiz_obj, _ = Quiz.objects.get_or_create(
                            concept=c_obj,
                            title=q_data["title"],
                            defaults={
                                "description": f"Mastery quiz for {c_obj.name}",
                                "difficulty": c_obj.difficulty,
                                "time_limit": 10,
                                "passing_percentage": 60,
                                "xp_reward": 30,
                                "is_active": True
                            }
                        )

                        for q_idx, q_tuple in enumerate(q_data["questions"], 1):
                            q_text, correct_opt, wrongs = q_tuple
                            qq_obj, _ = QuizQuestion.objects.get_or_create(
                                quiz=quiz_obj,
                                display_order=q_idx,
                                defaults={
                                    "question_text": q_text,
                                    "marks": 1,
                                    "explanation": f"The correct answer is: {correct_opt}"
                                }
                            )

                            # Correct Option
                            QuizOption.objects.get_or_create(
                                question=qq_obj,
                                option_text=correct_opt,
                                defaults={"is_correct": True, "order": 1}
                            )

                            # Wrong Options
                            for w_idx, w_text in enumerate(wrongs, 2):
                                QuizOption.objects.get_or_create(
                                    question=qq_obj,
                                    option_text=w_text,
                                    defaults={"is_correct": False, "order": w_idx}
                                )

                    # Attach Dream House Builder to Class 5 Math Ch 1 Concept 1
                    if s_cfg["title"] == "Mathematics" and ch_cfg["order"] == 1 and c_cfg["order"] == 1:
                        Game.objects.get_or_create(
                            slug="dream-house-builder",
                            defaults={
                                "concept": c_obj,
                                "template": house_template,
                                "title": "Dream House Builder",
                                "game_type": "house_builder",
                                "description": "3D Interactive construction game teaching Indian Number System reading, writing, and place value.",
                                "difficulty": "medium",
                                "estimated_time": 15,
                                "xp_reward": 50,
                                "coin_reward": 15,
                                "is_active": True
                            }
                        )

        # ── 6. Seed Daily Challenges for Active Dates ────────────────────────
        today = date.today()
        daily_challenges_data = [
            ("Class 5 Daily Mind Challenge", "Solve 5 quick questions on Class 5 topics to earn double XP and keep your streak burning!", "medium", 50, 25),
            ("Speed Calculation Blitz", "Test your mental math skills with 5 fast-paced arithmetic challenges!", "easy", 40, 20),
            ("Science Wonder Challenge", "Answer 5 intriguing daily questions on biology, physics, and ecosystems!", "medium", 50, 25),
            ("Grammar Guru Daily", "Sharpen your sentence mastery with 5 parts-of-speech puzzles!", "easy", 40, 20),
        ]

        for offset in range(-2, 6):
            target_date = today + timedelta(days=offset)
            title, desc, diff, xp, coins = daily_challenges_data[offset % len(daily_challenges_data)]
            DailyChallenge.objects.get_or_create(
                student_class=cls5,
                date=target_date,
                defaults={
                    "title": title,
                    "description": desc,
                    "difficulty": diff,
                    "xp_reward": xp,
                    "coin_reward": coins,
                    "is_active": True
                }
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded real-world NCERT & Olympiad curriculum database!"))
