from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from progress.models import StudentTopicProgress
from games.models import GameLevel


class Command(BaseCommand):
    help = "Fixes user roles, ensures demo student account has no admin permissions, and unlocks all learning content."

    def handle(self, *args, **options):
        # 1. Strip admin/staff permissions from demo student account 'student' (Tez)
        student_user = User.objects.filter(username="student").first()
        if student_user:
            student_user.is_staff = False
            student_user.is_superuser = False
            student_user.save()
            self.stdout.write(self.style.SUCCESS(f"Fixed 'student' (Tez): is_staff=False, is_superuser=False"))

        # 2. Ensure all other non-admin accounts do not have staff/superuser
        admin_usernames = {"admin", "sauravpund", "saurav", "pundsaurav", "saiurav"}
        for u in User.objects.exclude(username__in=admin_usernames):
            if u.is_staff or u.is_superuser:
                u.is_staff = False
                u.is_superuser = False
                u.save()
                self.stdout.write(self.style.WARNING(f"Stripped admin rights from: {u.username}"))

        # 3. Ensure primary admin accounts are staff & superuser
        for username in admin_usernames:
            u = User.objects.filter(username=username).first()
            if u:
                u.is_staff = True
                u.is_superuser = True
                u.save()
                self.stdout.write(self.style.SUCCESS(f"Verified administrator: {u.username}"))

        # 4. Unlock all topics and games
        StudentTopicProgress.objects.all().update(
            is_unlocked=True,
            game_unlocked=True,
            quiz_unlocked=True
        )
        GameLevel.objects.all().update(is_locked=False)

        self.stdout.write(self.style.SUCCESS("All authentication permissions and content locks synchronized successfully!"))
