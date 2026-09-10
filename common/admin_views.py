import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.conf import settings

from academics.models import Class, Subject, ClassSubject, Chapter, Concept, Quiz
from accounts.models import StudentProfile
from games.models import Game, GameLevel, GameSession, GameAttempt, GameTemplate
from rewards.models import Badge, StudentBadge, Achievement, DailyMission, XPTransaction, CoinTransaction
from common.models import AdminAuditLog, TopicUnlockRule
from common.admin_services import (
    log_admin_action,
    sanitize_and_extract_game_zip,
    get_admin_dashboard_metrics,
    get_game_analytics
)


def is_staff_or_admin(user):
    """Permission gate: Superusers, staff members, or users with admin permissions."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ══════════════════════════════════════════════════════════════════════════════
# 1. EXECUTIVE DASHBOARD & AUDIT LOGS
# ══════════════════════════════════════════════════════════════════════════════

@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_dashboard_view(request):
    """Main TezMindz Admin Panel Executive Dashboard."""
    metrics = get_admin_dashboard_metrics()
    context = {
        "title": "Executive Dashboard",
        "active_tab": "dashboard",
        **metrics,
    }
    return render(request, "admin/dashboard.html", context)


@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_audit_logs_view(request):
    """System activity trail & audit logs."""
    logs = AdminAuditLog.objects.select_related("admin_user").order_by("-created_at")[:100]
    return render(request, "admin/audit_logs.html", {
        "title": "Audit Logs",
        "active_tab": "audit_logs",
        "logs": logs,
    })


# ══════════════════════════════════════════════════════════════════════════════
# 2. ACADEMIC HIERARCHY MANAGEMENT (Class -> Subject -> Chapter -> Topic)
# ══════════════════════════════════════════════════════════════════════════════

@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_academic_hierarchy_view(request):
    """Interactive Curriculum Tree Viewer and Hierarchy Editor."""
    classes = Class.objects.prefetch_related(
        "class_subjects__subject",
        "class_subjects__chapters__concepts"
    ).order_by("grade_number")
    
    all_subjects = Subject.objects.all().order_by("title")

    context = {
        "title": "Academic Content Hierarchy",
        "active_tab": "academic",
        "classes": classes,
        "all_subjects": all_subjects,
    }
    return render(request, "admin/academic_hierarchy.html", context)


@user_passes_test(is_staff_or_admin, login_url="/login/")
def api_hierarchy_cascading(request):
    """
    Dynamic Cascading JSON API for dropdown chaining:
    - ?level=classes -> returns all classes
    - ?level=subjects&class_id=X -> returns subjects for class
    - ?level=chapters&class_subject_id=X or (class_id=X & subject_id=Y) -> returns chapters
    - ?level=topics&chapter_id=X -> returns topics
    """
    level = request.GET.get("level", "classes")

    if level == "classes":
        data = list(Class.objects.filter(is_active=True).order_by("grade_number").values("id", "grade_number", "class_label", "name"))
        return JsonResponse({"success": True, "data": data})

    elif level == "subjects":
        class_id = request.GET.get("class_id")
        if not class_id:
            return JsonResponse({"success": False, "message": "class_id required"}, status=400)
        
        class_subjects = ClassSubject.objects.filter(student_class_id=class_id, subject__is_active=True).select_related("subject")
        data = [
            {
                "class_subject_id": cs.id,
                "subject_id": cs.subject.id,
                "title": cs.subject.title,
                "icon_type": cs.subject.icon_type,
            }
            for cs in class_subjects
        ]
        return JsonResponse({"success": True, "data": data})

    elif level == "chapters":
        class_subject_id = request.GET.get("class_subject_id")
        class_id = request.GET.get("class_id")
        subject_id = request.GET.get("subject_id")

        if class_subject_id:
            chapters = Chapter.objects.filter(class_subject_id=class_subject_id, is_active=True).order_by("order")
        elif class_id and subject_id:
            chapters = Chapter.objects.filter(
                class_subject__student_class_id=class_id,
                class_subject__subject_id=subject_id,
                is_active=True
            ).order_by("order")
        else:
            return JsonResponse({"success": False, "message": "class_subject_id or (class_id & subject_id) required"}, status=400)

        data = list(chapters.values("id", "name", "order", "slug"))
        return JsonResponse({"success": True, "data": data})

    elif level == "topics":
        chapter_id = request.GET.get("chapter_id")
        if not chapter_id:
            return JsonResponse({"success": False, "message": "chapter_id required"}, status=400)

        topics = Concept.objects.filter(chapter_id=chapter_id, is_active=True).order_by("order")
        data = list(topics.values("id", "name", "order", "slug", "difficulty"))
        return JsonResponse({"success": True, "data": data})

    return JsonResponse({"success": False, "message": "Invalid level"}, status=400)


@user_passes_test(is_staff_or_admin, login_url="/login/")
@require_POST
def api_class_save(request):
    """Create or update a Class."""
    try:
        data = json.loads(request.body)
        class_id = data.get("id")
        grade = int(data.get("grade_number"))
        name = data.get("name", f"Grade {grade}")
        label = data.get("class_label", f"Class {grade}")
        stage = data.get("stage", "Primary")
        age_group = data.get("age_group", "Age 6-12")
        category = data.get("category", "primary")
        is_active = data.get("is_active", True)

        if class_id:
            cls = get_object_or_404(Class, id=class_id)
            cls.grade_number = grade
            cls.name = name
            cls.class_label = label
            cls.stage = stage
            cls.age_group = age_group
            cls.category = category
            cls.is_active = is_active
            cls.save()
            log_admin_action(request, "Updated Class", "Class", cls.id, f"Grade {grade}")
        else:
            cls = Class.objects.create(
                grade_number=grade, name=name, class_label=label,
                stage=stage, age_group=age_group, category=category, is_active=is_active
            )
            log_admin_action(request, "Created Class", "Class", cls.id, f"Grade {grade}")

        return JsonResponse({"success": True, "id": cls.id})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@user_passes_test(is_staff_or_admin, login_url="/login/")
@require_POST
def api_chapter_save(request):
    """Create or update a Chapter."""
    try:
        data = json.loads(request.body)
        chapter_id = data.get("id")
        class_subject_id = data.get("class_subject_id")
        name = data.get("name", "").strip()
        order = int(data.get("order", 1))
        description = data.get("description", "")

        cs = get_object_or_404(ClassSubject, id=class_subject_id)

        if chapter_id:
            ch = get_object_or_404(Chapter, id=chapter_id)
            ch.name = name
            ch.order = order
            ch.description = description
            ch.slug = slugify(name)
            ch.save()
            log_admin_action(request, "Updated Chapter", "Chapter", ch.id, name)
        else:
            ch = Chapter.objects.create(
                class_subject=cs, name=name, order=order,
                description=description, slug=slugify(name)
            )
            log_admin_action(request, "Created Chapter", "Chapter", ch.id, name)

        return JsonResponse({"success": True, "id": ch.id})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@user_passes_test(is_staff_or_admin, login_url="/login/")
@require_POST
def api_topic_save(request):
    """Create or update a Topic (Concept)."""
    try:
        data = json.loads(request.body)
        topic_id = data.get("id")
        chapter_id = data.get("chapter_id")
        name = data.get("name", "").strip()
        order = int(data.get("order", 1))
        description = data.get("description", "")
        difficulty = data.get("difficulty", "easy")

        chapter = get_object_or_404(Chapter, id=chapter_id)

        if topic_id:
            top = get_object_or_404(Concept, id=topic_id)
            top.name = name
            top.order = order
            top.description = description
            top.difficulty = difficulty
            top.slug = slugify(name)
            top.save()
            log_admin_action(request, "Updated Topic", "Concept", top.id, name)
        else:
            top = Concept.objects.create(
                chapter=chapter, name=name, order=order,
                description=description, difficulty=difficulty, slug=slugify(name)
            )
            log_admin_action(request, "Created Topic", "Concept", top.id, name)

        return JsonResponse({"success": True, "id": top.id})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# ══════════════════════════════════════════════════════════════════════════════
# 3. GAME MANAGEMENT SYSTEM & ZIP UPLOADER
# ══════════════════════════════════════════════════════════════════════════════

@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_game_library_view(request):
    """Interactive Game Library Table with search, filters, and quick toggles."""
    games = (
        Game.objects
        .select_related("concept__chapter__class_subject__student_class", "concept__chapter__class_subject__subject")
        .order_by("concept__chapter__class_subject__student_class__grade_number", "concept__chapter__order", "concept__order")
    )

    # Attach session metrics
    for g in games:
        g.play_count = g.sessions.count()

    context = {
        "title": "Educational Game Library",
        "active_tab": "games",
        "games": games,
        "classes": Class.objects.filter(is_active=True).order_by("grade_number"),
    }
    return render(request, "admin/game_library.html", context)


@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_game_form_view(request, game_id=None):
    """Add new game or edit existing game with dynamic cascading and ZIP uploader."""
    game = get_object_or_404(Game, id=game_id) if game_id else None
    classes = Class.objects.filter(is_active=True).order_by("grade_number")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug = request.POST.get("slug", "").strip() or slugify(title)
        topic_id = request.POST.get("topic_id")
        game_type = request.POST.get("game_type", "interactive_activity")
        difficulty = request.POST.get("difficulty", "easy")
        description = request.POST.get("description", "")
        xp_reward = int(request.POST.get("xp_reward", 50))
        coin_reward = int(request.POST.get("coin_reward", 15))
        is_active = request.POST.get("is_active") == "on"

        concept = get_object_or_404(Concept, id=topic_id)
        chapter = concept.chapter
        cs = chapter.class_subject
        student_class = cs.student_class

        # Determine standard hierarchical path
        subj_name = cs.subject.title.lower().replace(" ", "_")
        auto_game_path = f"class_{student_class.grade_number}/{subj_name}/chapter_{chapter.order:02d}_{chapter.slug or 'ch'}/topic_{concept.order:02d}_{concept.slug or 'top'}/{slug}"

        if game:
            game.title = title
            game.slug = slug
            game.concept = concept
            game.game_type = game_type
            game.difficulty = difficulty
            game.description = description
            game.xp_reward = xp_reward
            game.coin_reward = coin_reward
            game.is_active = is_active
            if not game.game_path:
                game.game_path = auto_game_path
            game.save()
            messages.success(request, f"Game '{game.title}' updated successfully!")
            log_admin_action(request, "Updated Game", "Game", game.id, title)
        else:
            game = Game.objects.create(
                title=title,
                slug=slug,
                concept=concept,
                game_type=game_type,
                difficulty=difficulty,
                description=description,
                xp_reward=xp_reward,
                coin_reward=coin_reward,
                is_active=is_active,
                game_path=auto_game_path,
            )
            messages.success(request, f"Game '{game.title}' created successfully!")
            log_admin_action(request, "Created Game", "Game", game.id, title)

        # Handle optional ZIP upload in same form
        if "game_zip" in request.FILES:
            zip_file = request.FILES["game_zip"]
            success, msg = sanitize_and_extract_game_zip(zip_file, game.game_path)
            if success:
                messages.success(request, f"Game source code extracted: {msg}")
                log_admin_action(request, "Uploaded Game ZIP", "Game", game.id, msg)
            else:
                messages.error(request, f"ZIP upload failed: {msg}")

        return redirect("tezadmin:game_library")

    context = {
        "title": f"Edit {game.title}" if game else "Add New Game",
        "active_tab": "games",
        "game": game,
        "classes": classes,
    }
    return render(request, "admin/game_form.html", context)


@user_passes_test(is_staff_or_admin, login_url="/login/")
@require_POST
def admin_game_toggle_status_view(request, game_id):
    """Toggle active status for a game."""
    game = get_object_or_404(Game, id=game_id)
    game.is_active = not game.is_active
    game.save()
    status_str = "Active" if game.is_active else "Draft/Inactive"
    log_admin_action(request, f"Toggled Game Status ({status_str})", "Game", game.id)
    return JsonResponse({"success": True, "is_active": game.is_active})


@user_passes_test(is_staff_or_admin, login_url="/login/")
@require_POST
def admin_game_duplicate_view(request, game_id):
    """One-click duplicate of a game."""
    orig = get_object_or_404(Game, id=game_id)
    new_slug = f"{orig.slug}-copy"
    counter = 1
    while Game.objects.filter(slug=new_slug).exists():
        new_slug = f"{orig.slug}-copy-{counter}"
        counter += 1

    clone = Game.objects.create(
        concept=orig.concept,
        template=orig.template,
        title=f"{orig.title} (Copy)",
        slug=new_slug,
        game_path=orig.game_path,
        game_type=orig.game_type,
        description=orig.description,
        difficulty=orig.difficulty,
        xp_reward=orig.xp_reward,
        coin_reward=orig.coin_reward,
        is_active=False
    )
    log_admin_action(request, "Duplicated Game", "Game", clone.id, f"From {orig.title}")
    messages.success(request, f"Duplicated game '{orig.title}' as '{clone.title}' (Draft)")
    return JsonResponse({"success": True, "new_id": clone.id})


@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_game_analytics_view(request, game_id):
    """Deep analytics view for an individual game."""
    analytics = get_game_analytics(game_id)
    if not analytics:
        messages.error(request, "Game not found.")
        return redirect("tezadmin:game_library")

    context = {
        "title": f"Analytics • {analytics['game'].title}",
        "active_tab": "games",
        **analytics,
    }
    return render(request, "admin/game_analytics.html", context)


# ══════════════════════════════════════════════════════════════════════════════
# 4. STUDENT, MEMBERSHIP & GAMIFICATION CONTROL
# ══════════════════════════════════════════════════════════════════════════════

@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_student_list_view(request):
    """Searchable directory of student profiles."""
    class_filter = request.GET.get("class")
    query = request.GET.get("q", "").strip()

    students = StudentProfile.objects.select_related("user", "student_class").order_by("-xp")

    if class_filter:
        students = students.filter(student_class__grade_number=class_filter)
    if query:
        students = students.filter(user__username__icontains=query) | students.filter(user__first_name__icontains=query) | students.filter(user__email__icontains=query)

    context = {
        "title": "Student Management",
        "active_tab": "students",
        "students": students[:100],
        "total_count": students.count(),
        "classes": Class.objects.filter(is_active=True).order_by("grade_number"),
        "selected_class": class_filter,
        "query": query,
    }
    return render(request, "admin/student_list.html", context)


@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_student_detail_view(request, student_id):
    """Comprehensive student profile inspector."""
    profile = get_object_or_404(StudentProfile.objects.select_related("user", "student_class"), id=student_id)
    sessions = GameSession.objects.filter(student=profile).select_related("game").order_by("-started_at")[:10]
    badges = StudentBadge.objects.filter(student=profile).select_related("badge")
    xp_txs = XPTransaction.objects.filter(student=profile).order_by("-created_at")[:10]

    context = {
        "title": f"Student Profile • {profile.user.username}",
        "active_tab": "students",
        "student": profile,
        "sessions": sessions,
        "badges": badges,
        "xp_txs": xp_txs,
    }
    return render(request, "admin/student_detail.html", context)


@user_passes_test(is_staff_or_admin, login_url="/login/")
@require_POST
def admin_student_toggle_active_view(request, student_id):
    """Toggle user active / banned status."""
    profile = get_object_or_404(StudentProfile, id=student_id)
    user = profile.user
    user.is_active = not user.is_active
    user.save()
    log_admin_action(request, f"Toggled Student Active Status ({user.is_active})", "User", user.id)
    return JsonResponse({"success": True, "is_active": user.is_active})


@user_passes_test(is_staff_or_admin, login_url="/login/")
def admin_gamification_view(request):
    """XP/Coins rules, Level thresholds, Rewards store, and Achievements control."""
    achievements = Achievement.objects.all().order_by("id")
    badges = Badge.objects.all().order_by("name")
    missions = DailyMission.objects.all().order_by("-created_at")

    context = {
        "title": "Gamification & Economy Engine",
        "active_tab": "gamification",
        "achievements": achievements,
        "badges": badges,
        "missions": missions,
    }
    return render(request, "admin/gamification.html", context)
