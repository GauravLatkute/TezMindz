import os
import zipfile
import json
from datetime import date, timedelta
from django.conf import settings
from django.db.models import Count, Avg, Sum, Q
from django.contrib.auth.models import User
from academics.models import Class, Subject, ClassSubject, Chapter, Concept, Quiz
from accounts.models import StudentProfile
from games.models import Game, GameSession, GameAttempt, GameProgress
from common.models import AdminAuditLog, TopicUnlockRule

# Allowed safe client-side web asset extensions
ALLOWED_EXTENSIONS = {
    '.html', '.htm', '.css', '.js',
    '.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp', '.ico',
    '.mp3', '.wav', '.ogg', '.m4a',
    '.json', '.md', '.txt',
    '.woff', '.woff2', '.ttf', '.eot'
}

DISALLOWED_EXTENSIONS = {
    '.py', '.pyc', '.pyd', '.pyw',
    '.exe', '.bat', '.cmd', '.sh', '.bash', '.ps1',
    '.php', '.asp', '.aspx', '.jsp', '.cgi', '.pl',
    '.dll', '.so', '.dylib', '.jar', '.vbs', '.scr'
}

MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50 MB limit


def log_admin_action(request, action, target_model, target_id="", details=""):
    """Records an administrative operation in the audit trail."""
    try:
        ip = None
        if request:
            x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded:
                ip = x_forwarded.split(",")[0].strip()
            else:
                ip = request.META.get("REMOTE_ADDR")

        admin_user = request.user if request and request.user.is_authenticated else None
        AdminAuditLog.objects.create(
            admin_user=admin_user,
            action=action,
            target_model=target_model,
            target_id=str(target_id),
            details=str(details),
            ip_address=ip
        )
    except Exception as e:
        print(f"[AdminAuditLog Error] {e}")


def sanitize_and_extract_game_zip(uploaded_zip, target_relative_path):
    """
    Securely inspects, validates, and extracts game source code into games/<target_relative_path>/.
    Rejects any executable or server-side scripts, protecting server integrity.
    """
    if uploaded_zip.size > MAX_ZIP_SIZE:
        return False, "File size exceeds the 50 MB limit."

    target_dir = (settings.BASE_DIR / "games" / target_relative_path).resolve()

    try:
        with zipfile.ZipFile(uploaded_zip, 'r') as z:
            namelist = z.namelist()
            if not namelist:
                return False, "The uploaded ZIP archive is empty."

            # 1. First Pass: Security Scan
            for member in namelist:
                # Check for zip slip
                member_path = (target_dir / member).resolve()
                if not str(member_path).startswith(str(target_dir)):
                    return False, f"Malicious path detected in archive: {member}"

                # Skip directories
                if member.endswith('/'):
                    continue

                _, ext = os.path.splitext(member.lower())
                if ext in DISALLOWED_EXTENSIONS:
                    return False, f"Security Violation: '{ext}' files are strictly forbidden for security reasons."

                if ext not in ALLOWED_EXTENSIONS and ext != '':
                    return False, f"Unsupported file type: '{ext}' in {member}."

            # 2. Second Pass: Extract Clean Files
            target_dir.mkdir(parents=True, exist_ok=True)
            for member in namelist:
                # Directory or file extraction
                if member.endswith('/'):
                    (target_dir / member).mkdir(parents=True, exist_ok=True)
                    continue

                # Strip leading top-level folder if archive was wrapped in a root folder
                out_path = target_dir / member
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member) as source, open(out_path, 'wb') as dest:
                    dest.write(source.read())

            # Verify index.html exists
            index_file = target_dir / "index.html"
            if not index_file.exists():
                # Check subdirectories for index.html and hoist if necessary
                for sub in target_dir.glob("**/index.html"):
                    index_file = sub
                    break

            return True, f"Extracted {len(namelist)} files successfully into {target_relative_path}."

    except zipfile.BadZipFile:
        return False, "Invalid ZIP archive format."
    except Exception as e:
        return False, f"Extraction failed: {str(e)}"


def get_admin_dashboard_metrics():
    """Calculates live KPI metrics and chart datasets for the executive dashboard."""
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    total_students = StudentProfile.objects.count()
    active_students = StudentProfile.objects.filter(last_activity_date__gte=today - timedelta(days=30)).count()
    total_games = Game.objects.count()
    active_games = Game.objects.filter(is_active=True).count()
    total_classes = Class.objects.filter(is_active=True).count()
    total_subjects = Subject.objects.filter(is_active=True).count()
    total_chapters = Chapter.objects.filter(is_active=True).count()
    total_topics = Concept.objects.filter(is_active=True).count()

    # Plays count
    total_game_sessions = GameSession.objects.count()
    today_game_sessions = GameSession.objects.filter(started_at__date=today).count()

    # 7-day registration and play trends
    registration_labels = [d.strftime("%b %d") for d in last_7_days]
    registration_data = []
    play_data = []

    for d in last_7_days:
        reg_count = User.objects.filter(date_joined__date=d).count()
        p_count = GameSession.objects.filter(started_at__date=d).count()
        registration_data.append(reg_count)
        play_data.append(p_count)

    # Popular games
    popular_games = (
        Game.objects.annotate(plays=Count("sessions"))
        .select_related("concept__chapter__class_subject__student_class", "concept__chapter__class_subject__subject")
        .order_by("-plays")[:5]
    )

    # Subject performance
    subjects = Subject.objects.filter(is_active=True)
    subject_names = [s.title for s in subjects]
    subject_topics_count = [
        Concept.objects.filter(chapter__class_subject__subject=s).count()
        for s in subjects
    ]

    recent_logs = AdminAuditLog.objects.select_related("admin_user")[:8]
    recent_attempts = GameAttempt.objects.select_related("session__student__user", "session__game").order_by("-created_at")[:6]

    return {
        "total_students": total_students,
        "active_students": active_students,
        "total_games": total_games,
        "active_games": active_games,
        "total_classes": total_classes,
        "total_subjects": total_subjects,
        "total_chapters": total_chapters,
        "total_topics": total_topics,
        "total_game_sessions": total_game_sessions,
        "today_game_sessions": today_game_sessions,
        "registration_labels": json.dumps(registration_labels),
        "registration_data": json.dumps(registration_data),
        "play_data": json.dumps(play_data),
        "subject_names": json.dumps(subject_names),
        "subject_topics_count": json.dumps(subject_topics_count),
        "popular_games": popular_games,
        "recent_logs": recent_logs,
        "recent_attempts": recent_attempts,
    }


def get_game_analytics(game_id):
    """Deep analytical telemetry for a single educational game."""
    game = Game.objects.select_related(
        "concept__chapter__class_subject__student_class",
        "concept__chapter__class_subject__subject"
    ).filter(id=game_id).first()
    if not game:
        return None

    sessions = GameSession.objects.filter(game=game)
    total_plays = sessions.count()
    unique_students = sessions.values("student").distinct().count()
    completed_sessions = sessions.filter(status="COMPLETED").count()
    completion_rate = round((completed_sessions / total_plays * 100) if total_plays else 0, 1)

    avg_score = sessions.aggregate(avg=Avg("score"))["avg"] or 0
    avg_score = round(avg_score, 1)

    # Attempts analytics
    attempts = GameAttempt.objects.filter(session__game=game)
    total_attempts = attempts.count()
    correct_attempts = attempts.filter(is_correct=True).count()
    accuracy = round((correct_attempts / total_attempts * 100) if total_attempts else 0, 1)
    avg_time = attempts.aggregate(avg=Avg("time_taken"))["avg"] or 0

    # Difficulty distribution
    easy_count = sessions.filter(difficulty="easy").count()
    med_count = sessions.filter(difficulty="medium").count()
    hard_count = sessions.filter(difficulty="hard").count()

    recent_sessions = sessions.select_related("student__user").order_by("-started_at")[:15]

    return {
        "game": game,
        "total_plays": total_plays,
        "unique_students": unique_students,
        "completion_rate": completion_rate,
        "avg_score": avg_score,
        "accuracy": accuracy,
        "avg_time_seconds": round(avg_time, 1),
        "difficulty_counts": {
            "easy": easy_count,
            "medium": med_count,
            "hard": hard_count,
        },
        "recent_sessions": recent_sessions,
    }
