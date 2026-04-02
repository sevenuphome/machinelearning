"""Gymnasium custom environment for the cat brain.

The cat is the agent. It observes its internal state and chooses an action.
The reward is designed to produce natural cat-like behavior:
- Eat when hungry, sleep when tired
- Play when energetic and curious
- Bond with owner over time
- Don't just do one thing all the time (variety bonus)
"""

import gymnasium as gym
import numpy as np
from gymnasium import spaces


# Cat actions (same indices as brain.py CAT_ACTIONS)
ACTION_NAMES = [
    "purr",        # 0
    "meow",        # 1
    "hiss",        # 2
    "nap",         # 3
    "play_alone",  # 4
    "explore",     # 5
    "eat",         # 6
    "ignore",      # 7
    "rub",         # 8
    "stare",       # 9
]

# Simulated user actions that happen randomly
USER_ACTIONS = ["feed", "pet", "play", "talk", "none"]


class CatEnv(gym.Env):
    """Environment where the cat agent learns to behave naturally.

    Observation: [hunger, energy, happiness, curiosity, bond_level, user_action_id]
    Action: one of 10 cat behaviors
    Reward: designed to produce natural, cat-like decisions
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode

        # 10 possible cat actions
        self.action_space = spaces.Discrete(10)

        # Observation: 5 state values + 1 user action encoding
        # All values normalized to [0, 1]
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(6,), dtype=np.float32
        )

        self.state = None
        self.step_count = 0
        self.max_steps = 200
        self.recent_actions = []  # Track for variety bonus

    def _encode_user_action(self, action: str) -> float:
        """Encode user action as a float for the observation."""
        mapping = {"feed": 0.2, "pet": 0.4, "play": 0.6, "talk": 0.8, "none": 0.0}
        return mapping.get(action, 0.0)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Random initial state
        self.state = {
            "hunger": self.np_random.uniform(0.1, 0.5),
            "energy": self.np_random.uniform(0.5, 0.9),
            "happiness": self.np_random.uniform(0.3, 0.7),
            "curiosity": self.np_random.uniform(0.3, 0.7),
            "bond_level": self.np_random.uniform(0.0, 0.3),
        }
        self.step_count = 0
        self.recent_actions = []
        self.current_user_action = "none"

        obs = self._get_obs()
        return obs, {}

    def _get_obs(self) -> np.ndarray:
        return np.array([
            self.state["hunger"],
            self.state["energy"],
            self.state["happiness"],
            self.state["curiosity"],
            self.state["bond_level"],
            self._encode_user_action(self.current_user_action),
        ], dtype=np.float32)

    def _clamp(self, v: float) -> float:
        return max(0.0, min(1.0, v))

    def step(self, action: int):
        self.step_count += 1
        action_name = ACTION_NAMES[action]
        self.recent_actions.append(action)

        # Simulate random user action (40% chance of user doing something)
        if self.np_random.random() < 0.4:
            self.current_user_action = self.np_random.choice(["feed", "pet", "play", "talk"])
        else:
            self.current_user_action = "none"

        # Apply user action effects on state
        self._apply_user_action(self.current_user_action)

        # Apply cat action effects on state
        self._apply_cat_action(action_name)

        # Time decay
        self.state["hunger"] = self._clamp(self.state["hunger"] + 0.02)
        self.state["energy"] = self._clamp(self.state["energy"] - 0.01)
        self.state["curiosity"] = self._clamp(self.state["curiosity"] + 0.015)
        self.state["happiness"] = self._clamp(self.state["happiness"] - 0.005)

        # Calculate reward
        reward = self._calculate_reward(action_name)

        terminated = self.step_count >= self.max_steps
        obs = self._get_obs()

        if self.render_mode == "human":
            self.render()

        return obs, reward, terminated, False, {"action_name": action_name}

    def _apply_user_action(self, user_action: str):
        """Apply effects of user action on cat state."""
        if user_action == "feed":
            self.state["hunger"] = self._clamp(self.state["hunger"] - 0.3)
        elif user_action == "pet":
            self.state["happiness"] = self._clamp(self.state["happiness"] + 0.1)
        elif user_action == "play":
            self.state["happiness"] = self._clamp(self.state["happiness"] + 0.1)
            self.state["energy"] = self._clamp(self.state["energy"] - 0.05)
        elif user_action == "talk":
            self.state["bond_level"] = self._clamp(self.state["bond_level"] + 0.02)

    def _apply_cat_action(self, action: str):
        """Apply effects of cat's chosen action on its own state."""
        effects = {
            "purr":       {"happiness": 0.05, "energy": -0.01},
            "meow":       {"energy": -0.02},
            "hiss":       {"happiness": -0.05, "bond_level": -0.05},
            "nap":        {"energy": 0.2, "hunger": 0.05},
            "play_alone": {"energy": -0.1, "happiness": 0.1, "curiosity": -0.1},
            "explore":    {"energy": -0.05, "curiosity": -0.15, "happiness": 0.05},
            "eat":        {"hunger": -0.3, "happiness": 0.05},
            "ignore":     {},
            "rub":        {"bond_level": 0.05, "happiness": 0.05},
            "stare":      {"curiosity": -0.02},
        }
        for attr, delta in effects.get(action, {}).items():
            self.state[attr] = self._clamp(self.state[attr] + delta)

    def _calculate_reward(self, action: str) -> float:
        """Reward function that encourages natural cat behavior."""
        reward = 0.0
        s = self.state

        # 1. Survival rewards: eat when hungry, sleep when tired
        if action == "eat" and s["hunger"] > 0.5:
            reward += 2.0  # Good: eating when hungry
        elif action == "eat" and s["hunger"] < 0.2:
            reward -= 1.0  # Bad: eating when not hungry
        if action == "nap" and s["energy"] < 0.3:
            reward += 2.0  # Good: sleeping when tired
        elif action == "nap" and s["energy"] > 0.7:
            reward -= 0.5  # Meh: sleeping when fully rested

        # 2. Emotional rewards: play when happy, explore when curious
        if action == "play_alone" and s["happiness"] > 0.5 and s["energy"] > 0.4:
            reward += 1.5
        if action == "explore" and s["curiosity"] > 0.5:
            reward += 1.5

        # 3. Social rewards: bond when owner is interacting
        user = self.current_user_action
        if user == "pet" and action == "purr":
            reward += 2.0  # Purring when petted
        if user == "pet" and action == "hiss":
            reward -= 1.0  # Hissing when petted (unless annoyed)
        if user == "play" and action == "play_alone":
            reward += 2.0  # Playing when owner plays
        if user == "talk" and action == "meow":
            reward += 1.0  # Responding to talk
        if user != "none" and action == "rub" and s["bond_level"] > 0.3:
            reward += 1.0  # Showing affection when bonded

        # 4. Independence: sometimes ignoring is natural
        if user != "none" and action == "ignore" and s["happiness"] > 0.5:
            reward += 0.3  # Cats ignore sometimes, that's ok

        # 5. Penalty for bad state
        if s["hunger"] > 0.8:
            reward -= 1.0  # Being too hungry is bad
        if s["energy"] < 0.1:
            reward -= 1.0  # Being exhausted is bad

        # 6. Variety bonus: don't repeat the same action too much
        if len(self.recent_actions) >= 5:
            last_5 = [int(a) for a in self.recent_actions[-5:]]
            unique = len(set(last_5))
            if unique == 1:
                reward -= 1.0  # Doing same thing 5 times in a row
            elif unique >= 3:
                reward += 0.3  # Good variety

        # 7. Small baseline: keep overall happiness up
        reward += (s["happiness"] - 0.5) * 0.2

        return reward

    def render(self):
        if self.render_mode == "human":
            s = self.state
            print(f"  Step {self.step_count}: "
                  f"H={s['hunger']:.2f} E={s['energy']:.2f} "
                  f"Hap={s['happiness']:.2f} C={s['curiosity']:.2f} "
                  f"B={s['bond_level']:.2f} | User: {self.current_user_action}")
