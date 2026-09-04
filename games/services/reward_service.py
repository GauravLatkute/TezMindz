"""
Reward Service for Tezz-Mindz Game Engine.
Calculates and awards XP, Coins, and Achievements securely on backend.
"""
from rewards.models import XPTransaction, CoinTransaction, Achievement, StudentAchievement
from common.views import award_xp, award_coins, check_achievements


def calculate_and_award_rewards(student_profile, game, session, is_completed: bool, accuracy: float) -> dict:
    """
    Awards game rewards upon completion:
      - Game completion base reward (+50 XP, +15 Coins)
      - Perfect score bonus (+25 XP, +5 Coins if 100% accuracy)
    """
    xp_to_award = game.xp_reward or 50
    coins_to_award = game.coin_reward or 15

    # Perfect accuracy bonus
    if accuracy >= 100.0:
        xp_to_award += 25
        coins_to_award += 5

    if is_completed:
        award_xp(student_profile, xp_to_award, f"Completed game: {game.title}")
        award_coins(student_profile, coins_to_award, f"Completed game: {game.title}")

        session.xp_earned = xp_to_award
        session.coins_earned = coins_to_award
        session.save(update_fields=["xp_earned", "coins_earned"])

    return {
        "xp_awarded": xp_to_award if is_completed else 0,
        "coins_awarded": coins_to_award if is_completed else 0,
        "total_xp": student_profile.xp,
        "total_coins": student_profile.coins,
        "current_level": student_profile.current_level
    }
