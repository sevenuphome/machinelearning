#!/usr/bin/env python3
"""Train the cat brain using DQN (Deep Q-Network).

This script trains a neural network to make decisions like a cat
using reinforcement learning with Stable-Baselines3.
"""

import os
import gymnasium as gym
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy

from src.cat_env import CatEnv, ACTION_NAMES

# Register our custom environment
gym.register(id="CatBrain-v0", entry_point="src.cat_env:CatEnv", max_episode_steps=200)


def train(total_timesteps: int = 50_000):
    """Train the DQN model."""
    print("=" * 50)
    print("  🐱 Cat Brain AI — Training")
    print("=" * 50)

    env = gym.make("CatBrain-v0")

    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=1e-3,
        buffer_size=10_000,
        learning_starts=1_000,
        batch_size=64,
        gamma=0.99,
        exploration_fraction=0.3,
        exploration_final_eps=0.05,
        target_update_interval=500,
        verbose=1,
        device="cpu",  # CPU is fine for this small model
    )

    print(f"\n  Training for {total_timesteps:,} timesteps...")
    print(f"  Network: {model.policy}\n")

    model.learn(total_timesteps=total_timesteps, progress_bar=True)

    # Save the model
    os.makedirs("models", exist_ok=True)
    model_path = "models/cat_brain_dqn"
    model.save(model_path)
    print(f"\n  Model saved to {model_path}.zip")

    # Evaluate
    print("\n  Evaluating trained model...")
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=20)
    print(f"  Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

    # Compare with random
    print("\n  Comparing with random agent...")
    random_rewards = []
    for _ in range(20):
        obs, _ = env.reset()
        total_reward = 0
        done = False
        while not done:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, _ = env.step(action)
            total_reward += reward
            done = terminated or truncated
        random_rewards.append(total_reward)

    import numpy as np
    random_mean = np.mean(random_rewards)
    random_std = np.std(random_rewards)
    print(f"  Random agent reward: {random_mean:.2f} +/- {random_std:.2f}")

    improvement = ((mean_reward - random_mean) / abs(random_mean)) * 100 if random_mean != 0 else 0
    print(f"\n  🎯 ML brain is {improvement:+.1f}% better than random!")

    # Show sample behavior
    print("\n" + "=" * 50)
    print("  Sample behavior from trained cat:")
    print("=" * 50)

    obs, _ = env.reset()
    for step in range(20):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        action_name = ACTION_NAMES[action]
        user = env.unwrapped.current_user_action
        s = env.unwrapped.state
        mood = "😴" if s["energy"] < 0.3 else "😾" if s["happiness"] < 0.3 else "😺"
        print(f"  {mood} Step {step+1:2d}: Cat={action_name:12s} | "
              f"User={user:5s} | H={s['hunger']:.1f} E={s['energy']:.1f} "
              f"Hap={s['happiness']:.1f}")
        if terminated or truncated:
            break

    env.close()
    print(f"\n  Done! Run 'python main.py --ml' to play with the ML cat.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Cat Brain DQN")
    parser.add_argument("--steps", type=int, default=50_000, help="Training timesteps")
    args = parser.parse_args()
    train(total_timesteps=args.steps)
