import json
from datetime import date, datetime, timedelta

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.utils import timezone

from academics.models import Class, Subject, ClassSubject, Chapter, Concept, Quiz, DailyChallenge
from accounts.models import StudentProfile
from games.models import Game, GameLevel, GameSession, Question, Attempt, Hint
from learning.models import Lesson
from rewards.models import (
    Badge, StudentBadge, XPTransaction, CoinTransaction,
    Achievement, StudentAchievement, StudentMission,
)
from progress.models import ConceptMastery, LessonProgress, QuizAttempt, StudentTopicProgress


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS & AUTHORIZATION
# ══════════════════════════════════════════════════════════════════════════════

def get_user_data_context(request):
    """Inject window.USER_DATA and profile into every template context safely."""
    context = {}
    if request.user.is_authenticated:
        profile = _get_profile(request)
        context["profile"] = profile
        try:
            if profile and hasattr(profile, "student_class") and profile.student_class:
                class_level = profile.student_class.grade_number
                class_label = profile.student_class.class_label
            else:
                class_level = 5
                class_label = "Class 5"

            user_data = {
                "name": request.user.first_name or request.user.username,
                "username": request.user.username,
                "classLevel": class_level,
                "classLabel": class_label,
                "xp": getattr(profile, "xp", 0) if profile else 0,
                "coins": getattr(profile, "coins", 0) if profile else 0,
                "streak": getattr(profile, "streak", 0) if profile else 0,
                "level": getattr(profile, "current_level", 1) if profile else 1,
                "loggedIn": True,
            }
        except Exception:
            user_data = {
                "name": request.user.username,
                "username": request.user.username,
                "classLevel": 5,
                "classLabel": "Class 5",
                "xp": 0, "coins": 0, "streak": 0, "level": 1,
                "loggedIn": True,
            }
        context["user_data_js"] = json.dumps(user_data)
    else:
        context["user_data_js"] = json.dumps({"loggedIn": False})
        context["profile"] = None
    return context


def _get_profile(request):
    """Shortcut: return authenticated student's profile, safely creating one if missing."""
    try:
        return request.user.profile
    except Exception:
        try:
            cls5 = Class.objects.filter(grade_number=5).first() or Class.objects.first()
            if not cls5:
                cls5 = Class.objects.create(
                    grade_number=5, class_label="Class 5", name="Grade 5",
                    stage="Primary", age_group="Age 10-11", category="primary"
                )
            prof, _ = StudentProfile.objects.get_or_create(
                user=request.user,
                defaults={"student_class": cls5, "xp": 0, "coins": 0, "streak": 1, "current_level": 1}
            )
            return prof
        except Exception:
            return None


def _get_student_class(profile):
    return profile.student_class


def _class_owns_chapter(profile, chapter):
    """Returns True if the chapter belongs to the student's class."""
    return chapter.class_subject.student_class_id == profile.student_class_id


def _class_owns_concept(profile, concept):
    return concept.chapter.class_subject.student_class_id == profile.student_class_id


def _class_owns_game(profile, game):
    return game.concept.chapter.class_subject.student_class_id == profile.student_class_id


def _class_owns_quiz(profile, quiz):
    return quiz.concept.chapter.class_subject.student_class_id == profile.student_class_id


def get_or_create_topic_progress(profile, concept):
    """
    Retrieves or initializes StudentTopicProgress for a student and concept.
    Topic 1 of Chapter 1 of each subject is automatically unlocked (is_unlocked=True).
    """
    tp, created = StudentTopicProgress.objects.get_or_create(
        student=profile,
        concept=concept,
        defaults={
            "is_unlocked": (concept.order == 1 and concept.chapter.order == 1)
        }
    )
    if not tp.is_unlocked:
        # Check if previous topic is mastered
        prev_concept = concept.chapter.concepts.filter(
            order__lt=concept.order, is_active=True
        ).order_by("-order").first()
        if prev_concept:
            prev_tp = StudentTopicProgress.objects.filter(student=profile, concept=prev_concept).first()
            if prev_tp and prev_tp.is_mastered:
                tp.is_unlocked = True
                tp.save(update_fields=["is_unlocked"])
    return tp


def award_xp(profile, points, reason):
    """Securely award XP to a student and record the transaction."""
    profile.xp = (profile.xp or 0) + points
    # Level formula: level = 1 + xp // 200
    profile.current_level = 1 + profile.xp // 200
    profile.save(update_fields=["xp", "current_level"])
    XPTransaction.objects.create(student=profile, points=points, reason=reason)
    check_achievements(profile)


def award_coins(profile, coins, reason):
    """Securely award coins to a student."""
    profile.coins = (profile.coins or 0) + coins
    profile.save(update_fields=["coins"])
    CoinTransaction.objects.create(student=profile, coins=coins, reason=reason)


def update_streak(profile):
    """Update daily learning streak."""
    today = date.today()
    last = profile.last_activity_date
    if last == today:
        return  # already counted today
    if last == today - timedelta(days=1):
        profile.streak = (profile.streak or 0) + 1
    else:
        profile.streak = 1  # reset streak
    profile.last_activity_date = today
    profile.save(update_fields=["streak", "last_activity_date"])


def check_achievements(profile):
    """Check and unlock any achievements the student qualifies for."""
    achievements = Achievement.objects.filter(is_active=True).exclude(
        id__in=StudentAchievement.objects.filter(student=profile).values_list("achievement_id", flat=True)
    )
    for ach in achievements:
        unlocked = False
        ct = ach.condition_type
        cv = ach.condition_value
        if ct == "xp_total" and profile.xp >= cv:
            unlocked = True
        elif ct == "streak_days" and profile.streak >= cv:
            unlocked = True
        elif ct == "games_completed":
            count = GameSession.objects.filter(student=profile, status="COMPLETED").count()
            unlocked = count >= cv
        elif ct == "lessons_completed":
            count = StudentTopicProgress.objects.filter(student=profile, learn_completed=True).count()
            unlocked = count >= cv
        elif ct == "quizzes_passed":
            count = StudentTopicProgress.objects.filter(student=profile, quiz_completed=True).count()
            unlocked = count >= cv
        elif ct == "first_game":
            unlocked = StudentTopicProgress.objects.filter(student=profile, game_completed=True).exists()
        elif ct == "first_lesson":
            unlocked = StudentTopicProgress.objects.filter(student=profile, learn_completed=True).exists()
        elif ct == "first_quiz":
            unlocked = StudentTopicProgress.objects.filter(student=profile, quiz_completed=True).exists()

        if unlocked:
            StudentAchievement.objects.get_or_create(student=profile, achievement=ach)
            if ach.xp_reward:
                award_xp(profile, ach.xp_reward, f"Achievement: {ach.name}")
            if ach.coin_reward:
                award_coins(profile, ach.coin_reward, f"Achievement: {ach.name}")


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC PAGES
# ══════════════════════════════════════════════════════════════════════════════

def landing_page(request):
    return render(request, "index.html", get_user_data_context(request))


def about_page(request):
    return render(request, "about.html", get_user_data_context(request))


def subjects_page(request):
    context = get_user_data_context(request)
    try:
        classes = Class.objects.filter(is_active=True).order_by("grade_number")
        class_subjects = (
            ClassSubject.objects.filter(student_class__is_active=True, subject__is_active=True)
            .select_related("student_class", "subject")
            .prefetch_related("chapters__concepts")
            .order_by("student_class__grade_number", "subject__title")
        )
        context["classes"] = classes
        context["class_subjects"] = class_subjects
    except Exception:
        context["classes"] = []
        context["class_subjects"] = []
    return render(request, "subjects.html", context)


def how_it_works_page(request):
    return render(request, "how_it_works.html", get_user_data_context(request))


def login_page(request):
    if request.user.is_authenticated:
        return redirect("common:dashboard")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            identifier = data.get("email", "")
            password = data.get("password", "")
        except Exception:
            identifier = request.POST.get("email", "")
            password = request.POST.get("password", "")

        user = User.objects.filter(email=identifier).first()
        if not user:
            user = User.objects.filter(username=identifier).first()

        if user and user.check_password(password):
            login(request, user)
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "message": "Invalid email or password."}, status=400)

    return render(request, "login.html", get_user_data_context(request))


def register_page(request):
    if request.user.is_authenticated:
        return redirect("common:dashboard")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            username = data.get("username", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
            class_level = int(data.get("classLevel", 5))
        except Exception:
            name = request.POST.get("name", "").strip()
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")
            class_level = int(request.POST.get("classLevel", 5))

        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email already registered."}, status=400)

        if username:
            if User.objects.filter(username=username).exists():
                return JsonResponse({"success": False, "message": "Username already taken."}, status=400)
        else:
            username = email.split("@")[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

        user = User.objects.create_user(
            username=username, email=email, password=password, first_name=name
        )

        cls_obj = Class.objects.filter(grade_number=class_level).first()
        if not cls_obj:
            cls_obj = Class.objects.filter(grade_number=5).first()

        profile = StudentProfile.objects.create(user=user, student_class=cls_obj)
        
        # Unlock Topic 1 of Math Chapter 1 by default
        first_concept = Concept.objects.filter(
            chapter__class_subject__student_class=cls_obj,
            chapter__order=1, order=1
        ).first()
        if first_concept:
            StudentTopicProgress.objects.get_or_create(
                student=profile, concept=first_concept,
                defaults={"is_unlocked": True}
            )

        login(request, user)
        return JsonResponse({"success": True})

    return render(request, "register.html", get_user_data_context(request))


def logout_page(request):
    logout(request)
    return redirect("common:landing")


@login_required
def class_select_page(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            grade = int(data.get("classLevel", 5))
        except Exception:
            grade = int(request.POST.get("classLevel", 5))

        cls = Class.objects.filter(grade_number=grade).first()
        if cls:
            profile = request.user.profile
            profile.student_class = cls
            profile.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "message": "Class not found."}, status=400)

    classes = Class.objects.filter(is_active=True).order_by("grade_number")
    context = get_user_data_context(request)
    context["classes"] = classes
    return render(request, "class.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def dashboard_page(request):
    profile = _get_profile(request)
    student_class = _get_student_class(profile)
    today = date.today()

    # Subjects for this class
    class_subjects = (
        ClassSubject.objects
        .filter(student_class=student_class)
        .select_related("subject")
        .order_by("subject__title")
    )
    for cs in class_subjects:
        total = Concept.objects.filter(chapter__class_subject=cs, is_active=True).count()
        done = StudentTopicProgress.objects.filter(
            student=profile, concept__chapter__class_subject=cs, is_mastered=True
        ).count()
        cs.total_concepts = total
        cs.done_concepts = done
        cs.progress_pct = round((done / total * 100) if total else 0)

    # Continue Learning - find active unlocked topic
    active_tp = (
        StudentTopicProgress.objects
        .filter(student=profile, is_unlocked=True, is_mastered=False)
        .select_related("concept__chapter__class_subject__subject")
        .order_by("concept__chapter__order", "concept__order")
        .first()
    )

    if not active_tp:
        # Fallback to first concept in curriculum
        first_concept = Concept.objects.filter(
            chapter__class_subject__student_class=student_class,
            is_active=True
        ).order_by("chapter__order", "order").first()
        if first_concept:
            active_tp = get_or_create_topic_progress(profile, first_concept)

    # Determine next learning activity for Continue Learning card
    continue_action_url = "/learn/"
    continue_action_text = "Continue Lesson →"
    continue_stage_label = "Learn Activity"
    
    if active_tp:
        concept = active_tp.concept
        if not active_tp.learn_completed:
            continue_action_url = f"/concept/{concept.id}/"
            continue_action_text = "Continue Lesson →"
            continue_stage_label = "Learn"
        elif not active_tp.game_completed:
            game = concept.games.first()
            continue_action_url = f"/game/{game.id}/play/" if game else f"/concept/{concept.id}/"
            continue_action_text = "Play Game →"
            continue_stage_label = "Play Game"
        elif not active_tp.quiz_completed:
            quiz = concept.quizzes.filter(is_active=True).first()
            continue_action_url = f"/quiz/{quiz.id}/" if quiz else f"/concept/{concept.id}/"
            continue_action_text = "Take Quiz →"
            continue_stage_label = "Quiz"

    # Today's daily challenge for this class
    today_challenge = DailyChallenge.objects.filter(
        student_class=student_class, date=today, is_active=True
    ).first()

    # Mini leaderboard
    classmates = (
        StudentProfile.objects
        .filter(student_class=student_class)
        .select_related("user")
        .order_by("-xp")[:5]
    )
    for idx, cm in enumerate(classmates, 1):
        cm.rank = idx

    my_rank = (
        StudentProfile.objects
        .filter(student_class=student_class, xp__gt=profile.xp)
        .count() + 1
    )

    # Progress summary
    total_concepts = Concept.objects.filter(
        chapter__class_subject__student_class=student_class, is_active=True
    ).count()
    completed_concepts = StudentTopicProgress.objects.filter(
        student=profile, is_mastered=True
    ).count()
    progress_pct = round((completed_concepts / total_concepts * 100) if total_concepts else 0)

    recent_sessions = (
        GameSession.objects
        .filter(student=profile, status="COMPLETED")
        .select_related("game__concept__chapter__class_subject__subject")
        .order_by("-completed_at")[:4]
    )

    recent_quizzes = (
        QuizAttempt.objects
        .filter(student=profile)
        .select_related("quiz__concept")
        .order_by("-started_at")[:3]
    )

    context = get_user_data_context(request)
    context.update({
        "student_class": student_class,
        "class_subjects": class_subjects,
        "continue_learning": active_tp,
        "continue_action_url": continue_action_url,
        "continue_action_text": continue_action_text,
        "continue_stage_label": continue_stage_label,
        "today_challenge": today_challenge,
        "classmates": classmates,
        "my_rank": my_rank,
        "total_concepts": total_concepts,
        "completed_concepts": completed_concepts,
        "progress_pct": progress_pct,
        "recent_sessions": recent_sessions,
        "recent_quizzes": recent_quizzes,
        "today": today,
    })
    return render(request, "dashboard.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# LEARNING PAGES & SEQUENTIAL TOPIC FLOW
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def learn_page(request):
    profile = _get_profile(request)
    student_class = _get_student_class(profile)

    class_subjects = (
        ClassSubject.objects
        .filter(student_class=student_class)
        .select_related("subject")
        .prefetch_related("chapters__concepts")
        .order_by("subject__title")
    )

    for cs in class_subjects:
        total = sum(ch.concepts.filter(is_active=True).count() for ch in cs.chapters.filter(is_active=True))
        done = StudentTopicProgress.objects.filter(
            student=profile,
            concept__chapter__class_subject=cs,
            is_mastered=True
        ).count()
        cs.total_concepts = total
        cs.done_concepts = done
        cs.progress_pct = round((done / total * 100) if total else 0)

    context = get_user_data_context(request)
    context.update({
        "student_class": student_class,
        "class_subjects": class_subjects,
    })
    return render(request, "learn.html", context)


@login_required
def subject_page(request, cs_id):
    profile = _get_profile(request)
    cs = get_object_or_404(
        ClassSubject.objects.select_related("student_class", "subject"),
        id=cs_id
    )
    if cs.student_class_id != profile.student_class_id:
        return redirect("common:learn")

    chapters = (
        Chapter.objects
        .filter(class_subject=cs, is_active=True)
        .prefetch_related("concepts")
        .order_by("order")
    )

    for ch in chapters:
        total = ch.concepts.filter(is_active=True).count()
        done = StudentTopicProgress.objects.filter(
            student=profile, concept__chapter=ch, is_mastered=True
        ).count()
        ch.total_concepts = total
        ch.done_concepts = done
        ch.progress_pct = round((done / total * 100) if total else 0)

    context = get_user_data_context(request)
    context.update({
        "class_subject": cs,
        "chapters": chapters,
        "student_class": cs.student_class,
    })
    return render(request, "subject.html", context)


@login_required
def chapter_page(request, chapter_id):
    profile = _get_profile(request)
    chapter = get_object_or_404(
        Chapter.objects.select_related("class_subject__student_class", "class_subject__subject"),
        id=chapter_id
    )
    if not _class_owns_chapter(profile, chapter):
        return redirect("common:learn")

    concepts = chapter.concepts.filter(is_active=True).order_by("order")

    # Retrieve or generate sequential topic progress for each topic
    for c in concepts:
        tp = get_or_create_topic_progress(profile, c)
        c.progress = tp
        c.has_quiz = c.quizzes.filter(is_active=True).exists()
        c.has_game = c.games.exists()

    context = get_user_data_context(request)
    context.update({
        "chapter": chapter,
        "concepts": concepts,
        "student_class": chapter.class_subject.student_class,
    })
    return render(request, "chapter.html", context)


@login_required
def concept_page(request, concept_id):
    """
    Dedicated Topic Learning Page showing Topic name, Chapter name, Progress,
    and three strictly sequenced activities: Learn -> Play Game -> Quiz.
    """
    profile = _get_profile(request)
    concept = get_object_or_404(
        Concept.objects.select_related(
            "chapter__class_subject__student_class",
            "chapter__class_subject__subject"
        ),
        id=concept_id
    )
    # Access control
    if not _class_owns_concept(profile, concept):
        return redirect("common:learn")

    # Sequence Unlocking Verification
    tp = get_or_create_topic_progress(profile, concept)
    if not tp.is_unlocked:
        # If locked, redirect to chapter page
        return redirect("common:chapter", chapter_id=concept.chapter_id)

    lessons = concept.lessons.order_by("order")
    quizzes = concept.quizzes.filter(is_active=True)
    games = concept.games.all()

    first_game = games.first()
    first_quiz = quizzes.first()
    quick_question = first_quiz.questions.prefetch_related("options").first() if first_quiz else None

    context = get_user_data_context(request)
    context.update({
        "concept": concept,
        "chapter": concept.chapter,
        "lessons": lessons,
        "quizzes": quizzes,
        "games": games,
        "first_game": first_game,
        "first_quiz": first_quiz,
        "quick_question": quick_question,
        "topic_progress": tp,
        "student_class": concept.chapter.class_subject.student_class,
    })
    return render(request, "concept.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# GAME ACTIVITY (BACKEND PROTECTED)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def difficulty_page(request, game_id):
    profile = _get_profile(request)
    game = get_object_or_404(
        Game.objects.select_related("concept__chapter__class_subject__student_class"),
        id=game_id
    )
    if not _class_owns_game(profile, game):
        return redirect("common:games")

    tp = get_or_create_topic_progress(profile, game.concept)
    if not tp.game_unlocked:
        return redirect("common:concept", concept_id=game.concept_id)

    context = get_user_data_context(request)
    context["game"] = game
    return render(request, "difficulty.html", context)


@login_required
def games_page(request):
    profile = _get_profile(request)
    games = (
        Game.objects
        .filter(concept__chapter__class_subject__student_class=profile.student_class)
        .select_related("concept__chapter__class_subject__subject")
    )
    context = get_user_data_context(request)
    context["games"] = games
    return render(request, "games.html", context)


@login_required
def game_page(request, game_id):
    """
    Dedicated Educational Game screen for the topic.
    Delegates to modular_game_runner_view for isolated game architecture.
    """
    from games.views import modular_game_runner_view as _runner
    profile = _get_profile(request)
    game = get_object_or_404(
        Game.objects.select_related("concept__chapter__class_subject__student_class"),
        id=game_id
    )
    if not _class_owns_game(profile, game):
        return redirect("common:games")

    # Sequence Check: Game requires Learn to be completed
    tp = get_or_create_topic_progress(profile, game.concept)
    if not tp.game_unlocked:
        return redirect("common:concept", concept_id=game.concept_id)

    return _runner(request, game_id=game_id)


def modular_game_runner_view(request, *args, **kwargs):
    """Lazy wrapper to prevent circular imports."""
    from games.views import modular_game_runner_view as _runner
    return _runner(request, *args, **kwargs)




@login_required
def result_page(request):
    profile = _get_profile(request)
    session = (
        GameSession.objects
        .filter(student=profile, status="COMPLETED")
        .select_related("game__concept__chapter__class_subject__subject")
        .order_by("-completed_at")
        .first()
    )
    
    next_quiz = None
    if session and session.game:
        next_quiz = session.game.concept.quizzes.filter(is_active=True).first()

    context = get_user_data_context(request)
    context["session"] = session
    context["next_quiz"] = next_quiz
    return render(request, "result.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# QUIZ ACTIVITY (BACKEND PROTECTED)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def quiz_page(request, quiz_id):
    """
    Child-friendly interactive Quiz screen.
    Backend verifies that Game is completed (quiz_unlocked=True).
    """
    profile = _get_profile(request)
    quiz = get_object_or_404(
        Quiz.objects.select_related("concept__chapter__class_subject__student_class"),
        id=quiz_id, is_active=True
    )
    if not _class_owns_quiz(profile, quiz):
        return redirect("common:learn")

    # Sequence Check: Quiz requires Game to be completed
    tp = get_or_create_topic_progress(profile, quiz.concept)
    if not tp.quiz_unlocked:
        return redirect("common:concept", concept_id=quiz.concept_id)

    questions = quiz.questions.prefetch_related("options").order_by("display_order")

    context = get_user_data_context(request)
    context.update({
        "quiz": quiz,
        "concept": quiz.concept,
        "questions": questions,
        "questions_json": json.dumps([
            {
                "id": q.id,
                "text": q.question_text,
                "marks": q.marks,
                "explanation": q.explanation,
                "options": [{"id": o.id, "text": o.option_text, "order": o.order, "is_correct": o.is_correct} for o in q.options.all()],
            }
            for q in questions
        ]),
        "topic_progress": tp,
    })
    return render(request, "quiz.html", context)


@login_required
def quiz_result_page(request, attempt_id):
    profile = _get_profile(request)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=profile)
    tp = StudentTopicProgress.objects.filter(student=profile, concept=attempt.quiz.concept).first()

    # Find next topic if mastered
    next_concept = None
    if tp and tp.is_mastered:
        next_concept = attempt.quiz.concept.chapter.concepts.filter(
            order__gt=attempt.quiz.concept.order, is_active=True
        ).order_by("order").first()

    context = get_user_data_context(request)
    context.update({
        "attempt": attempt,
        "topic_progress": tp,
        "next_concept": next_concept,
    })
    return render(request, "quiz_result.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS / REWARDS / LEADERBOARD / ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def progress_page(request):
    profile = _get_profile(request)
    student_class = _get_student_class(profile)

    topic_progresses = (
        StudentTopicProgress.objects
        .filter(student=profile)
        .select_related("concept__chapter__class_subject__subject")
        .order_by("-updated_at")
    )

    class_subjects = (
        ClassSubject.objects
        .filter(student_class=student_class)
        .select_related("subject")
    )
    subject_progress = []
    for cs in class_subjects:
        total = Concept.objects.filter(chapter__class_subject=cs, is_active=True).count()
        done = StudentTopicProgress.objects.filter(
            student=profile, concept__chapter__class_subject=cs, is_mastered=True
        ).count()
        subject_progress.append({
            "cs": cs,
            "total": total,
            "done": done,
            "pct": round((done / total * 100) if total else 0),
        })

    lesson_progress = (
        LessonProgress.objects
        .filter(student=profile)
        .select_related("lesson__concept")
        .order_by("-completed_at")[:10]
    )

    quiz_attempts = (
        QuizAttempt.objects
        .filter(student=profile)
        .select_related("quiz__concept")
        .order_by("-started_at")[:10]
    )

    context = get_user_data_context(request)
    context.update({
        "topic_progresses": topic_progresses,
        "subject_progress": subject_progress,
        "lesson_progress": lesson_progress,
        "quiz_attempts": quiz_attempts,
        "student_class": student_class,
    })
    return render(request, "progress.html", context)


@login_required
def rewards_page(request):
    profile = _get_profile(request)
    badges = Badge.objects.all()
    earned_badge_ids = set(
        StudentBadge.objects.filter(student=profile).values_list("badge_id", flat=True)
    )
    for badge in badges:
        badge.is_earned = badge.id in earned_badge_ids

    xp_history = XPTransaction.objects.filter(student=profile).order_by("-created_at")[:10]
    coin_history = CoinTransaction.objects.filter(student=profile).order_by("-created_at")[:10]

    context = get_user_data_context(request)
    context.update({
        "badges": badges,
        "xp_history": xp_history,
        "coin_history": coin_history,
    })
    return render(request, "rewards.html", context)


@login_required
def leaderboard_page(request):
    profile = _get_profile(request)
    student_class = _get_student_class(profile)

    classmates = (
        StudentProfile.objects
        .filter(student_class=student_class)
        .select_related("user")
        .order_by("-xp")
    )
    for idx, cm in enumerate(classmates, 1):
        cm.rank = idx

    my_rank = next((cm.rank for cm in classmates if cm.id == profile.id), 1)

    context = get_user_data_context(request)
    context.update({
        "leaderboard": classmates,
        "my_rank": my_rank,
        "student_class": student_class,
    })
    return render(request, "leaderboard.html", context)


@login_required
def achievements_page(request):
    profile = _get_profile(request)
    all_achievements = Achievement.objects.filter(is_active=True)
    earned_ids = set(
        StudentAchievement.objects.filter(student=profile).values_list("achievement_id", flat=True)
    )
    for ach in all_achievements:
        ach.is_earned = ach.id in earned_ids

    context = get_user_data_context(request)
    context.update({
        "achievements": all_achievements,
        "earned_count": len(earned_ids),
        "total_count": all_achievements.count(),
    })
    return render(request, "achievements.html", context)


@login_required
def profile_page(request):
    profile = _get_profile(request)
    earned_badges = StudentBadge.objects.filter(student=profile).select_related("badge")
    earned_achievements = StudentAchievement.objects.filter(student=profile).select_related("achievement")

    context = get_user_data_context(request)
    context.update({
        "earned_badges": earned_badges,
        "earned_achievements": earned_achievements,
    })
    return render(request, "profile.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# SECURE API ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@login_required
@require_POST
def api_complete_lesson(request):
    """
    Step 1: Completes the Learn phase for a topic and unlocks the Game phase.
    """
    try:
        data = json.loads(request.body)
        concept_id = int(data.get("concept_id"))
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid concept_id."}, status=400)

    profile = _get_profile(request)
    concept = get_object_or_404(Concept, id=concept_id)

    if not _class_owns_concept(profile, concept):
        return JsonResponse({"success": False, "message": "Unauthorized."}, status=403)

    tp = get_or_create_topic_progress(profile, concept)
    if not tp.learn_completed:
        tp.mark_learn_complete(xp=15)
        award_xp(profile, 15, f"Learn Completed: {concept.name}")
        update_streak(profile)

    return JsonResponse({
        "success": True,
        "game_unlocked": True,
        "message": f"Great job! You mastered the lesson on {concept.name}. The Game is now unlocked!",
        "new_xp": profile.xp
    })


@login_required
@require_POST
def api_submit_game(request):
    """
    Step 2: Submits the Game result, evaluates accuracy, awards XP/coins, and unlocks the Quiz.
    """
    try:
        data = json.loads(request.body)
        game_id = int(data.get("game_id"))
        difficulty = data.get("difficulty", "easy")
        score = int(data.get("score", 100))
        accuracy = float(data.get("accuracy", 100.0))
        time_spent = int(data.get("time_spent", 0))
        hints_used = int(data.get("hints_used", 0))
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid game data."}, status=400)

    profile = _get_profile(request)
    game = get_object_or_404(Game, id=game_id)

    if not _class_owns_game(profile, game):
        return JsonResponse({"success": False, "message": "Unauthorized."}, status=403)

    level = GameLevel.objects.filter(game=game, difficulty=difficulty).first()
    xp_reward = level.xp_reward if level else 20
    coin_reward = level.coin_reward if level else 10

    # Record Session
    session = GameSession.objects.create(
        student=profile,
        game=game,
        difficulty=difficulty,
        status="COMPLETED",
        score=score,
        accuracy=accuracy,
        time_spent=time_spent,
        hints_used=hints_used,
        xp_earned=xp_reward,
        coins_earned=coin_reward,
        completed_at=timezone.now(),
    )

    # Update Topic Sequence
    tp = get_or_create_topic_progress(profile, game.concept)
    tp.mark_game_complete(score=score, accuracy=accuracy, xp=xp_reward, coins=coin_reward, hints=hints_used)

    award_xp(profile, xp_reward, f"Game completed: {game.title}")
    award_coins(profile, coin_reward, f"Game completed: {game.title}")
    update_streak(profile)

    return JsonResponse({
        "success": True,
        "session_id": session.id,
        "quiz_unlocked": True,
        "message": f"Awesome! Game '{game.title}' completed. Quiz is now unlocked!",
        "xp_earned": xp_reward,
        "coins_earned": coin_reward,
        "new_xp": profile.xp,
        "new_coins": profile.coins,
    })


@login_required
@require_POST
def api_submit_quiz(request):
    """
    Step 3: Submits the Quiz, checks passing criteria, awards XP/coins,
    marks Topic as Mastered, and unlocks the next Topic!
    """
    try:
        data = json.loads(request.body)
        quiz_id = int(data.get("quiz_id"))
        answers = data.get("answers", {})   # {question_id: option_id}
        time_taken = int(data.get("time_taken", 0))
        hints_used = int(data.get("hints_used", 0))
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid quiz data."}, status=400)

    profile = _get_profile(request)
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)

    if not _class_owns_quiz(profile, quiz):
        return JsonResponse({"success": False, "message": "Unauthorized."}, status=403)

    questions = quiz.questions.prefetch_related("options").all()
    total_marks = sum(q.marks for q in questions)
    score = 0

    for q in questions:
        chosen_id = answers.get(str(q.id))
        if chosen_id:
            correct_opt = q.options.filter(is_correct=True).first()
            if correct_opt and correct_opt.id == int(chosen_id):
                score += q.marks

    percentage = round((score / total_marks * 100) if total_marks else 0, 2)
    passed = percentage >= quiz.passing_percentage
    xp_earned = round(quiz.xp_reward * (percentage / 100)) if passed else round(quiz.xp_reward * 0.3)
    coins_earned = 15 if passed else 5

    attempt = QuizAttempt.objects.create(
        student=profile,
        quiz=quiz,
        score=score,
        total_marks=total_marks,
        percentage=percentage,
        time_taken=time_taken,
        passed=passed,
        xp_earned=xp_earned,
        completed_at=timezone.now(),
    )

    tp = get_or_create_topic_progress(profile, quiz.concept)
    tp.mark_quiz_complete(
        score=score,
        total_marks=total_marks,
        percentage=percentage,
        xp=xp_earned,
        coins=coins_earned,
        hints=hints_used
    )

    if xp_earned:
        award_xp(profile, xp_earned, f"Quiz passed: {quiz.title}")
    if coins_earned:
        award_coins(profile, coins_earned, f"Quiz passed: {quiz.title}")
    update_streak(profile)

    return JsonResponse({
        "success": True,
        "attempt_id": attempt.id,
        "score": score,
        "total_marks": total_marks,
        "percentage": float(percentage),
        "passed": passed,
        "is_mastered": tp.is_mastered,
        "xp_earned": xp_earned,
        "coins_earned": coins_earned,
        "new_xp": profile.xp,
        "new_coins": profile.coins,
    })


@login_required
@require_POST
def api_explain_question(request):
    """
    AI Tutor explanation for both correct and wrong answers, suitable for Class 5 to Class 8.
    """
    try:
        data = json.loads(request.body)
        question_text = data.get("question_text", "")
        selected_text = data.get("selected_text", "")
        correct_text = data.get("correct_text", "")
        is_correct = data.get("is_correct", False)
    except Exception:
        return JsonResponse({"success": False, "message": "Invalid request payload."}, status=400)

    profile = _get_profile(request)
    grade = profile.student_class.grade_number

    if is_correct:
        explanation = f"🌟 Fantastic job! That is exactly right! In Class {grade} Mathematics, when you select '{selected_text}', it correctly satisfies the concept because '{correct_text}' represents the true proportion of the whole. Keep up this brilliant thinking!"
    else:
        explanation = f"💡 Let's learn this together! You selected '{selected_text}', but the correct answer is '{correct_text}'.\n\nRemember: In fractions, the bottom number (denominator) tells us how many equal pieces make up the entire whole. The top number (numerator) tells us how many pieces we have chosen. Therefore, {correct_text} is the right choice."

    return JsonResponse({
        "success": True,
        "explanation": explanation
    })
