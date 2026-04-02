"""ML-powered brain that uses a trained DQN model for cat decisions."""

import os
import numpy as np
from stable_baselines3 import DQN

from src.cat_state import CatState
from src.memory import CatMemory
from src.brain import RuleBrain, ACTION_TEXT, CAT_ACTIONS
from src.cat_env import ACTION_NAMES


class MLBrain(RuleBrain):
    """ML brain that uses DQN for decisions, falls back to rules if no model."""

    def __init__(self, model_path: str = "models/cat_brain_dqn"):
        super().__init__()
        self.model = None
        zip_path = model_path + ".zip"
        if os.path.exists(zip_path):
            self.model = DQN.load(model_path, device="cpu")
            print(f"  🧠 ML brain loaded from {zip_path}")
        else:
            print(f"  ⚠️  No trained model found at {zip_path}")
            print(f"  ⚠️  Using rule-based brain. Run 'python train.py' first.")

    def _encode_user_action(self, action: str | None) -> float:
        mapping = {"feed": 0.2, "pet": 0.4, "play": 0.6, "talk": 0.8}
        return mapping.get(action, 0.0)

    def decide_response(self, state: CatState, memory: CatMemory, user_action: str | None) -> str:
        if self.model is None:
            return super().decide_response(state, memory, user_action)

        obs = np.array([
            state.hunger,
            state.energy,
            state.happiness,
            state.curiosity,
            state.bond_level,
            self._encode_user_action(user_action),
        ], dtype=np.float32)

        action_idx, _ = self.model.predict(obs, deterministic=False)
        return ACTION_NAMES[int(action_idx)]
