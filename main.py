#!/usr/bin/env python3
"""Cat Brain AI — Virtual Pet with Cat-like Behavior.

A text-based virtual cat that has emotions, memory, and makes its own decisions.
"""

import argparse
import random
import sys

from src.cat_state import CatState
from src.brain import RuleBrain, CAT_ACTIONS
from src.memory import CatMemory

# Cat names for random selection
CAT_NAMES = ["มิโกะ", "โมจิ", "ซูชิ", "ทามะ", "ลูน่า", "มาเมะ", "คุโระ", "ชิโร่"]

MENU_OPTIONS = [
    ("feed", "🍖 ให้อาหาร"),
    ("pet",  "🤚 ลูบหัว"),
    ("play", "🧶 เล่นด้วย"),
    ("talk", "💬 พูดคุย"),
    ("wait", "⏳ รอ (ดูแมวทำอะไร)"),
    ("look", "👀 ดูสถานะ"),
    ("quit", "👋 ออกจากเกม"),
]


def print_banner(cat_name: str):
    print(f"""
  ╔══════════════════════════════════════╗
  ║     🐱 Cat Brain AI — {cat_name:6s}       ║
  ║     Virtual Pet with a Mind         ║
  ╚══════════════════════════════════════╝

       /\\_/\\
      ( o.o )   สวัสดี! ฉันชื่อ {cat_name}
       > ^ <
      /|   |\\
     (_|   |_)
""")


CAT_FACE = {
    "happy":    "  ( ^.^ )",
    "playful":  "  ( >w< )",
    "content":  "  ( -.- )",
    "sleepy":   "  ( =.= ) zzz",
    "hungry":   "  ( >o< )",
    "annoyed":  "  ( >.< )",
    "curious":  "  ( o.O )",
}


def print_menu():
    print()
    for i, (_, label) in enumerate(MENU_OPTIONS, 1):
        print(f"    {i}. {label}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Cat Brain AI")
    parser.add_argument("--ml", action="store_true", help="Use ML brain (requires trained model)")
    args = parser.parse_args()

    cat_name = random.choice(CAT_NAMES)
    state = CatState()
    memory = CatMemory()

    if args.ml:
        from src.ml_brain import MLBrain
        brain = MLBrain()
    else:
        brain = RuleBrain()

    print_banner(cat_name)
    print(f"  {cat_name} เดินเข้ามาหา... ดวงตากลมโตมองอย่างสงสัย")
    print(f"  แมวตัวนี้ดูมีนิสัยเป็นของตัวเอง")

    # Show initial state
    print(f"\n  --- สถานะของ {cat_name} ---")
    print(state.summary())

    while True:
        print_menu()
        try:
            choice = input(f"  [{cat_name}] เลือก (1-{len(MENU_OPTIONS)}): ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {cat_name} มองตามขณะที่คุณเดินจากไป... เมี้ยว~")
            break

        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU_OPTIONS)):
            print(f"  กรุณาเลือก 1-{len(MENU_OPTIONS)}")
            continue

        cmd, _ = MENU_OPTIONS[int(choice) - 1]

        if cmd == "quit":
            print(f"\n  {cat_name} มองตามขณะที่คุณเดินจากไป... เมี้ยว~")
            break

        if cmd == "look":
            state.tick()
            print(f"\n  --- สถานะของ {cat_name} ---")
            print(state.summary())
            print(f"\n  --- ความสัมพันธ์ ---")
            print(memory.relationship_summary())
            continue

        if cmd == "wait":
            state.tick()
            cat_action = brain.decide_response(state, memory, user_action=None)
            text = brain.get_action_text(cat_action)
            face = CAT_FACE.get(state.mood, "  ( o.o )")
            print(f"\n  (เวลาผ่านไป...)")
            print(f"  /\\_/\\")
            print(f" {face}")
            print(f"  > ^ <")
            print(f"  {text}")
            continue

        # Process user action (feed, pet, play, talk)
        state.tick()
        cat_action = brain.decide_response(state, memory, user_action=cmd)
        was_positive = brain.was_positive_interaction(state, cat_action)

        state.apply_action(cmd)
        memory.record(cmd, state.mood, was_positive)

        if was_positive:
            state.bond_level = state.clamp(state.bond_level + 0.02)
        else:
            state.bond_level = state.clamp(state.bond_level - 0.01)

        text = brain.get_action_text(cat_action)
        face = CAT_FACE.get(state.mood, "  ( o.o )")
        print(f"\n  /\\_/\\")
        print(f" {face}")
        print(f"  > ^ <")
        print(f"  {text}")


if __name__ == "__main__":
    main()
