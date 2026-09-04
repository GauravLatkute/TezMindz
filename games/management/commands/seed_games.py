"""
Seed Management Command for Tezz-Mindz Game Engine: Dream House Builder.
Populates production-quality levels and dynamic content.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from academics.models import Class, Subject, ClassSubject, Chapter, Concept
from games.models import GameTemplate, Game, GameLevel, GameContent, GameHint, GameReward


class Command(BaseCommand):
    help = "Seed the Dream House Builder game with 5 levels and dynamic content"

    def handle(self, *args, **options):
        self.stdout.write("Starting Dream House Builder game seeding...")

        # ── 1. Locate Class 5 Mathematics Topic 1 ────────────────────────────
        cls5 = Class.objects.filter(grade_number=5).first()
        if not cls5:
            self.stdout.write(self.style.ERROR("Class 5 not found. Please run seed_chapter1 first."))
            return

        topic1 = Concept.objects.filter(
            chapter__class_subject__student_class=cls5,
            order=1
        ).first()

        if not topic1:
            self.stdout.write(self.style.ERROR("Topic 1 for Class 5 not found."))
            return

        # ── 2. Create or Update GameTemplate ─────────────────────────────────
        template, _ = GameTemplate.objects.get_or_create(
            slug="house_builder",
            defaults={
                "name": "Dream House Builder",
                "description": "Interactive virtual construction game teaching Indian place value, large numbers, comparison, and budgeting."
            }
        )

        # ── 3. Create or Update Game ─────────────────────────────────────────
        game, created = Game.objects.get_or_create(
            slug="dream-house-builder",
            defaults={
                "concept": topic1,
                "template": template,
                "title": "Dream House Builder",
                "game_type": "house_builder",
                "description": "Become a Junior House Builder! Buy land, pour the foundation, source materials, compare quotes, and balance the final budget to construct your ultimate Dream House!",
                "instructions": "Master each construction stage by reading, building, comparing, and verifying real-world large numbers in the Indian numbering system.",
                "difficulty": "medium",
                "estimated_time": 15,
                "xp_reward": 50,
                "coin_reward": 15,
                "is_active": True,
                "config": {
                    "theme": "construction_adventure",
                    "total_levels": 5,
                    "target_house": "Villa Royale"
                }
            }
        )
        if not created and game.concept != topic1:
            game.concept = topic1
            game.template = template
            game.game_type = "house_builder"
            game.save()

        self.stdout.write(self.style.SUCCESS(f"Game '{game.title}' verified."))

        # ── 4. Create 5 Levels ───────────────────────────────────────────────
        levels_data = [
            {
                "level_number": 1,
                "title": "Buy the Land",
                "instructions": "Inspect property listings and correctly read large property prices in the Indian Numbering System.",
                "difficulty": "easy",
                "time_limit": 60,
                "points": 100,
                "xp": 10,
                "coins": 3,
                "config": {"house_stage": 1, "stage_name": "Land Purchased"}
            },
            {
                "level_number": 2,
                "title": "Build the Foundation",
                "instructions": "Arrange digits into the exact place value positions to form the foundation budget.",
                "difficulty": "easy",
                "time_limit": 90,
                "points": 150,
                "xp": 12,
                "coins": 3,
                "config": {"house_stage": 2, "stage_name": "Concrete Foundation Poured"}
            },
            {
                "level_number": 3,
                "title": "Buy Building Material",
                "instructions": "Analyze construction invoices using the Indian Place Value chart (Lakhs, Thousands, Ones).",
                "difficulty": "medium",
                "time_limit": 75,
                "points": 150,
                "xp": 15,
                "coins": 4,
                "config": {"house_stage": 3, "stage_name": "Walls & Windows Built"}
            },
            {
                "level_number": 4,
                "title": "Choose the Best Material",
                "instructions": "Compare supplier quotes using >, <, = and order material costs from lowest to highest.",
                "difficulty": "medium",
                "time_limit": 90,
                "points": 150,
                "xp": 15,
                "coins": 4,
                "config": {"house_stage": 4, "stage_name": "Roof & Structure Completed"}
            },
            {
                "level_number": 5,
                "title": "Complete Your Dream House",
                "instructions": "Perform the final architectural budget verification to complete your Dream House!",
                "difficulty": "hard",
                "time_limit": 120,
                "points": 200,
                "xp": 25,
                "coins": 5,
                "config": {"house_stage": 5, "stage_name": "Dream House Complete"}
            },
        ]

        created_levels = {}
        for l_data in levels_data:
            lvl, _ = GameLevel.objects.get_or_create(
                game=game,
                level_number=l_data["level_number"],
                defaults={
                    "title": l_data["title"],
                    "instructions": l_data["instructions"],
                    "difficulty": l_data["difficulty"],
                    "time_limit": l_data["time_limit"],
                    "points": l_data["points"],
                    "xp_reward": l_data["xp"],
                    "coin_reward": l_data["coins"],
                    "configuration": l_data["config"],
                    "is_locked": False if l_data["level_number"] == 1 else True,
                }
            )
            created_levels[l_data["level_number"]] = lvl

        self.stdout.write(self.style.SUCCESS("All 5 Game Levels verified."))

        # ── 5. Create Dynamic GameContent for Each Level ─────────────────────
        # Level 1 Content (Read Number)
        lvl1 = created_levels[1]
        GameContent.objects.filter(level=lvl1).delete()

        c1_1 = GameContent.objects.create(
            game=game,
            level=lvl1,
            content_type="read_number",
            question="The Riverside Plot is on sale for ₹2,50,000. How do you read this property price?",
            data={
                "property_name": "Riverside Prime Plot",
                "price": 250000,
                "formatted_price": "₹2,50,000",
                "options": [
                    "Two Lakh Fifty Thousand",
                    "Twenty-Five Thousand",
                    "Two Thousand Five Hundred",
                    "Twenty-Five Lakh"
                ]
            },
            correct_answer={"value": "Two Lakh Fifty Thousand"},
            hint="Look at the comma groups: 2 is before the Lakhs comma, and 50 is before the Thousands comma.",
            explanation="In the Indian System, 2,50,000 is read as 'Two Lakh Fifty Thousand' (2 Lakhs + 50 Thousands).",
            points=100,
            display_order=1
        )
        GameHint.objects.create(content=c1_1, level=lvl1, order=1, text="The first comma from left separates the Lakhs period.", cost_points=10)
        GameHint.objects.create(content=c1_1, level=lvl1, order=2, text="2 is in the Lakhs place, followed by 50 in the Thousands place.", cost_points=15)

        c1_2 = GameContent.objects.create(
            game=game,
            level=lvl1,
            content_type="read_number",
            question="The Hilltop Luxury Plot costs ₹3,75,000. Select the correct number name:",
            data={
                "property_name": "Hilltop Luxury Estate",
                "price": 375000,
                "formatted_price": "₹3,75,000",
                "options": [
                    "Three Lakh Seventy-Five Thousand",
                    "Thirty-Seven Thousand Five Hundred",
                    "Three Lakh Seven Thousand Five Hundred",
                    "Three Million Seventy-Five Thousand"
                ]
            },
            correct_answer={"value": "Three Lakh Seventy-Five Thousand"},
            hint="3 is in the Lakhs period and 75 is in the Thousands period.",
            explanation="3,75,000 is 'Three Lakh Seventy-Five Thousand'.",
            points=100,
            display_order=2
        )

        # Level 2 Content (Build Number)
        lvl2 = created_levels[2]
        GameContent.objects.filter(level=lvl2).delete()

        c2_1 = GameContent.objects.create(
            game=game,
            level=lvl2,
            content_type="build_number",
            question="The civil engineer requires 'Three Lakh Twenty-Five Thousand' for the foundation concrete. Build this amount using the digits below:",
            data={
                "target_words": "Three Lakh Twenty-Five Thousand",
                "target_number": 325000,
                "digits_pool": [0, 5, 7, 2, 1, 0, 3, 4, 0, 8],
                "slots": ["Lakhs", "T-Th", "Th", "Hundreds", "Tens", "Ones"]
            },
            correct_answer={"number": 325000, "value": "325000"},
            hint="Place 3 in Lakhs, 2 in Ten-Thousands, 5 in Thousands, and zeroes in the rest.",
            explanation="3 in Lakhs, 25 in Thousands, and 000 in Ones = 3,25,000.",
            points=150,
            display_order=1
        )
        GameHint.objects.create(content=c2_1, level=lvl2, order=1, text="Start from the highest place: 'Three Lakh' means place 3 first.", cost_points=10)
        GameHint.objects.create(content=c2_1, level=lvl2, order=2, text="'Twenty-Five Thousand' has 2 in Ten-Thousands and 5 in Thousands.", cost_points=15)

        c2_2 = GameContent.objects.create(
            game=game,
            level=lvl2,
            content_type="build_number",
            question="The steel reinforcement contractor quote is 'Four Lakh Eight Thousand Two Hundred'. Build this budget figure:",
            data={
                "target_words": "Four Lakh Eight Thousand Two Hundred",
                "target_number": 408200,
                "digits_pool": [0, 8, 4, 0, 1, 0, 5, 2, 9, 7],
                "slots": ["Lakhs", "T-Th", "Th", "Hundreds", "Tens", "Ones"]
            },
            correct_answer={"number": 408200, "value": "408200"},
            hint="4 in Lakhs, 0 in Ten-Thousands, 8 in Thousands, 2 in Hundreds, 0 in Tens and Ones.",
            explanation="4 Lakhs + 08 Thousands + 200 = 4,08,200.",
            points=150,
            display_order=2
        )

        # Level 3 Content (Place Value)
        lvl3 = created_levels[3]
        GameContent.objects.filter(level=lvl3).delete()

        c3_1 = GameContent.objects.create(
            game=game,
            level=lvl3,
            content_type="place_value",
            question="The invoice for Structural Steel is ₹2,50,000. What is the PLACE VALUE of digit 5 in this price?",
            data={
                "material": "Structural Steel",
                "price": 250000,
                "target_digit": 5,
                "chart": [
                    {"period": "Lakhs", "place": "Lakhs", "digit": 2},
                    {"period": "Thousands", "place": "Ten-Thousands", "digit": 5},
                    {"period": "Thousands", "place": "Thousands", "digit": 0},
                    {"period": "Ones", "place": "Hundreds", "digit": 0},
                    {"period": "Ones", "place": "Tens", "digit": 0},
                    {"period": "Ones", "place": "Ones", "digit": 0},
                ],
                "options": [
                    "50,000 (Ten-Thousands)",
                    "5,000 (Thousands)",
                    "500 (Hundreds)",
                    "5 Lakhs"
                ]
            },
            correct_answer={"value": "50,000 (Ten-Thousands)"},
            hint="Digit 5 is the 5th digit from the right (Ten-Thousands place). 5 × 10,000 = 50,000.",
            explanation="The digit 5 is in the Ten-Thousands place, so its place value is 5 × 10,000 = 50,000.",
            points=150,
            display_order=1
        )
        GameHint.objects.create(content=c3_1, level=lvl3, order=1, text="Count the place from the right: Ones, Tens, Hundreds, Thousands, Ten-Thousands.", cost_points=10)

        c3_2 = GameContent.objects.create(
            game=game,
            level=lvl3,
            content_type="place_value",
            question="In the Red Clay Bricks invoice of ₹1,25,400, what is the place value of the digit 1?",
            data={
                "material": "Red Clay Bricks",
                "price": 125400,
                "target_digit": 1,
                "options": [
                    "1,00,000 (One Lakh)",
                    "10,000 (Ten-Thousands)",
                    "1,000 (Thousands)",
                    "100 (Hundreds)"
                ]
            },
            correct_answer={"value": "1,00,000 (One Lakh)"},
            hint="Digit 1 is in the Lakhs place. 1 × 1,00,000 = 1,00,000.",
            explanation="1 is in the Lakhs place, representing ₹1,00,000.",
            points=150,
            display_order=2
        )

        # Level 4 Content (Compare & Order)
        lvl4 = created_levels[4]
        GameContent.objects.filter(level=lvl4).delete()

        c4_1 = GameContent.objects.create(
            game=game,
            level=lvl4,
            content_type="compare_order",
            question="Compare the flooring quotes: Italian Marble (₹3,12,000) vs Ceramic Tiles (₹2,45,000). Which comparison symbol is correct?",
            data={
                "type": "comparison",
                "item_a": {"name": "Italian Marble", "price": 312000, "formatted": "₹3,12,000"},
                "item_b": {"name": "Ceramic Tiles", "price": 245000, "formatted": "₹2,45,000"},
                "options": [
                    "> (Greater than)",
                    "< (Less than)",
                    "= (Equal to)"
                ]
            },
            correct_answer={"operator": ">", "value": "> (Greater than)"},
            hint="Compare the leftmost digit (Lakhs place): 3 Lakhs is greater than 2 Lakhs.",
            explanation="₹3,12,000 > ₹2,45,000 because 3 in Lakhs place > 2 in Lakhs place.",
            points=150,
            display_order=1
        )

        c4_2 = GameContent.objects.create(
            game=game,
            level=lvl4,
            content_type="compare_order",
            question="Arrange these 4 roofing material quotes from LOWEST (Cheapest) to HIGHEST (Most Expensive):",
            data={
                "type": "ordering",
                "items": [
                    {"id": 1, "name": "Clay Roof Tiles", "price": 125000, "formatted": "₹1,25,000"},
                    {"id": 2, "name": "Solar Glass Panels", "price": 400000, "formatted": "₹4,00,000"},
                    {"id": 3, "name": "Galvanized Steel", "price": 210000, "formatted": "₹2,10,000"},
                    {"id": 4, "name": "Teak Wood Trusses", "price": 350000, "formatted": "₹3,50,000"},
                ]
            },
            correct_answer={"order": [125000, 210000, 350000, 400000]},
            hint="Inspect the Lakhs and Ten-Thousands places: 1,25,000 < 2,10,000 < 3,50,000 < 4,00,000.",
            explanation="The correct ascending order is: ₹1,25,000 (Clay) < ₹2,10,000 (Steel) < ₹3,50,000 (Wood) < ₹4,00,000 (Solar).",
            points=150,
            display_order=2
        )

        # Level 5 Content (Budget Verification)
        lvl5 = created_levels[5]
        GameContent.objects.filter(level=lvl5).delete()

        c5_1 = GameContent.objects.create(
            game=game,
            level=lvl5,
            content_type="budget_verification",
            question="The chief architect presents the final Dream House Budget: 'Eight Lakh Thirty-Five Thousand' (₹8,35,000). Verify whether the itemized expenses equal this total:",
            data={
                "target_total_words": "Eight Lakh Thirty-Five Thousand",
                "target_total_number": 835000,
                "expenses": [
                    {"item": "1. Prime Plot of Land", "amount": 250000, "formatted": "₹2,50,000"},
                    {"item": "2. Foundation & Structure", "amount": 125000, "formatted": "₹1,25,000"},
                    {"item": "3. Walls, Roof & Materials", "amount": 310000, "formatted": "₹3,10,000"},
                    {"item": "4. Interior Finishing & Lights", "amount": 150000, "formatted": "₹1,50,000"},
                ],
                "expanded_sum_check": "2,50,000 + 1,25,000 + 3,10,000 + 1,50,000",
                "options": [
                    "Yes, the budget total is EXACTLY ₹8,35,000 ✓",
                    "No, the total is ₹7,35,000",
                    "No, the total is ₹9,35,000"
                ]
            },
            correct_answer={"is_correct_budget": True, "value": "Yes, the budget total is EXACTLY ₹8,35,000 ✓"},
            hint="Add the Lakhs: 2 + 1 + 3 + 1 = 7 Lakhs. Add Thousands: 50 + 25 + 10 + 50 = 135 Thousands (1 Lakh 35 Thousand). Total = 8,35,000.",
            explanation="2,50,000 + 1,25,000 + 3,10,000 + 1,50,000 = ₹8,35,000 (Eight Lakh Thirty-Five Thousand). The budget is perfectly balanced!",
            points=200,
            display_order=1
        )

        # ── 6. Setup Game Rewards ────────────────────────────────────────────
        GameReward.objects.filter(game=game).delete()
        GameReward.objects.create(
            game=game,
            reward_type="game_complete",
            title="Master House Builder Trophy",
            description="Awarded for successfully constructing the entire 5-stage Dream House!",
            xp_reward=50,
            coin_reward=15,
            badge_icon="🏠"
        )
        GameReward.objects.create(
            game=game,
            reward_type="perfect_accuracy",
            title="Architectural Precision Star",
            description="Achieved 100% accuracy across all mathematical construction stages!",
            xp_reward=25,
            coin_reward=5,
            badge_icon="⭐"
        )

        self.stdout.write(self.style.SUCCESS("All 5 Levels & Dynamic Content for 'Dream House Builder' seeded successfully!"))
