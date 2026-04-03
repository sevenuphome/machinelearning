#!/usr/bin/env python3
"""Web server for Cat Brain AI."""

import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.cat_state import CatState
from src.brain import RuleBrain
from src.memory import CatMemory

# Try ML brain, fall back to rules
try:
    from src.ml_brain import MLBrain
    _brain = MLBrain()
except Exception:
    _brain = RuleBrain()

app = FastAPI()

# In-memory sessions (each visitor gets their own cat)
sessions: dict[str, dict] = {}


def get_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {
            "state": CatState(),
            "memory": CatMemory(),
        }
    return sessions[session_id]


class ActionRequest(BaseModel):
    session_id: str
    action: str  # feed, pet, play, talk, wait


@app.post("/api/action")
def do_action(req: ActionRequest):
    session = get_session(req.session_id)
    state: CatState = session["state"]
    memory: CatMemory = session["memory"]

    state.tick()

    if req.action == "wait":
        cat_action = _brain.decide_response(state, memory, user_action=None)
        was_positive = _brain.was_positive_interaction(state, cat_action)
    elif req.action in ("feed", "pet", "play", "talk"):
        cat_action = _brain.decide_response(state, memory, user_action=req.action)
        was_positive = _brain.was_positive_interaction(state, cat_action)
        state.apply_action(req.action)
        memory.record(req.action, state.mood, was_positive)
        if was_positive:
            state.bond_level = state.clamp(state.bond_level + 0.02)
        else:
            state.bond_level = state.clamp(state.bond_level - 0.01)
    else:
        cat_action = "stare"

    text = _brain.get_action_text(cat_action)

    return _build_response(state, memory, cat_action=cat_action, text=text)


@app.get("/api/state")
def get_state(session_id: str):
    session = get_session(session_id)
    state: CatState = session["state"]
    memory: CatMemory = session["memory"]
    state.tick()
    return _build_response(state, memory)


def _build_response(state: CatState, memory: CatMemory, cat_action: str = "", text: str = "") -> dict:
    from datetime import datetime
    return {
        "cat_action": cat_action,
        "text": text,
        "mood": state.mood,
        "time_period": state.time_period,
        "time_period_th": state.time_period_th,
        "hour": datetime.now().hour,
        "state": {
            "hunger": round(state.hunger, 2),
            "energy": round(state.energy, 2),
            "happiness": round(state.happiness, 2),
            "curiosity": round(state.curiosity, 2),
            "bond": round(state.bond_level, 2),
        },
        "relationship": {
            "total": memory.total_interactions,
            "positivity": round(memory.recent_positive_ratio, 2),
        },
    }


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = Path(__file__).parent / "static" / "index.html"
    return html_path.read_text()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
