import time
from dataclasses import dataclass, field


@dataclass
class Interaction:
    action: str
    timestamp: float
    cat_mood: str
    was_positive: bool  # Did the cat enjoy it?


class CatMemory:
    """Tracks interaction history and calculates relationship quality."""

    def __init__(self, max_history: int = 100):
        self.history: list[Interaction] = []
        self.max_history = max_history
        self.total_interactions = 0
        self.last_interaction_time: float | None = None

    def record(self, action: str, cat_mood: str, was_positive: bool):
        """Record an interaction."""
        now = time.time()
        self.history.append(Interaction(
            action=action,
            timestamp=now,
            cat_mood=cat_mood,
            was_positive=was_positive,
        ))
        self.total_interactions += 1
        self.last_interaction_time = now

        # Keep history bounded
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    @property
    def time_since_last_interaction(self) -> float | None:
        """Seconds since last interaction, or None if never interacted."""
        if self.last_interaction_time is None:
            return None
        return time.time() - self.last_interaction_time

    @property
    def recent_positive_ratio(self) -> float:
        """Ratio of positive interactions in last 20 interactions."""
        recent = self.history[-20:]
        if not recent:
            return 0.5
        return sum(1 for i in recent if i.was_positive) / len(recent)

    @property
    def favorite_action(self) -> str | None:
        """The action the owner does most often."""
        if not self.history:
            return None
        counts: dict[str, int] = {}
        for interaction in self.history[-30:]:
            counts[interaction.action] = counts.get(interaction.action, 0) + 1
        return max(counts, key=counts.get)

    @property
    def neglect_level(self) -> float:
        """How neglected the cat feels. 0 = well cared for, 1 = very neglected."""
        gap = self.time_since_last_interaction
        if gap is None:
            return 0.5  # Unknown owner
        # 5 minutes without interaction = max neglect (in game time)
        return min(1.0, gap / 300.0)

    def relationship_summary(self) -> str:
        lines = [
            f"  Total interactions: {self.total_interactions}",
            f"  Recent positivity: {self.recent_positive_ratio:.0%}",
        ]
        fav = self.favorite_action
        if fav:
            lines.append(f"  Favorite activity: {fav}")
        gap = self.time_since_last_interaction
        if gap is not None:
            if gap < 10:
                lines.append("  Last seen: just now")
            elif gap < 60:
                lines.append(f"  Last seen: {gap:.0f}s ago")
            else:
                lines.append(f"  Last seen: {gap / 60:.1f}min ago")
        return "\n".join(lines)
