#!/usr/bin/env python3
"""ARC-AGI-3 game player. Uses Claude to reason about frames and pick actions.

This is the ONLY file modified during the autoresearch loop.
"""

import os, sys, json, time
import httpx, anthropic

# === Configuration ===
MODEL = "claude-sonnet-4-6"  # reasoning model
EVAL_GAMES = 5               # games per evaluation run
MAX_STEPS = 200              # max actions per game

SYSTEM_PROMPT = """\
You are playing an ARC-AGI-3 interactive grid game.
Your goal is to figure out the game's rules and complete all levels.
Analyze the grid carefully. Track what changes between frames. Act strategically.
When unsure, try different actions to learn the game mechanics."""

# === ARC API ===
BASE = "https://three.arcprize.org"
KEY = os.environ["ARC_API_KEY"]


def api(session, method, path, body=None):
    """Call ARC API with retry on rate limit."""
    headers = {"X-API-Key": KEY, "Content-Type": "application/json"}
    for attempt in range(3):
        if method == "GET":
            r = session.get(f"{BASE}{path}", headers=headers)
        else:
            r = session.post(f"{BASE}{path}", headers=headers, json=body or {})
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


# === Frame rendering ===
def render(frame_data):
    """Render frame as compact text grid. Skip all-zero rows."""
    lines = []
    for frame in frame_data:
        for y, row in enumerate(frame):
            if any(v != 0 for v in row):
                cells = ["." if v == 0 else hex(v)[2:] for v in row]
                lines.append(f"{y:02d}|{''.join(cells)}")
    return "\n".join(lines) or "(empty)"


# === Claude reasoning ===
def pick_action(claude, frame, actions, game_id, levels, history):
    """Ask Claude to pick the next action."""
    hist = "\n".join(f"  {h}" for h in history[-15:])
    msg = f"""\
Game: {game_id} | Levels completed: {levels}
Available actions: {actions}

Frame (. = black/empty, 1-f = colors):
{render(frame)}

{"Recent history:\n" + hist if hist else ""}

What action? Reply ONLY: ACTION<N> or ACTION6 <x> <y>"""

    resp = claude.messages.create(
        model=MODEL, max_tokens=256, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": msg}],
    )
    text = resp.content[0].text.strip()

    # Parse last ACTION line in response
    for line in reversed(text.split("\n")):
        if "ACTION" in line:
            parts = line.split("ACTION")[-1].strip().split()
            try:
                n = int(parts[0])
                if n == 6 and len(parts) >= 3:
                    x = int(parts[1].strip("x=,"))
                    y = int(parts[2].strip("y=,"))
                    return f"ACTION6", {"x": x, "y": y}
                return f"ACTION{n}", {}
            except (ValueError, IndexError):
                pass
    return f"ACTION{actions[0]}", {}  # fallback


# === Game loop ===
def play(game_id, card_id, session, claude):
    """Play one game. Returns (levels_completed, state, steps)."""
    obs = api(session, "POST", "/api/cmd/RESET",
              {"game_id": game_id, "card_id": card_id, "guid": None})
    guid = obs["guid"]
    history = []

    for step in range(MAX_STEPS):
        state = obs.get("state", "NOT_FINISHED")
        levels = obs.get("levels_completed", 0)
        if state in ("WIN", "GAME_OVER"):
            return levels, state, step

        cmd, kwargs = pick_action(
            claude, obs.get("frame", []),
            obs.get("available_actions", [1, 2, 3, 4]),
            game_id, levels, history,
        )
        body = {"game_id": game_id, "guid": guid, **kwargs}
        obs = api(session, "POST", f"/api/cmd/{cmd}", body)
        history.append(
            f"step{step}: {cmd}"
            + (f" {kwargs}" if kwargs else "")
            + f" -> {obs.get('state', '?')} lvl={obs.get('levels_completed', 0)}"
        )

    return obs.get("levels_completed", 0), "MAX_STEPS", MAX_STEPS


# === Main ===
def main():
    session = httpx.Client(timeout=60)
    claude = anthropic.Anthropic()

    games = api(session, "GET", "/api/games")
    eval_set = games[:EVAL_GAMES]
    sc = api(session, "POST", "/api/scorecard/open", {})
    card_id = sc["card_id"]

    results = []
    for g in eval_set:
        gid = g["game_id"] if isinstance(g, dict) else g
        name = g.get("title", gid) if isinstance(g, dict) else gid
        print(f"Playing {name}...", end=" ", flush=True)
        try:
            lvl, state, steps = play(gid, card_id, session, claude)
            print(f"{state} levels={lvl} steps={steps}")
            results.append((gid, lvl, state, steps))
        except Exception as e:
            print(f"ERROR: {e}")
            results.append((gid, 0, "ERROR", 0))

    try:
        api(session, "POST", "/api/scorecard/close", {"card_id": card_id})
    except Exception:
        pass

    wins = sum(1 for _, _, s, _ in results if s == "WIN")
    total = sum(l for _, l, _, _ in results)
    n = len(results)

    print(f"\nwin_rate:    {wins / n:.4f}")
    print(f"avg_levels:  {total / n:.2f}")
    print(f"total_levels:{total}")
    print(f"wins:        {wins}")
    print(f"games:       {n}")
    for gid, lvl, state, steps in results:
        print(f"  {gid}: {state} levels={lvl} steps={steps}")


if __name__ == "__main__":
    main()
