#!/usr/bin/env python3
"""ARC-AGI-3 API client and exploration library.

CLI usage:
    play.py games                                  List available games
    play.py scorecard-open                         Open a new scorecard
    play.py scorecard-close <card_id>              Close scorecard, get results
    play.py scorecard-get <card_id>                Get scorecard status
    play.py reset <game_id> <card_id>              Start/reset a game
    play.py action <CMD> <game_id> <guid> [x y]   Take an action (ACTION1-7)
    play.py explore <game_id> <card_id> [N]        Try N random actions, report changes
    play.py run-experiment <script.py>             Run a generated experiment script

Importable API (for generated experiment scripts):
    from play import api, render, reset, act, seq, find_objects, diff_frames, frame_to_grid
"""

import os, sys, json, time, random
import pickle
from pathlib import Path

import httpx

BASE = "https://three.arcprize.org"
KEY = os.environ["ARC_API_KEY"]

COOKIE_FILE = Path(__file__).parent / ".cookies"
ACTION_MAP = {"U": "ACTION1", "D": "ACTION2", "L": "ACTION3", "R": "ACTION4",
              "S": "ACTION5", "X": "ACTION7"}
ACTION_NAMES = {1: "U", 2: "D", 3: "L", 4: "R", 5: "S", 6: "C", 7: "X"}


def _load_cookies():
    """Load cookies from file for session persistence across processes."""
    if COOKIE_FILE.exists():
        try:
            jar = pickle.loads(COOKIE_FILE.read_bytes())
            return httpx.Client(timeout=60, cookies=jar)
        except Exception:
            pass
    return httpx.Client(timeout=60)


def _save_cookies(client):
    """Save cookies to file."""
    try:
        COOKIE_FILE.write_bytes(pickle.dumps(dict(client.cookies)))
    except Exception:
        pass


SESSION = _load_cookies()


STATUS_DIR = Path(__file__).parent / "status"
_SCRIPT_TITLE_CACHE = None
_LOG_LINES = []


def _script_title():
    """Extract title from first comment line of the calling script."""
    global _SCRIPT_TITLE_CACHE
    if _SCRIPT_TITLE_CACHE is not None:
        return _SCRIPT_TITLE_CACHE
    try:
        script = Path(sys.argv[0]).resolve()
        first_line = script.read_text().split("\n", 1)[0]
        if first_line.startswith("#") and not first_line.startswith("#!"):
            _SCRIPT_TITLE_CACHE = first_line.lstrip("# ").strip()
        else:
            _SCRIPT_TITLE_CACHE = ""
    except Exception:
        _SCRIPT_TITLE_CACHE = ""
    return _SCRIPT_TITLE_CACHE


def log(msg):
    """Log a message to both stdout and the dashboard status file."""
    print(msg)
    _LOG_LINES.append(msg)


def _write_status(body, data):
    """Write latest frame to status dir for dashboard. Best-effort, never throws."""
    try:
        guid = data.get("guid")
        if not guid or "frame" not in data:
            return
        STATUS_DIR.mkdir(exist_ok=True)
        experiment = Path(sys.argv[0]).name if sys.argv[0] else "interactive"
        title = _script_title() or experiment
        status = {
            "game_id": (body or {}).get("game_id"),
            "guid": guid,
            "frame": data.get("frame"),
            "state": data.get("state"),
            "levels_completed": data.get("levels_completed", 0),
            "experiment": experiment,
            "title": title,
            "logs": _LOG_LINES[:],
            "updated_at": time.time(),
        }
        (STATUS_DIR / f"{guid}.json").write_text(json.dumps(status))
    except Exception:
        pass


def api(method, path, body=None):
    """Call ARC API with retry on rate limit."""
    headers = {"X-API-Key": KEY, "Content-Type": "application/json"}
    for attempt in range(3):
        if method == "GET":
            r = SESSION.get(f"{BASE}{path}", headers=headers)
        else:
            r = SESSION.post(f"{BASE}{path}", headers=headers, json=body or {})
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        _save_cookies(SESSION)
        data = r.json()
        _write_status(body, data)
        return data
    r.raise_for_status()


# ── High-level helpers (for generated experiment scripts) ─────────────

def start(game_id):
    """Open a fresh scorecard, reset the game, return (card_id, obs). Use this in experiment scripts."""
    card = api("POST", "/api/scorecard/open", {})
    card_id = card.get("card_id") or card.get("id")
    obs = api("POST", "/api/cmd/RESET", {"game_id": game_id, "card_id": card_id})
    return card_id, obs


def reset(game_id, card_id, guid=None):
    """Reset game, return obs dict with keys: guid, frame, state, levels_completed, available_actions."""
    return api("POST", "/api/cmd/RESET", {"game_id": game_id, "card_id": card_id, "guid": guid})


def act(action_cmd, game_id, guid, x=None, y=None):
    """Execute a single action. action_cmd is e.g. 'ACTION1' or 'U'/'D'/'L'/'R'/'S'/'X'.
    Returns obs dict."""
    if action_cmd in ACTION_MAP:
        action_cmd = ACTION_MAP[action_cmd]
    body = {"game_id": game_id, "guid": guid}
    if x is not None and y is not None:
        body["x"], body["y"] = int(x), int(y)
    return api("POST", f"/api/cmd/{action_cmd}", body)


def seq(game_id, guid, moves):
    """Execute a sequence of moves (e.g. 'UUULLDR'). Returns list of obs dicts."""
    results = []
    for m in moves.upper():
        cmd = ACTION_MAP.get(m)
        if not cmd:
            continue
        obs = api("POST", f"/api/cmd/{cmd}", {"game_id": game_id, "guid": guid})
        results.append(obs)
        if obs.get("state") in ("WIN", "GAME_OVER"):
            break
    return results


def frame_to_grid(obs):
    """Extract the last frame from obs as a 2D list of ints."""
    frames = obs.get("frame", [[]])
    return frames[-1] if frames else []


def find_objects(grid, val):
    """Find all cells with a given value. Returns list of (row, col)."""
    positions = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v == val:
                positions.append((r, c))
    return positions


def find_blob(grid, val, min_size=3):
    """Find the bounding box of the largest connected region of val.
    Returns (min_row, min_col, max_row, max_col) or None."""
    positions = find_objects(grid, val)
    if len(positions) < min_size:
        return None
    return (min(r for r, c in positions), min(c for r, c in positions),
            max(r for r, c in positions), max(c for r, c in positions))


def diff_frames(grid_a, grid_b):
    """Compare two grids, return dict of {(row, col): (old_val, new_val)} for changed cells."""
    changes = {}
    for r in range(min(len(grid_a), len(grid_b))):
        for c in range(min(len(grid_a[r]), len(grid_b[r]))):
            if grid_a[r][c] != grid_b[r][c]:
                changes[(r, c)] = (grid_a[r][c], grid_b[r][c])
    return changes


def grid_summary(grid):
    """Return a compact summary: unique values and their counts."""
    counts = {}
    for row in grid:
        for v in row:
            counts[v] = counts.get(v, 0) + 1
    return dict(sorted(counts.items()))


def run_sequences(game_id, card_id, sequences):
    """Run multiple move sequences, resetting between each. Returns list of result dicts.
    Each result: {seq, levels, state, final_grid_summary, changes_per_step}."""
    results = []
    obs = reset(game_id, card_id)
    guid = obs["guid"]
    for s in sequences:
        obs = reset(game_id, card_id, guid)
        guid = obs["guid"]
        initial_grid = frame_to_grid(obs)
        prev_grid = initial_grid
        step_changes = []
        final_obs = obs
        for m in s.upper():
            cmd = ACTION_MAP.get(m)
            if not cmd:
                continue
            final_obs = api("POST", f"/api/cmd/{cmd}", {"game_id": game_id, "guid": guid})
            cur_grid = frame_to_grid(final_obs)
            n_changed = len(diff_frames(prev_grid, cur_grid))
            step_changes.append(n_changed)
            prev_grid = cur_grid
            if final_obs.get("state") in ("WIN", "GAME_OVER"):
                break
        results.append({
            "seq": s,
            "levels": final_obs.get("levels_completed", 0),
            "state": final_obs.get("state", "?"),
            "final_grid_summary": grid_summary(frame_to_grid(final_obs)),
            "changes_per_step": step_changes,
        })
    return results


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
        prev_frame = None  # will be set to last frame's 2D grid
        for i, m in enumerate(moves):
            act = action_map.get(m)
            if not act:
                print(f"Unknown move '{m}', use U/D/L/R/S/X")
                continue
            obs = api("POST", f"/api/cmd/{act}", {"game_id": game_id, "guid": guid})
            state = obs.get("state", "?")
            levels = obs.get("levels_completed", 0)
            # Find block (5 consecutive val=12 in a row) and cross (val=1)
            # Check ALL frames for block positions
            all_frames = obs.get("frame", [[]])
            frame_count = len(all_frames)
            # Collect block positions per frame
            per_frame_blocks = []
            for fi, fr in enumerate(all_frames):
                fb = []
                for y, row in enumerate(fr):
                    for x in range(len(row) - 4):
                        if all(row[x+j] == 12 for j in range(5)):
                            fb.append((y, x))
                            break
                per_frame_blocks.append(fb)
            f = all_frames[-1] if all_frames else []
            blocks = per_frame_blocks[-1] if per_frame_blocks else []
            cross_r, cross_c = -1, -1
            cells_changed = 0
            for y, row in enumerate(f):
                for x, val in enumerate(row):
                    if val == 1 and cross_r == -1:
                        cross_r, cross_c = y, x
                    if prev_frame and y < len(prev_frame) and x < len(prev_frame[y]):
                        if val != prev_frame[y][x]:
                            cells_changed += 1
            blk_r = blocks[0][0] if blocks else -1
            blk_c = blocks[0][1] if blocks else -1
            prev_frame = f
            dist = abs(blk_r - cross_r) + abs(blk_c - cross_c) if blk_r >= 0 and cross_r >= 0 else -1
            blk_str = " ".join(f"({r},{c})" for r,c in blocks)
            # Show per-frame block info if multiple frames
            frame_info = ""
            if frame_count > 1:
                frame_parts = []
                for fi, fb in enumerate(per_frame_blocks):
                    pos = fb[0] if fb else (-1,-1)
                    frame_parts.append(f"f{fi}=({pos[0]},{pos[1]})")
                frame_info = f" frames={frame_count} [{' '.join(frame_parts)}]"
            print(f"{i+1:3d}. {m} -> lvl={levels} blocks=[{blk_str}] cross=({cross_r},{cross_c}) chg={cells_changed}{frame_info}")
            # prev_frame already set above to f (the last frame's 2D grid)
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

    elif cmd == "run-experiment":
        # Run a generated experiment script
        # Usage: play.py run-experiment <script.py>
        script_path = sys.argv[2]
        import subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=300,
            env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)},
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

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
