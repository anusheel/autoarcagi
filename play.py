#!/usr/bin/env python3
"""ARC-AGI-3 API client. Thin CLI wrapper for Claude Code to call.

Usage:
    play.py games                                  List available games
    play.py scorecard-open                         Open a new scorecard
    play.py scorecard-close <card_id>              Close scorecard, get results
    play.py scorecard-get <card_id>                Get scorecard status
    play.py reset <game_id> <card_id>              Start/reset a game
    play.py action <CMD> <game_id> <guid> [x y]   Take an action (ACTION1-7)
    play.py explore <game_id> <card_id> [N]        Try N random actions, report changes
"""

import os, sys, json, time, random
import httpx

BASE = "https://three.arcprize.org"
KEY = os.environ["ARC_API_KEY"]


def api(method, path, body=None):
    """Call ARC API with retry on rate limit."""
    session = httpx.Client(timeout=60)
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


def render(frame_data):
    """Render frame as compact text grid. Skip all-zero rows."""
    lines = []
    for fi, frame in enumerate(frame_data):
        if len(frame_data) > 1:
            lines.append(f"--- Frame {fi} ---")
        for y, row in enumerate(frame):
            if any(v != 0 for v in row):
                cells = ["." if v == 0 else hex(v)[2:] for v in row]
                lines.append(f"{y:02d}|{''.join(cells)}")
    return "\n".join(lines) or "(empty)"


def print_obs(obs):
    """Print observation in a readable format."""
    print(f"state:   {obs.get('state', '?')}")
    print(f"levels:  {obs.get('levels_completed', 0)}/{obs.get('win_levels', '?')}")
    print(f"guid:    {obs.get('guid', '?')}")
    print(f"actions: {obs.get('available_actions', [])}")
    print(f"frame:")
    print(render(obs.get("frame", [])))


def main():
    cmd = sys.argv[1]

    if cmd == "games":
        games = api("GET", "/api/games")
        for g in games:
            gid = g["game_id"] if isinstance(g, dict) else g
            title = g.get("title", "") if isinstance(g, dict) else ""
            print(f"{gid}  {title}")

    elif cmd == "scorecard-open":
        r = api("POST", "/api/scorecard/open", {})
        print(json.dumps(r))

    elif cmd == "scorecard-close":
        r = api("POST", "/api/scorecard/close", {"card_id": sys.argv[2]})
        print(json.dumps(r, indent=2))

    elif cmd == "scorecard-get":
        r = api("GET", f"/api/scorecard/{sys.argv[2]}")
        print(json.dumps(r, indent=2))

    elif cmd == "reset":
        game_id, card_id = sys.argv[2], sys.argv[3]
        guid = sys.argv[4] if len(sys.argv) > 4 else None
        obs = api("POST", "/api/cmd/RESET", {
            "game_id": game_id, "card_id": card_id, "guid": guid,
        })
        print_obs(obs)

    elif cmd == "action":
        action_cmd, game_id, guid = sys.argv[2], sys.argv[3], sys.argv[4]
        body = {"game_id": game_id, "guid": guid}
        if action_cmd == "ACTION6" and len(sys.argv) >= 7:
            body["x"] = int(sys.argv[5])
            body["y"] = int(sys.argv[6])
        obs = api("POST", f"/api/cmd/{action_cmd}", body)
        print_obs(obs)

    elif cmd == "explore":
        game_id, card_id = sys.argv[2], sys.argv[3]
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        obs = api("POST", "/api/cmd/RESET", {
            "game_id": game_id, "card_id": card_id, "guid": None,
        })
        guid = obs["guid"]
        actions = obs.get("available_actions", [1, 2, 3, 4])
        print(f"game:    {game_id}")
        print(f"guid:    {guid}")
        print(f"levels:  0/{obs.get('win_levels', '?')}")
        print(f"actions: {actions}")
        print(f"initial frame:")
        print(render(obs.get("frame", [])))
        print(f"\n--- Exploring {n} random actions ---")
        best_levels = 0
        for step in range(n):
            act = random.choice(actions)
            body = {"game_id": game_id, "guid": guid}
            if act == 6:
                body["x"] = random.randint(0, 63)
                body["y"] = random.randint(0, 63)
            obs = api("POST", f"/api/cmd/ACTION{act}", body)
            state = obs.get("state", "?")
            levels = obs.get("levels_completed", 0)
            if levels > best_levels:
                best_levels = levels
                xy = f" x={body.get('x')} y={body.get('y')}" if act == 6 else ""
                print(f"  step {step}: ACTION{act}{xy} -> levels={levels} state={state}")
            if state in ("WIN", "GAME_OVER"):
                print(f"  step {step}: ACTION{act} -> {state} levels={levels}")
                break
        print(f"\nfinal_state: {obs.get('state', '?')}")
        print(f"levels_completed: {obs.get('levels_completed', 0)}")
        print(f"steps: {step + 1}")
        print(f"best_levels: {best_levels}")

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
