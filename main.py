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

USER_COMMANDS = {
    "feed":    "ให้อาหาร",
    "pet":     "ลูบหัว",
    "play":    "เล่นด้วย",
    "talk":    "พูดคุย",
    "look":    "ดูสถานะ",
    "wait":    "รอ (ให้เวลาผ่าน)",
    "help":    "แสดงคำสั่งทั้งหมด",
    "quit":    "ออกจากเกม",
}


def print_banner(cat_name: str):
    print(f"""
╔══════════════════════════════════════╗
║     🐱 Cat Brain AI — {cat_name:6s}       ║
║     Virtual Pet with a Mind         ║
╚══════════════════════════════════════╝
""")


def print_help():
    print("\n  คำสั่งที่ใช้ได้:")
    for cmd, desc in USER_COMMANDS.items():
        print(f"    {cmd:8s} — {desc}")
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
    print(f"  แมวตัวนี้ดูมีนิสัยเป็นของตัวเอง\n")
    print_help()

    # Show initial state
    print(f"  --- สถานะของ {cat_name} ---")
    print(state.summary())
    print()

    while True:
        try:
            user_input = input(f"  [{cat_name}] > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {cat_name} มองตามขณะที่คุณเดินจากไป... เมี้ยว~")
            break

        if not user_input:
            continue

        if user_input == "quit":
            print(f"\n  {cat_name} มองตามขณะที่คุณเดินจากไป... เมี้ยว~")
            break

        if user_input == "help":
            print_help()
            continue

        if user_input == "look":
            state.tick()
            print(f"\n  --- สถานะของ {cat_name} ---")
            print(state.summary())
            print(f"\n  --- ความสัมพันธ์ ---")
            print(memory.relationship_summary())
            print()
            continue

        if user_input == "wait":
            state.tick()
            # Autonomous behavior
            cat_action = brain.decide_response(state, memory, user_action=None)
            text = brain.get_action_text(cat_action)
            print(f"\n  (เวลาผ่านไป...)")
            print(f"  {text}\n")
            continue

        if user_input not in ("feed", "pet", "play", "talk"):
            print(f"  ไม่เข้าใจคำสั่ง '{user_input}' — พิมพ์ 'help' เพื่อดูคำสั่ง\n")
            continue

        # Process user action
        state.tick()
        cat_action = brain.decide_response(state, memory, user_action=user_input)
        was_positive = brain.was_positive_interaction(state, cat_action)

        # Apply effects to cat state
        state.apply_action(user_input)

        # Record in memory
        memory.record(user_input, state.mood, was_positive)

        # Update bond based on interaction quality
        if was_positive:
            state.bond_level = state.clamp(state.bond_level + 0.02)
        else:
            state.bond_level = state.clamp(state.bond_level - 0.01)

        # Show cat's response
        text = brain.get_action_text(cat_action)
        print(f"\n  {text}\n")


if __name__ == "__main__":
    main()
