from django.core.management.base import BaseCommand
from django.utils.text import slugify
from games.models import Game, GameLevel

class Command(BaseCommand):
    help = "Fix duplicate level numbers and empty slugs across all games"

    def handle(self, *args, **options):
        updated_games = 0
        updated_levels = 0
        for g in Game.objects.all():
            if not g.slug:
                g.slug = slugify(g.title)
                g.save()
                updated_games += 1
            
            lvls = list(g.levels.order_by('id'))
            level_nums = [l.level_number for l in lvls]
            if len(lvls) > 1 and len(set(level_nums)) < len(lvls):
                for idx, lvl in enumerate(lvls, 1):
                    lvl.level_number = idx
                    diff_label = lvl.difficulty.capitalize() if lvl.difficulty else f"Level {idx}"
                    lvl.title = f"Level {idx} ({diff_label})"
                    lvl.save()
                    updated_levels += 1

        self.stdout.write(self.style.SUCCESS(f"Cleanup complete! Updated {updated_games} games and {updated_levels} game levels."))
