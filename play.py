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

    elif cmd == "probe":
        # Try each action once, show which rows changed vs initial frame
        game_id, card_id = sys.argv[2], sys.argv[3]
        obs = api("POST", "/api/cmd/RESET", {
            "game_id": game_id, "card_id": card_id, "guid": None,
        })
        guid = obs["guid"]
        actions = obs.get("available_actions", [1, 2, 3, 4])
        initial = render(obs.get("frame", []))
        initial_lines = initial.split("\n")
        print(f"game: {game_id} | guid: {guid} | actions: {actions}")
        print(f"levels: 0/{obs.get('win_levels', '?')}")
        print(f"\ninitial frame:\n{initial}\n")
        for act in actions:
            if act == 6:
                # Try a few click positions
                for x, y in [(32, 32), (16, 16), (48, 48)]:
                    body = {"game_id": game_id, "guid": guid, "x": x, "y": y}
                    obs2 = api("POST", f"/api/cmd/ACTION{act}", body)
                    after = render(obs2.get("frame", []))
                    after_lines = after.split("\n")
                    changed = []
                    for i, (a, b) in enumerate(zip(initial_lines, after_lines)):
                        if a != b:
                            changed.append(f"  was: {a}")
                            changed.append(f"  now: {b}")
                    state = obs2.get("state", "?")
                    lvl = obs2.get("levels_completed", 0)
                    print(f"ACTION{act} x={x} y={y} -> state={state} levels={lvl}")
                    if changed:
                        print("\n".join(changed[:20]))
                    else:
                        print("  (no change)")
                    # Reset back
                    obs = api("POST", "/api/cmd/RESET", {
                        "game_id": game_id, "card_id": card_id, "guid": guid,
                    })
                    guid = obs["guid"]
                    initial_lines = render(obs.get("frame", [])).split("\n")
            else:
                body = {"game_id": game_id, "guid": guid}
                obs2 = api("POST", f"/api/cmd/ACTION{act}", body)
                after = render(obs2.get("frame", []))
                after_lines = after.split("\n")
                changed = []
                for i, (a, b) in enumerate(zip(initial_lines, after_lines)):
                    if a != b:
                        changed.append(f"  was: {a}")
                        changed.append(f"  now: {b}")
                state = obs2.get("state", "?")
                lvl = obs2.get("levels_completed", 0)
                print(f"ACTION{act} -> state={state} levels={lvl}")
                if changed:
                    print("\n".join(changed[:20]))
                else:
                    print("  (no change)")
                # Reset back
                obs = api("POST", "/api/cmd/RESET", {
                    "game_id": game_id, "card_id": card_id, "guid": guid,
                })
                guid = obs["guid"]
                initial_lines = render(obs.get("frame", [])).split("\n")

    elif cmd == "seq":
        # Execute a sequence of actions with block position tracking
        # Usage: play.py seq <game_id> <guid> UUUULLLLDR
        game_id, guid = sys.argv[2], sys.argv[3]
        moves = sys.argv[4].upper()
        action_map = {"U": "ACTION1", "D": "ACTION2", "L": "ACTION3", "R": "ACTION4",
                       "S": "ACTION5", "X": "ACTION7"}
        prev_frame = None
        for i, m in enumerate(moves):
            act = action_map.get(m)
            if not act:
                print(f"Unknown move '{m}', use U/D/L/R/S/X")
                continue
            obs = api("POST", f"/api/cmd/{act}", {"game_id": game_id, "guid": guid})
            state = obs.get("state", "?")
            levels = obs.get("levels_completed", 0)
            # Find block (5 consecutive val=12 in a row) and cross (val=1)
            frame = obs.get("frame", [[]])
            blk_r, blk_c, cross_r, cross_c = -1, -1, -1, -1
            cells_changed = 0
            for fi, f in enumerate(frame):
                for y, row in enumerate(f):
                    # Find block: 5 consecutive pixels of value 12
                    for x in range(len(row) - 4):
                        if blk_r == -1 and all(row[x+j] == 12 for j in range(5)):
                            blk_r, blk_c = y, x
                    # Find cross: value 1 surrounded by value 0
                    for x, val in enumerate(row):
                        if val == 1 and cross_r == -1:
                            cross_r, cross_c = y, x
                        if prev_frame and fi < len(prev_frame):
                            if y < len(prev_frame[fi]) and x < len(prev_frame[fi][y]):
                                if val != prev_frame[fi][y][x]:
                                    cells_changed += 1
            dist = abs(blk_r - cross_r) + abs(blk_c - cross_c) if blk_r >= 0 and cross_r >= 0 else -1
            print(f"{i+1:3d}. {m} -> lvl={levels} blk=({blk_r},{blk_c}) cross=({cross_r},{cross_c}) dist={dist} changed={cells_changed}")
            prev_frame = frame
            if state in ("WIN", "GAME_OVER"):
                print(f"     {state}!")
                break
        print(f"\nfinal frame:")
        print_obs(obs)

    elif cmd == "solve":
        # BFS over action sequences, resetting between tries, looking for level completion
        # Usage: play.py solve <game_id> <card_id> [max_depth] [beam_width]
        game_id, card_id = sys.argv[2], sys.argv[3]
        max_depth = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        beam = int(sys.argv[5]) if len(sys.argv) > 5 else 50
        # Get initial state
        obs = api("POST", "/api/cmd/RESET", {
            "game_id": game_id, "card_id": card_id, "guid": None,
        })
        guid = obs["guid"]
        actions = obs.get("available_actions", [1, 2, 3, 4])
        print(f"game: {game_id} | actions: {actions} | levels: 0/{obs.get('win_levels','?')}")
        print(f"searching depth {max_depth}, beam {beam}...")

        best_levels = 0
        best_seq = ""
        tried = 0
        # Try random sequences, keep the best
        for trial in range(beam):
            obs = api("POST", "/api/cmd/RESET", {
                "game_id": game_id, "card_id": card_id, "guid": guid,
            })
            guid = obs["guid"]
            seq = ""
            names = {1: "U", 2: "D", 3: "L", 4: "R", 5: "S", 6: "C", 7: "X"}
            for step in range(max_depth):
                act = random.choice(actions)
                body = {"game_id": game_id, "guid": guid}
                if act == 6:
                    body["x"] = random.randint(0, 63)
                    body["y"] = random.randint(0, 63)
                obs = api("POST", f"/api/cmd/ACTION{act}", body)
                seq += names.get(act, str(act))
                state = obs.get("state", "?")
                levels = obs.get("levels_completed", 0)
                if levels > best_levels:
                    best_levels = levels
                    best_seq = seq
                    print(f"  NEW BEST: levels={levels} seq={seq} (trial {trial})")
                if state in ("WIN", "GAME_OVER"):
                    break
            tried += 1
            if tried % 10 == 0:
                print(f"  tried {tried}/{beam}, best_levels={best_levels}")

        print(f"\nbest_levels: {best_levels}")
        print(f"best_seq:    {best_seq}")
        print(f"trials:      {tried}")

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
