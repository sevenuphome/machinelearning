import time
import random
from dataclasses import dataclass, field
from datetime import datetime


# Time-of-day periods
TIME_PERIODS = {
    "dawn":      (5, 7),    # ตื่นเช้า ยังงัวเงีย
    "morning":   (7, 12),   # ตื่นตัว อยากรู้อยากเห็น
    "afternoon": (12, 16),  # หลังกินข้าวเที่ยง ง่วง
    "evening":   (16, 21),  # ช่วงเย็น ขี้เล่นที่สุด
    "night":     (21, 24),  # เริ่มพักผ่อน
    "late_night": (0, 5),   # หลับลึก
}

TIME_PERIOD_TH = {
    "dawn": "รุ่งเช้า",
    "morning": "เช้า",
    "afternoon": "บ่าย",
    "evening": "เย็น",
    "night": "กลางคืน",
    "late_night": "ดึก",
}


def get_time_period(hour: int | None = None) -> str:
    if hour is None:
        hour = datetime.now().hour
    for period, (start, end) in TIME_PERIODS.items():
        if start <= hour < end:
            return period
    return "late_night"


@dataclass
class CatState:
    """The cat's internal state — hunger, energy, mood, curiosity, bond level."""

    # Core needs (0.0 = empty/none, 1.0 = full/max)
    hunger: float = 0.3       # 0 = full, 1 = starving
    energy: float = 0.8       # 0 = exhausted, 1 = fully rested
    happiness: float = 0.5    # 0 = miserable, 1 = very happy
    curiosity: float = 0.5    # 0 = bored, 1 = very curious
    bond_level: float = 0.1   # 0 = stranger, 1 = best friend

    # Mood is derived from the combination of states
    # Possible moods: happy, playful, sleepy, hungry, annoyed, curious, content
    _last_update: float = field(default_factory=time.time, repr=False)

    # Base decay/growth rates per second
    HUNGER_RATE = 0.002
    ENERGY_DECAY = 0.001
    CURIOSITY_RATE = 0.0015
    HAPPINESS_DECAY = 0.0005
    BOND_DECAY = 0.0001

    @property
    def time_period(self) -> str:
        return get_time_period()

    @property
    def time_period_th(self) -> str:
        return TIME_PERIOD_TH.get(self.time_period, "")

    def clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _time_multipliers(self) -> dict[str, float]:
        """Adjust rates based on real time of day."""
        period = self.time_period
        if period == "morning":
            # เช้า: หิวเร็ว ตื่นตัว อยากรู้อยากเห็น
            return {"hunger": 1.5, "energy": 0.5, "curiosity": 1.8, "happiness": 0.8}
        elif period == "afternoon":
            # บ่าย: ง่วง พลังงานลดเร็ว หิวหลังกินข้าว
            return {"hunger": 1.0, "energy": 2.0, "curiosity": 0.5, "happiness": 0.8}
        elif period == "evening":
            # เย็น: ขี้เล่นมาก พลังงานดี อยากรู้อยากเห็น
            return {"hunger": 1.3, "energy": 0.7, "curiosity": 1.5, "happiness": 0.3}
        elif period == "night":
            # กลางคืน: เริ่มง่วง อยากพัก
            return {"hunger": 0.8, "energy": 1.8, "curiosity": 0.3, "happiness": 1.0}
        elif period == "late_night":
            # ดึก: หลับ พลังงานฟื้นตัว
            return {"hunger": 0.5, "energy": -1.5, "curiosity": 0.2, "happiness": 0.5}
        elif period == "dawn":
            # รุ่งเช้า: เริ่มตื่น ยังงัวเงีย
            return {"hunger": 1.2, "energy": -0.5, "curiosity": 1.0, "happiness": 0.7}
        return {"hunger": 1.0, "energy": 1.0, "curiosity": 1.0, "happiness": 1.0}

    def tick(self):
        """Update states based on elapsed time and real time of day."""
        now = time.time()
        elapsed = now - self._last_update
        self._last_update = now

        m = self._time_multipliers()

        self.hunger = self.clamp(self.hunger + self.HUNGER_RATE * elapsed * m["hunger"])

        # energy multiplier: positive = drains faster, negative = recovers
        if m["energy"] < 0:
            self.energy = self.clamp(self.energy + self.ENERGY_DECAY * elapsed * abs(m["energy"]))
        else:
            self.energy = self.clamp(self.energy - self.ENERGY_DECAY * elapsed * m["energy"])

        self.curiosity = self.clamp(self.curiosity + self.CURIOSITY_RATE * elapsed * m["curiosity"])
        self.happiness = self.clamp(self.happiness - self.HAPPINESS_DECAY * elapsed * m["happiness"])
        self.bond_level = self.clamp(self.bond_level - self.BOND_DECAY * elapsed)

        # Hunger and tiredness reduce happiness
        if self.hunger > 0.7:
            self.happiness = self.clamp(self.happiness - 0.001 * elapsed)
        if self.energy < 0.2:
            self.happiness = self.clamp(self.happiness - 0.001 * elapsed)

    def apply_action(self, action: str):
        """Apply the effects of a user action on cat state."""
        effects = {
            "feed": {"hunger": -0.4, "happiness": 0.1, "bond_level": 0.05},
            "pet": {"happiness": 0.2, "bond_level": 0.08, "energy": -0.02},
            "play": {"happiness": 0.3, "energy": -0.15, "curiosity": -0.2, "bond_level": 0.1},
            "talk": {"happiness": 0.05, "bond_level": 0.03, "curiosity": 0.05},
            "sleep": {"energy": 0.5, "hunger": 0.1},
            "explore": {"curiosity": -0.3, "energy": -0.1, "happiness": 0.1},
        }

        if action not in effects:
            return

        for attr, delta in effects[action].items():
            current = getattr(self, attr)
            # Add some randomness to make it feel alive
            noise = random.uniform(-0.03, 0.03)
            setattr(self, attr, self.clamp(current + delta + noise))

    @property
    def mood(self) -> str:
        """Derive the current mood from internal states."""
        if self.energy < 0.2:
            return "sleepy"
        if self.hunger > 0.7:
            return "hungry"
        if self.happiness < 0.2:
            return "annoyed"
        if self.curiosity > 0.7:
            return "curious"
        if self.happiness > 0.7 and self.energy > 0.5:
            return "playful"
        if self.happiness > 0.5:
            return "happy"
        return "content"

    @property
    def state_vector(self) -> list[float]:
        """Return state as a list for ML input."""
        return [self.hunger, self.energy, self.happiness, self.curiosity, self.bond_level]

    def summary(self) -> str:
        """Human-readable state summary."""
        bars = {
            "hunger": self.hunger,
            "energy": self.energy,
            "happiness": self.happiness,
            "curiosity": self.curiosity,
            "bond": self.bond_level,
        }
        lines = [f"  Mood: {self.mood}"]
        for name, val in bars.items():
            filled = int(val * 10)
            bar = "█" * filled + "░" * (10 - filled)
            lines.append(f"  {name:10s} [{bar}] {val:.0%}")
        return "\n".join(lines)
