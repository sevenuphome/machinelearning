import random
from src.cat_state import CatState
from src.memory import CatMemory


# All possible cat actions (what the cat decides to do)
CAT_ACTIONS = [
    "purr",        # Happy response
    "meow",        # Wants attention
    "hiss",        # Annoyed / leave me alone
    "nap",         # Goes to sleep
    "play_alone",  # Bats at imaginary things
    "explore",     # Wanders around curiously
    "eat",         # Goes to food bowl
    "ignore",      # Completely ignores the owner
    "rub",         # Rubs against owner (affection)
    "stare",       # Stares at owner (judging or curious)
]

# Text descriptions for each cat action
ACTION_TEXT = {
    "purr": [
        "แมวครางเบา ๆ อย่างมีความสุข... prrrr~",
        "แมวหลับตาแล้วครางเสียงดัง นี่มันพอใจมาก",
        "เสียงครางเบา ๆ ดังขึ้นจากลำคอ... แมวดูผ่อนคลาย",
    ],
    "meow": [
        "เมี้ยว~! แมวร้องเรียกความสนใจ",
        "แมวเดินมาเสียดสีขาพร้อมร้อง เมี้ยว!",
        "เมี้ยววว... แมวนั่งจ้องด้วยตาโต",
    ],
    "hiss": [
        "ฟืดดด! แมวขู่แล้วเดินหนีไป",
        "แมวหูแนบหัว ดวงตาเหลือบมอง... อย่ามายุ่ง",
        "แมวสะบัดหางแรง ๆ แล้วเดินจากไป",
    ],
    "nap": [
        "แมวม้วนตัวเป็นก้อนกลม ๆ แล้วหลับไป... zzz",
        "แมวหาวยาว แล้วหลับตาลง... นอนเลย",
        "แมวเดินไปนอนในที่อุ่น ๆ แล้วนอนหลับสนิท",
    ],
    "play_alone": [
        "แมวกระโดดไล่จับอะไรบางอย่างที่มองไม่เห็น!",
        "แมวตบลูกบอลไปมาอย่างสนุกสนาน",
        "แมวกระโดดตัวลอย! เล่นกับเงาตัวเอง",
    ],
    "explore": [
        "แมวเดินสำรวจรอบ ๆ อย่างระมัดระวัง...",
        "แมวดมนู่นดมนี่ หูตั้งชัน สนใจทุกอย่าง",
        "แมวกระโดดขึ้นที่สูงเพื่อสำรวจ มองลงมาอย่างภาคภูมิ",
    ],
    "eat": [
        "แมวเดินไปที่ชามอาหารแล้วกินอย่างเอร็ดอร่อย",
        "มุบมิบ มุบมิบ... แมวกินข้าวอย่างตั้งใจ",
        "แมวเลียปากหลังกินอิ่ม แล้วนั่งเลียขน",
    ],
    "ignore": [
        "... แมวเมินไปเลย ไม่สนใจแม้แต่นิดเดียว",
        "แมวหันหลังให้ แกล้งทำเป็นไม่เห็น",
        "แมวนั่งเลียขนอย่างไม่แยแส ราวกับไม่มีใครอยู่",
    ],
    "rub": [
        "แมวเดินมาเสียดสีที่ขา แสดงความรัก~",
        "แมวเอาหัวมาดุนมือ... อยากให้ลูบ",
        "แมวนอนหงายท้องให้! ...แต่อาจเป็นกับดักนะ",
    ],
    "stare": [
        "แมวนั่งจ้องนิ่ง ๆ... ดวงตากลมโตไม่กะพริบ",
        "แมวมองจากมุมห้อง ใครจะรู้ว่าคิดอะไร...",
        "แมวเอียงหัว จ้องมองอย่างสงสัย...",
    ],
}


class RuleBrain:
    """Rule-based decision engine for the cat.

    This will later be replaced/augmented by an ML model (DQN).
    """

    def decide_response(self, state: CatState, memory: CatMemory, user_action: str | None) -> str:
        """Decide what the cat does, considering state, memory, and user action."""

        # Cat-like independence: sometimes ignores commands
        if user_action and self._should_ignore(state, memory):
            return "ignore"

        # If user did something, respond to it
        if user_action:
            return self._respond_to_action(state, memory, user_action)

        # Autonomous behavior when no user input
        return self._autonomous_action(state, memory)

    def _should_ignore(self, state: CatState, memory: CatMemory) -> bool:
        """Cat-like independence — sometimes ignores the owner."""
        # Higher bond = less likely to ignore
        # Bad mood = more likely to ignore
        ignore_chance = 0.15  # Base 15% ignore rate

        if state.mood == "annoyed":
            ignore_chance += 0.3
        if state.mood == "sleepy":
            ignore_chance += 0.2
        if state.bond_level > 0.6:
            ignore_chance -= 0.1
        if state.bond_level < 0.2:
            ignore_chance += 0.15

        return random.random() < ignore_chance

    def _respond_to_action(self, state: CatState, memory: CatMemory, action: str) -> str:
        """Respond to a specific user action based on current state."""

        if action == "feed":
            if state.hunger > 0.5:
                return "eat"
            else:
                return random.choice(["stare", "ignore"])  # Not hungry

        if action == "pet":
            if state.mood in ("happy", "playful", "content"):
                return "purr" if state.bond_level > 0.3 else "rub"
            if state.mood == "annoyed":
                return "hiss"
            if state.mood == "sleepy":
                return random.choice(["purr", "ignore"])
            return "stare"

        if action == "play":
            if state.energy > 0.3 and state.mood in ("playful", "curious", "happy"):
                return "play_alone"  # Joins in playing
            if state.energy < 0.2:
                return "nap"
            return random.choice(["stare", "ignore"])

        if action == "talk":
            if state.bond_level > 0.4:
                return "meow"  # Responds
            return random.choice(["stare", "ignore"])

        # Unknown action
        return "stare"

    def _autonomous_action(self, state: CatState, memory: CatMemory) -> str:
        """What does the cat do on its own?"""

        # Urgent needs first
        if state.hunger > 0.8:
            return "meow"  # Begging for food
        if state.energy < 0.15:
            return "nap"

        # State-driven behavior
        if state.mood == "curious" and state.energy > 0.3:
            return "explore"
        if state.mood == "playful" and state.energy > 0.4:
            return "play_alone"
        if state.mood == "happy" and state.bond_level > 0.5:
            return random.choice(["purr", "rub"])

        # Neglect response
        if memory.neglect_level > 0.7 and state.bond_level > 0.3:
            return "meow"  # Missing the owner

        # Default idle behaviors
        return random.choice(["stare", "nap", "explore", "play_alone"])

    def get_action_text(self, action: str) -> str:
        """Get a random text description for a cat action."""
        texts = ACTION_TEXT.get(action, [f"แมวทำ {action}..."])
        return random.choice(texts)

    def was_positive_interaction(self, state: CatState, cat_action: str) -> bool:
        """Determine if the interaction was positive for the cat."""
        positive_actions = {"purr", "rub", "play_alone", "eat", "meow"}
        negative_actions = {"hiss", "ignore"}

        if cat_action in positive_actions:
            return True
        if cat_action in negative_actions:
            return False
        return state.happiness > 0.4
