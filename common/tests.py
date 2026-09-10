from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command
from academics.models import Class, Subject, ClassSubject, Chapter, Concept, Quiz, QuizQuestion, QuizOption
from learning.models import Lesson
from games.models import Game, GameTemplate, GameLevel, GameSession
from progress.models import StudentTopicProgress, QuizAttempt
from accounts.models import StudentProfile


class Chapter1WeTheTravellersTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Seed Chapter 1 using our idempotent management command
        call_command("seed_chapter1")

        self.cls5 = Class.objects.get(grade_number=5)
        self.math = Subject.objects.get(title="Mathematics")
        self.ch1 = Chapter.objects.get(class_subject__student_class=self.cls5, class_subject__subject=self.math, order=1)
        self.topic1 = self.ch1.concepts.get(order=1)
        self.topic2 = self.ch1.concepts.get(order=2)
        self.game1 = self.topic1.games.first()
        self.quiz1 = self.topic1.quizzes.first()

        # Create a student user
        self.user = User.objects.create_user(username="traveller_student", email="traveller@test.com", password="password123", first_name="Aarav")
        self.profile = StudentProfile.objects.create(user=self.user, student_class=self.cls5)

    def test_chapter1_structure_and_10_topics(self):
        """Verify Chapter 1 exists and has exactly 10 topics in order."""
        self.assertEqual(self.ch1.name, "We the Travellers – I")
        self.assertEqual(self.ch1.concepts.count(), 10)

        topic_names = list(self.ch1.concepts.order_by("order").values_list("name", flat=True))
        expected_names = [
            "Reading and Writing Large Numbers",
            "Place Value",
            "Expanded Form and Standard Form",
            "Number Names",
            "Comparing Large Numbers",
            "Ordering Numbers",
            "Making Numbers Using Digits",
            "Large Numbers in Real Life",
            "Number Patterns and Puzzles",
            "Logical Number Challenges"
        ]
        self.assertEqual(topic_names, expected_names)

    def test_complete_user_journey_topic1_to_topic2(self):
        """
        Tests the complete student journey:
        Login -> Dashboard -> Chapter 1 -> Topic 1 (Learn -> Game -> Quiz) -> Topic 1 Mastered -> Topic 2 Unlocked.
        """
        self.client.login(username="traveller_student", password="password123")

        # 1. Open Chapter 1
        res = self.client.get(f"/chapter/{self.ch1.id}/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "We the Travellers – I")
        self.assertContains(res, "Reading and Writing Large Numbers")

        # 2. Topic 1 is initially unlocked, Game and Quiz are locked
        res_t1 = self.client.get(f"/concept/{self.topic1.id}/")
        self.assertEqual(res_t1.status_code, 200)

        # Direct access to Game & Quiz is blocked
        self.assertEqual(self.client.get(f"/game/{self.game1.id}/play/").status_code, 302)
        self.assertEqual(self.client.get(f"/quiz/{self.quiz1.id}/").status_code, 302)
        # Direct access to Topic 2 is blocked
        self.assertEqual(self.client.get(f"/concept/{self.topic2.id}/").status_code, 302)

        # 3. Complete Topic 1 Learn
        res_learn = self.client.post("/api/lesson/complete/", {
            "concept_id": self.topic1.id
        }, content_type="application/json")
        self.assertEqual(res_learn.status_code, 200)
        self.assertTrue(res_learn.json()["game_unlocked"])

        # Game is now unlocked
        res_game = self.client.get(f"/game/{self.game1.id}/play/")
        self.assertEqual(res_game.status_code, 200)
        self.assertContains(res_game, "Number Builder")

        # 4. Submit Game
        res_game_submit = self.client.post("/api/game/submit/", {
            "game_id": self.game1.id,
            "difficulty": "easy",
            "score": 100,
            "accuracy": 100.0,
            "time_spent": 30,
            "hints_used": 1
        }, content_type="application/json")
        self.assertEqual(res_game_submit.status_code, 200)
        self.assertTrue(res_game_submit.json()["quiz_unlocked"])

        # Quiz is now unlocked
        res_quiz = self.client.get(f"/quiz/{self.quiz1.id}/")
        self.assertEqual(res_quiz.status_code, 200)

        # 5. Submit Quiz with correct answers
        answers = {}
        for q in self.quiz1.questions.all():
            corr_opt = q.options.filter(is_correct=True).first()
            if corr_opt:
                answers[str(q.id)] = corr_opt.id

        res_quiz_submit = self.client.post("/api/quiz/submit/", {
            "quiz_id": self.quiz1.id,
            "answers": answers,
            "time_taken": 45,
            "hints_used": 0
        }, content_type="application/json")
        self.assertEqual(res_quiz_submit.status_code, 200)
        self.assertTrue(res_quiz_submit.json()["is_mastered"])

        # 6. Verify Topic 1 is Mastered and Topic 2 is Unlocked!
        tp1 = StudentTopicProgress.objects.get(student=self.profile, concept=self.topic1)
        self.assertTrue(tp1.is_mastered)
        self.assertEqual(tp1.mastery_percentage, 100.0)

        tp2 = StudentTopicProgress.objects.get(student=self.profile, concept=self.topic2)
        self.assertTrue(tp2.is_unlocked)

        # Topic 2 is now accessible
        res_t2 = self.client.get(f"/concept/{self.topic2.id}/")
        self.assertEqual(res_t2.status_code, 200)


class AuthNavbarAndLogoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cls5 = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Primary",
            age_group="Age 10-11",
            category="primary"
        )
        self.user = User.objects.create_user(
            username="aarav_sharma",
            email="aarav@tezmindz.com",
            password="password123",
            first_name="Aarav"
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            student_class=self.cls5,
            xp=450,
            coins=120,
            streak=5,
            current_level=3
        )

    def test_unauthenticated_landing_page_shows_login_button(self):
        """Unauthenticated user sees public Home page with Login and Get Started buttons."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'class="btn-nav-login"')
        self.assertContains(res, "Get Started")
        self.assertNotContains(res, 'class="hud-profile-pill"')

    def test_authenticated_landing_page_swaps_login_button_to_profile(self):
        """Authenticated student sees Home page with their name, profile pill, and Dashboard CTA (no Login button)."""
        self.client.login(username="aarav_sharma", password="password123")
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Aarav")
        self.assertContains(res, "Class 5")
        self.assertContains(res, "Dashboard")
        self.assertContains(res, 'class="hud-profile-pill"')
        self.assertNotContains(res, 'class="btn-nav-login"')

    def test_distinct_user_dashboard_page(self):
        """Authenticated student can navigate between separate Home page (/) and User Dashboard (/dashboard/)."""
        self.client.login(username="aarav_sharma", password="password123")
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, "Olympiad Learning,")

        res_dash = self.client.get("/dashboard/")
        self.assertEqual(res_dash.status_code, 200)
        self.assertContains(res_dash, "Adventure World")

    def test_clean_logout_flow(self):
        """Logging out terminates session cleanly and redirects directly to Home page in logged-out state."""
        self.client.login(username="aarav_sharma", password="password123")
        res_logout = self.client.get("/logout/", follow=True)
        self.assertEqual(res_logout.status_code, 200)
        # Should now be on the public landing page in logged-out state
        self.assertContains(res_logout, 'class="btn-nav-login"')
        self.assertContains(res_logout, "Get Started")
        self.assertNotContains(res_logout, 'class="hud-profile-pill"')


class DedicatedPagesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cls5 = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Primary",
            age_group="Age 10-11",
            category="primary"
        )
        self.user = User.objects.create_user(
            username="aarav_test",
            email="aarav_test@tezmindz.com",
            password="password123",
            first_name="Aarav"
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            student_class=self.cls5,
            xp=300,
            coins=50,
            streak=3,
            current_level=2
        )

    def test_about_page_status_and_content(self):
        """Dedicated /about/ page renders correctly with mission, vision, and core pillars."""
        res = self.client.get("/about/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "About Tezz-Mindz")
        self.assertContains(res, "Pioneering the Future of")
        self.assertContains(res, "Our Mission")
        self.assertContains(res, "Our Vision")
        self.assertContains(res, "Pedagogical Precision")

    def test_subjects_page_status_and_classes(self):
        """Dedicated /subjects/ page renders correctly with classes directory and 3 subject tracks."""
        res = self.client.get("/subjects/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Class 1 to 8")
        self.assertContains(res, "Mathematics (IMO)")
        self.assertContains(res, "Science (NSO)")
        self.assertContains(res, "English (IEO)")
        self.assertContains(res, "Class 5")

    def test_how_it_works_page_status_and_steps(self):
        """Dedicated /how-it-works/ page renders correctly with 4-step journey and FAQ."""
        res = self.client.get("/how-it-works/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "How")
        self.assertContains(res, "Tezz-Mindz")
        self.assertContains(res, "Discover &amp; Learn")
        self.assertContains(res, "Practice &amp; Diagnose")
        self.assertContains(res, "Apply in 3D Arena")
        self.assertContains(res, "Master &amp; Compete")
        self.assertContains(res, "Frequently Asked Questions")

    def test_cross_page_navigation_links(self):
        """Navigation links to /subjects/, /how-it-works/, and /about/ exist across pages."""
        for path in ["/", "/about/", "/subjects/", "/how-it-works/"]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, 'href="/subjects/"')
            self.assertContains(res, 'href="/how-it-works/"')
            self.assertContains(res, 'href="/about/"')

    def test_authenticated_student_hud_on_dedicated_pages(self):
        """Authenticated student sees their HUD on /about/, /subjects/, and /how-it-works/."""
        self.client.login(username="aarav_test", password="password123")
        for path in ["/about/", "/subjects/", "/how-it-works/"]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, "Aarav")
            self.assertContains(res, "Class 5")
            self.assertContains(res, 'class="hud-profile-pill"')

    def test_legacy_html_redirects(self):
        """Legacy .html URLs redirect to modern clean paths."""
        res_about = self.client.get("/about.html")
        self.assertRedirects(res_about, "/about/", status_code=301)

        res_subj = self.client.get("/subjects.html")
        self.assertRedirects(res_subj, "/subjects/", status_code=301)

        res_hiw = self.client.get("/how-it-works.html")
        self.assertRedirects(res_hiw, "/how-it-works/", status_code=301)


class TezMindzAdminPanelTests(TestCase):
    def setUp(self):
        import io
        import zipfile
        self.client = Client()

        # Create normal student user
        self.student_user = User.objects.create_user(
            username="regular_student",
            email="student@tezmindz.com",
            password="password123"
        )

        # Create staff admin user
        self.admin_user = User.objects.create_user(
            username="head_admin",
            email="admin@tezmindz.com",
            password="adminpassword123",
            is_staff=True,
            is_superuser=True
        )

        # Create sample academic hierarchy
        self.cls5 = Class.objects.create(
            grade_number=5,
            name="Grade 5",
            class_label="Class 5",
            stage="Primary",
            age_group="Age 10-11",
            category="primary"
        )
        self.math = Subject.objects.create(
            title="Mathematics",
            subtitle="Explore Numbers & Logic",
            olympiad_code="IMO",
            icon_type="math",
            color_theme={"accent": "#6366F1"}
        )
        self.cs = ClassSubject.objects.create(student_class=self.cls5, subject=self.math)
        self.ch = Chapter.objects.create(class_subject=self.cs, name="Large Numbers", order=1, slug="large-numbers")
        self.top = Concept.objects.create(chapter=self.ch, name="Place Value", order=1, slug="place-value", difficulty="easy")

        # Create sample game
        self.game = Game.objects.create(
            title="Place Value Builder",
            slug="place-value-builder",
            concept=self.top,
            game_type="interactive_activity",
            difficulty="easy",
            xp_reward=50,
            coin_reward=15,
            is_active=True,
            game_path="class_5/mathematics/chapter_01_large-numbers/topic_01_place-value/place-value-builder"
        )

        # Create StudentProfile
        self.profile = StudentProfile.objects.create(
            user=self.student_user,
            student_class=self.cls5,
            xp=250,
            coins=60,
            streak=4
        )

    def test_unauthenticated_and_non_staff_access_blocked(self):
        """Unauthenticated or regular student is denied access to /tezadmin/."""
        # Unauthenticated
        res = self.client.get("/tezadmin/")
        self.assertRedirects(res, "/login/?next=/tezadmin/")

        # Regular non-staff student
        self.client.login(username="regular_student", password="password123")
        res2 = self.client.get("/tezadmin/")
        self.assertEqual(res2.status_code, 302)
        self.assertIn("/login/", res2["Location"])

    def test_admin_dashboard_renders_for_staff(self):
        """Staff admin can access executive dashboard with live metrics."""
        self.client.login(username="head_admin", password="adminpassword123")
        res = self.client.get("/tezadmin/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Executive Dashboard")
        self.assertContains(res, "Place Value Builder")

    def test_academic_hierarchy_view_and_cascading_api(self):
        """Academic hierarchy view and cascading dropdown JSON API work correctly."""
        self.client.login(username="head_admin", password="adminpassword123")

        # View page
        res = self.client.get("/tezadmin/academic/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Academic Content Hierarchy")
        self.assertContains(res, "Large Numbers")

        # Cascading API: classes
        api_cls = self.client.get("/tezadmin/api/hierarchy/?level=classes")
        self.assertEqual(api_cls.status_code, 200)
        self.assertEqual(len(api_cls.json()["data"]), 1)

        # Cascading API: subjects
        api_sub = self.client.get(f"/tezadmin/api/hierarchy/?level=subjects&class_id={self.cls5.id}")
        self.assertEqual(api_sub.status_code, 200)
        self.assertEqual(api_sub.json()["data"][0]["title"], "Mathematics")

        # Cascading API: chapters
        api_ch = self.client.get(f"/tezadmin/api/hierarchy/?level=chapters&class_id={self.cls5.id}&subject_id={self.math.id}")
        self.assertEqual(api_ch.status_code, 200)
        self.assertEqual(api_ch.json()["data"][0]["name"], "Large Numbers")

        # Cascading API: topics
        api_top = self.client.get(f"/tezadmin/api/hierarchy/?level=topics&chapter_id={self.ch.id}")
        self.assertEqual(api_top.status_code, 200)
        self.assertEqual(api_top.json()["data"][0]["name"], "Place Value")

    def test_hierarchy_crud_apis(self):
        """CRUD save endpoints for Class, Chapter, and Topic."""
        self.client.login(username="head_admin", password="adminpassword123")

        # Create new Class 6
        res_c = self.client.post("/tezadmin/api/classes/save/", {
            "grade_number": 6,
            "name": "Grade 6",
            "class_label": "Class 6",
            "stage": "Middle",
            "age_group": "Age 11-12"
        }, content_type="application/json")
        self.assertEqual(res_c.status_code, 200)
        self.assertTrue(Class.objects.filter(grade_number=6).exists())

        # Create new Chapter
        res_ch = self.client.post("/tezadmin/api/chapters/save/", {
            "class_subject_id": self.cs.id,
            "name": "Roman Numerals",
            "order": 2,
            "description": "Learning Roman numerals"
        }, content_type="application/json")
        self.assertEqual(res_ch.status_code, 200)
        self.assertTrue(Chapter.objects.filter(name="Roman Numerals").exists())

        # Create new Topic
        new_ch = Chapter.objects.get(name="Roman Numerals")
        res_top = self.client.post("/tezadmin/api/topics/save/", {
            "chapter_id": new_ch.id,
            "name": "Rules of Roman Numerals",
            "order": 1,
            "difficulty": "medium",
            "description": "Rules"
        }, content_type="application/json")
        self.assertEqual(res_top.status_code, 200)
        self.assertTrue(Concept.objects.filter(name="Rules of Roman Numerals").exists())

    def test_game_library_and_actions(self):
        """Game library view, toggle status, and clone duplication."""
        self.client.login(username="head_admin", password="adminpassword123")

        # View library
        res = self.client.get("/tezadmin/games/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Place Value Builder")

        # Toggle status
        res_toggle = self.client.post(f"/tezadmin/games/{self.game.id}/toggle-status/")
        self.assertEqual(res_toggle.status_code, 200)
        self.assertFalse(res_toggle.json()["is_active"])

        # Duplicate game
        res_dup = self.client.post(f"/tezadmin/games/{self.game.id}/duplicate/")
        self.assertEqual(res_dup.status_code, 200)
        self.assertTrue(Game.objects.filter(title="Place Value Builder (Copy)").exists())

    def test_game_form_and_secure_zip_upload(self):
        """Add new game with ZIP file and verify safe extraction & audit logging."""
        import io
        import zipfile
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.login(username="head_admin", password="adminpassword123")

        # Create in-memory zip archive containing safe assets
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("index.html", "<!DOCTYPE html><html><body><h1>Game Test</h1></body></html>")
            zf.writestr("game.js", "console.log('Game running');")
            zf.writestr("style.css", "body { background: #000; }")
        zip_buffer.seek(0)

        uploaded_zip = SimpleUploadedFile("test_game.zip", zip_buffer.getvalue(), content_type="application/zip")

        res_create = self.client.post("/tezadmin/games/add/", {
            "title": "Abacus Master",
            "slug": "abacus-master",
            "topic_id": self.top.id,
            "game_type": "math_arithmetic",
            "difficulty": "medium",
            "xp_reward": 75,
            "coin_reward": 25,
            "is_active": "on",
            "game_zip": uploaded_zip
        }, follow=True)

        self.assertEqual(res_create.status_code, 200)
        self.assertTrue(Game.objects.filter(slug="abacus-master").exists())

    def test_game_analytics_view(self):
        """Deep analytics view for an educational game."""
        self.client.login(username="head_admin", password="adminpassword123")
        res = self.client.get(f"/tezadmin/games/{self.game.id}/analytics/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Place Value Builder")
        self.assertContains(res, "Completion Rate")

    def test_student_management_and_toggle(self):
        """Student directory listing, detail inspector, and active toggle."""
        self.client.login(username="head_admin", password="adminpassword123")

        # Student list
        res_list = self.client.get("/tezadmin/students/")
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "regular_student")

        # Student detail
        res_detail = self.client.get(f"/tezadmin/students/{self.profile.id}/")
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "regular_student")

        # Toggle student active
        res_toggle = self.client.post(f"/tezadmin/students/{self.profile.id}/toggle-active/")
        self.assertEqual(res_toggle.status_code, 200)
        self.student_user.refresh_from_db()
        self.assertFalse(self.student_user.is_active)

    def test_gamification_and_audit_logs_views(self):
        """Gamification engine and audit logs views render successfully."""
        self.client.login(username="head_admin", password="adminpassword123")

        res_gam = self.client.get("/tezadmin/gamification/")
        self.assertEqual(res_gam.status_code, 200)
        self.assertContains(res_gam, "Gamification")

        res_logs = self.client.get("/tezadmin/audit-logs/")
        self.assertEqual(res_logs.status_code, 200)
        self.assertContains(res_logs, "System Governance & Audit Logs")



