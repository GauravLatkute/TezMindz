from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from progress.models import ConceptMastery
from progress.serializers import ConceptMasterySerializer
from games.models import GameSession, Game, Question
from academics.models import ClassSubject, Chapter, Concept
from rewards.models import DailyMission, StudentMission, Badge, StudentBadge
from accounts.models import StudentProfile

class ProgressOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        
        # Calculate session parameters
        completed_sessions = GameSession.objects.filter(student=profile, status="COMPLETED")
        total_games_completed = completed_sessions.count()
        
        avg_accuracy = completed_sessions.aggregate(Avg("accuracy"))["accuracy__avg"] or 0.0
        total_score = completed_sessions.aggregate(Sum("score"))["score__sum"] or 0
        
        # Calculate concept mastery metrics
        masteries = ConceptMastery.objects.filter(student=profile)
        avg_mastery = masteries.aggregate(Avg("mastery_score"))["mastery_score__avg"] or 0.0

        return Response({
            "success": True,
            "message": "Progress overview retrieved successfully",
            "data": {
                "total_games_completed": total_games_completed,
                "overall_accuracy": float(avg_accuracy),
                "overall_mastery": float(avg_mastery),
                "xp": profile.xp,
                "coins": profile.coins,
                "streak": profile.streak,
                "current_level": profile.current_level
            }
        })


class SubjectProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        class_subjects = ClassSubject.objects.filter(student_class=profile.student_class)
        
        data = []
        for cs in class_subjects:
            # Get concepts linked to this subject
            concepts = Concept.objects.filter(chapter__class_subject=cs)
            total_concepts = concepts.count()
            
            # Fetch mastered concepts count
            mastered_concepts = ConceptMastery.objects.filter(
                student=profile,
                concept__in=concepts,
                mastery_score__gte=70.0
            ).count()
            
            # Fetch average accuracy for this subject's games
            games_sessions = GameSession.objects.filter(
                student=profile,
                game__concept__in=concepts,
                status="COMPLETED"
            )
            accuracy = games_sessions.aggregate(Avg("accuracy"))["accuracy__avg"] or 0.0

            data.append({
                "subject_id": cs.subject.id,
                "subject_title": cs.subject.title,
                "total_concepts": total_concepts,
                "mastered_concepts": mastered_concepts,
                "accuracy": float(accuracy),
                "completion_percentage": float((mastered_concepts / total_concepts) * 100) if total_concepts > 0 else 0.0
            })

        return Response({
            "success": True,
            "message": "Subject progress retrieved successfully",
            "data": data
        })


class ChapterProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        subject_id = request.query_params.get("subject_id")
        
        if not subject_id:
            chapters = Chapter.objects.filter(class_subject__student_class=profile.student_class)
        else:
            chapters = Chapter.objects.filter(
                class_subject__student_class=profile.student_class,
                class_subject__subject_id=subject_id
            )

        data = []
        for chapter in chapters:
            concepts = Concept.objects.filter(chapter=chapter)
            total_concepts = concepts.count()
            
            mastered_concepts = ConceptMastery.objects.filter(
                student=profile,
                concept__in=concepts,
                mastery_score__gte=70.0
            ).count()
            
            data.append({
                "chapter_id": chapter.id,
                "chapter_name": chapter.name,
                "order": chapter.order,
                "total_concepts": total_concepts,
                "mastered_concepts": mastered_concepts,
                "completion_percentage": float((mastered_concepts / total_concepts) * 100) if total_concepts > 0 else 0.0
            })

        return Response({
            "success": True,
            "message": "Chapter progress retrieved successfully",
            "data": data
        })


class ConceptProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        chapter_id = request.query_params.get("chapter_id")
        
        if not chapter_id:
            concepts = Concept.objects.filter(chapter__class_subject__student_class=profile.student_class)
        else:
            concepts = Concept.objects.filter(chapter_id=chapter_id)

        data = []
        for concept in concepts:
            try:
                mastery = ConceptMastery.objects.get(student=profile, concept=concept)
                mastery_score = float(mastery.mastery_score)
                accuracy = float(mastery.accuracy)
                attempts = mastery.attempts_count
            except ConceptMastery.DoesNotExist:
                mastery_score = 0.0
                accuracy = 0.0
                attempts = 0

            data.append({
                "concept_id": concept.id,
                "concept_name": concept.name,
                "order": concept.order,
                "mastery_score": mastery_score,
                "accuracy": accuracy,
                "attempts_count": attempts
            })

        return Response({
            "success": True,
            "message": "Concept progress retrieved successfully",
            "data": data
        })


class ConceptMasteryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        masteries = ConceptMastery.objects.filter(student=request.user.profile).order_by("-mastery_score")
        serializer = ConceptMasterySerializer(masteries, many=True)
        return Response({
            "success": True,
            "message": "Concept masteries retrieved successfully",
            "data": serializer.data
        })


class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        import datetime
        today = datetime.date.today()

        # 1. Student Information
        student_data = {
            "name": profile.user.first_name or profile.user.username,
            "class": profile.student_class.grade_number,
            "class_label": profile.student_class.class_label,
            "stage": profile.student_class.stage,
            "avatar": profile.avatar or "🌟"
        }

        # 2. Player Status Metrics
        level = profile.current_level or 1
        xp = profile.xp or 0
        xp_required = (level + 1) * 150
        coins = profile.coins or 0
        streak = profile.streak or 0

        completed_sessions = GameSession.objects.filter(student=profile, status="COMPLETED")
        accuracy = int(completed_sessions.aggregate(Avg("accuracy"))["accuracy__avg"] or 0)

        stats_data = {
            "level": level,
            "xp": xp,
            "xp_required": xp_required,
            "coins": coins,
            "streak": streak,
            "accuracy": accuracy
        }

        # 3. Continue Learning
        last_session = GameSession.objects.filter(student=profile).order_by("-started_at").first()
        concept = None
        if last_session:
            concept = last_session.game.concept
        else:
            concept = Concept.objects.filter(
                chapter__class_subject__student_class=profile.student_class
            ).order_by("chapter__order", "order").first()

        continue_learning_data = None
        if concept:
            mastery = ConceptMastery.objects.filter(student=profile, concept=concept).first()
            continue_learning_data = {
                "subject_title": concept.chapter.class_subject.subject.title,
                "chapter_name": concept.chapter.name,
                "concept_name": concept.name,
                "concept_id": concept.id,
                "progress": int(mastery.mastery_score) if mastery else 0
            }

        # 4. Subject Progress Card Grid
        subjects_data = []
        class_subjects = ClassSubject.objects.filter(student_class=profile.student_class)
        for cs in class_subjects:
            total_concepts = Concept.objects.filter(chapter__class_subject=cs).count()
            completed_concepts = ConceptMastery.objects.filter(
                student=profile, concept__chapter__class_subject=cs, mastery_score__gte=70.0
            ).count()
            
            prog_percent = int((completed_concepts / total_concepts) * 100) if total_concepts > 0 else 0
            
            first_chap = Chapter.objects.filter(class_subject=cs).order_by("order").first()
            current_chap_name = first_chap.name if first_chap else "Basics"

            subjects_data.append({
                "subject_id": cs.subject.id,
                "title": cs.subject.title,
                "icon_type": cs.subject.icon_type,
                "color_theme": cs.subject.color_theme,
                "concepts_completed": completed_concepts,
                "total_concepts": total_concepts,
                "progress_percentage": prog_percent,
                "current_chapter": current_chap_name
            })

        # 5. Daily Missions Seeding & Retrieve
        # Check standard daily missions exist
        default_missions = [
            ("Play 1 Game", "Play and complete 1 game challenge.", "games_count", 1, 20, 10),
            ("Complete a Lesson", "Read 1 lesson study guide content.", "concepts_count", 1, 25, 12),
            ("Solve 5 Questions", "Answer 5 questions during levels.", "questions_solved", 5, 30, 15),
            ("Maintain your Streak", "Log in and learn today to maintain your daily streak.", "streak_days", 1, 15, 5),
        ]
        
        for title, desc, t_type, t_val, xp_rew, coin_rew in default_missions:
            DailyMission.objects.get_or_create(
                title=title,
                defaults={
                    "description": desc,
                    "target_type": t_type,
                    "target_value": t_val,
                    "xp_reward": xp_rew,
                    "coin_reward": coin_rew
                }
            )

        # Seed student active daily missions for today if empty
        active_student_missions = StudentMission.objects.filter(student=profile, assigned_date=today)
        if not active_student_missions.exists():
            all_dm = DailyMission.objects.all()[:4]
            for dm in all_dm:
                if not StudentMission.objects.filter(student=profile, mission=dm, assigned_date=today).exists():
                    StudentMission.objects.create(
                        student=profile,
                        mission=dm,
                        progress=0,
                        is_completed=False
                    )
            active_student_missions = StudentMission.objects.filter(student=profile, assigned_date=today)

        missions_data = []
        for sm in active_student_missions:
            status_str = "AVAILABLE"
            if sm.is_completed:
                status_str = "COMPLETED"
            elif sm.progress > 0:
                status_str = "IN_PROGRESS"

            missions_data.append({
                "id": sm.id,
                "title": sm.mission.title,
                "description": sm.mission.description,
                "progress": sm.progress,
                "target_value": sm.mission.target_value,
                "xp_reward": sm.mission.xp_reward,
                "coin_reward": sm.mission.coin_reward,
                "status": status_str
            })

        # 6. Dynamic Recommendation Engine
        recommendations_data = []
        
        # Misconception check
        weak_mastery = ConceptMastery.objects.filter(student=profile, mastery_score__lt=70.0).order_by("mastery_score").first()
        if weak_mastery:
            recommendations_data.append({
                "title": f"Practice {weak_mastery.concept.name}",
                "reason": "You had difficulty with this concept.",
                "concept_id": weak_mastery.concept.id,
                "subject_title": weak_mastery.concept.chapter.class_subject.subject.title
            })
        else:
            # Recommend next concept in line
            next_concept = Concept.objects.filter(chapter__class_subject__student_class=profile.student_class).exclude(
                id__in=ConceptMastery.objects.filter(student=profile, mastery_score__gte=70.0).values_list("concept_id", flat=True)
            ).order_by("chapter__order", "order").first()
            if next_concept:
                recommendations_data.append({
                    "title": f"Explore {next_concept.name}",
                    "reason": "Ready for your next learning adventure!",
                    "concept_id": next_concept.id,
                    "subject_title": next_concept.chapter.class_subject.subject.title
                })

        # Science encouragement
        sci_mastery_count = ConceptMastery.objects.filter(
            student=profile, concept__chapter__class_subject__subject__title="Science", mastery_score__gte=70.0
        ).count()
        if sci_mastery_count > 0:
            recommendations_data.append({
                "title": "Try Science Challenge",
                "reason": "You're doing great in Science!",
                "subject_title": "Science"
            })

        # Accuracy check
        if accuracy >= 90:
            recommendations_data.append({
                "title": "Ready for Hard Mode?",
                "reason": "Your accuracy is above 90%!",
                "subject_title": "Mathematics"
            })

        # 7. Badge unlocking states
        earned_badge_ids = list(StudentBadge.objects.filter(student=profile).values_list("badge_id", flat=True))
        all_badges = Badge.objects.all()
        badges_data = []
        for b in all_badges:
            badges_data.append({
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "is_unlocked": b.id in earned_badge_ids
            })

        # 8. Weekly Leaderboard rank gap check
        top_profiles = StudentProfile.objects.order_by("-xp")[:10]
        rank_list = []
        my_rank = 0
        for idx, p in enumerate(top_profiles):
            curr_rank = idx + 1
            if p == profile:
                my_rank = curr_rank
            rank_list.append({
                "rank": curr_rank,
                "display_name": p.user.first_name or p.user.username,
                "avatar": p.avatar or "🌟",
                "xp": p.xp,
                "is_me": p == profile
            })
            
        if my_rank == 0:
            my_rank = StudentProfile.objects.filter(xp__gt=profile.xp).count() + 1

        better_p = StudentProfile.objects.filter(xp__gt=profile.xp).order_by("xp").first()
        xp_required_to_next = (better_p.xp - profile.xp) if better_p else 40

        leaderboard_data = {
            "rankings": rank_list,
            "my_rank": my_rank,
            "xp_required_to_next": xp_required_to_next
        }

        # 9. Mon-Sun Streak checklist
        today_weekday = timezone.now().weekday()
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        streak_checklist = []
        for idx, day in enumerate(weekdays):
            status_str = "pending"
            if idx <= today_weekday and streak > 0:
                status_str = "completed"
            streak_checklist.append({"day": day, "status": status_str})

        streak_data = {
            "current_streak": streak,
            "checklist": streak_checklist
        }

        # Construct final unified payload
        return Response({
            "success": True,
            "message": "Student dashboard retrieved successfully",
            "data": {
                "student": student_data,
                "stats": stats_data,
                "continue_learning": continue_learning_data,
                "subjects": subjects_data,
                "daily_missions": missions_data,
                "recommendations": recommendations_data,
                "achievements": badges_data,
                "leaderboard": leaderboard_data,
                "streak": streak_data
            }
        })
