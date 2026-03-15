#!/usr/bin/env python3
"""ARC-AGI-3 API client and exploration library.

CLI: play.py games | scorecard-open | scorecard-close <id> | scorecard-get <id>
API: from play import start, reset, act, seq, frame_to_grid, find_objects, diff_frames, result
"""

import os, sys, json, time, atexit
from pathlib import Path
import httpx

BASE = "https://three.arcprize.org"
KEY = os.environ["ARC_API_KEY"]
COOKIE_FILE = Path(__file__).parent / ".arc_session.json"
SESSION = httpx.Client(timeout=60)
ACTION_MAP = {"U": "ACTION1", "D": "ACTION2", "L": "ACTION3", "R": "ACTION4",
              "S": "ACTION5", "X": "ACTION6"}

# Restore cookies from previous invocations
if COOKIE_FILE.exists():
    try:
        for name, value in json.loads(COOKIE_FILE.read_text()).items():
            if value and value != "_remove_":
                SESSION.cookies.set(name, value)
    except Exception:
        pass


# ── Core API ─────────────────────────────────────────────────────────

def api(method, path, body=None):
    """Call ARC API with retry on rate limit."""
    headers = {"X-API-Key": KEY, "Content-Type": "application/json"}
    for attempt in range(3):
        r = (SESSION.get if method == "GET" else SESSION.post)(
            f"{BASE}{path}", headers=headers, **({"json": body or {}} if method != "GET" else {}))
        if r.status_code == 429:
            time.sleep(0.1 * (attempt + 1))
            continue
        r.raise_for_status()
        data = r.json()
        # Persist cookies for cross-invocation state
        try:
            COOKIE_FILE.write_text(json.dumps({n: v for n, v in SESSION.cookies.items()}))
        except Exception:
            pass
        _status.update(body, data)
        return data
    r.raise_for_status()


# ── Game helpers ─────────────────────────────────────────────────────

def start(game_id):
    """Open a fresh scorecard + reset. Returns (card_id, obs)."""
    card = api("POST", "/api/scorecard/open", {})
    card_id = card.get("card_id") or card.get("id")
    return card_id, api("POST", "/api/cmd/RESET", {"game_id": game_id, "card_id": card_id})


def reset(game_id, card_id, guid=None):
    """Reset game. Returns obs dict."""
    return api("POST", "/api/cmd/RESET", {"game_id": game_id, "card_id": card_id, "guid": guid})


def act(action_cmd, game_id, guid, card_id=None, x=None, y=None):
    """Single action (U/D/L/R/S/X or ACTION1-6). Returns obs dict."""
    if action_cmd in ACTION_MAP:
        action_cmd = ACTION_MAP[action_cmd]
    body = {"game_id": game_id, "guid": guid}
    if card_id:
        body["card_id"] = card_id
    if x is not None and y is not None:
        body["x"], body["y"] = int(x), int(y)
    return api("POST", f"/api/cmd/{action_cmd}", body)


def seq(game_id, guid, moves, card_id=None):
    """Execute a move string (e.g. 'UUULLDR'). Returns final obs only."""
    obs = None
    for m in moves.upper():
        cmd = ACTION_MAP.get(m)
        if not cmd:
            continue
        body = {"game_id": game_id, "guid": guid}
        if card_id:
            body["card_id"] = card_id
        obs = api("POST", f"/api/cmd/{cmd}", body)
        if obs.get("state") in ("WIN", "GAME_OVER"):
            break
    return obs


def frame_to_grid(obs):
    """Extract the last frame from obs as a 2D list."""
    frames = obs.get("frame", [[]])
    return frames[-1] if frames else []


def find_objects(grid, val):
    """Find all (row, col) with given value."""
    return [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == val]


def find_blob(grid, val, min_size=3):
    """Bounding box of largest region of val. Returns (r0, c0, r1, c1) or None."""
    pts = find_objects(grid, val)
    if len(pts) < min_size:
        return None
    return (min(r for r, c in pts), min(c for r, c in pts),
            max(r for r, c in pts), max(c for r, c in pts))


def diff_frames(grid_a, grid_b):
    """Dict of {(row, col): (old, new)} for changed cells."""
    return {(r, c): (grid_a[r][c], grid_b[r][c])
            for r in range(min(len(grid_a), len(grid_b)))
            for c in range(min(len(grid_a[r]), len(grid_b[r])))
            if grid_a[r][c] != grid_b[r][c]}


def grid_summary(grid):
    """Value counts as sorted dict."""
    counts = {}
    for row in grid:
        for v in row:
            counts[v] = counts.get(v, 0) + 1
    return dict(sorted(counts.items()))


def render(frame_data):
    """Compact text render of frame. Skips empty rows."""
    lines = []
    for fi, frame in enumerate(frame_data):
        if len(frame_data) > 1:
            lines.append(f"--- Frame {fi} ---")
        for y, row in enumerate(frame):
            if any(v != 0 for v in row):
                lines.append(f"{y:02d}|{''.join('.' if v == 0 else hex(v)[2:] for v in row)}")
    return "\n".join(lines) or "(empty)"


def result(msg):
    """Set final learning for this experiment. Shows on dashboard."""
    print(msg)
    _status.result_msg = msg


# ── Custom helpers (add your own below) ───────────────────────────────


def answer_pattern(grid):
    """Read the 3x3 answer pattern from the lower-left box (2x scale at rows 55-60, cols 3-8)."""
    pattern = []
    for rp in [(55, 56), (57, 58), (59, 60)]:
        row = []
        for cp in [(3, 4), (5, 6), (7, 8)]:
            vals = [grid[r][c] for r in rp for c in cp]
            row.append('9' if all(v == 9 for v in vals) else '.')
        pattern.append(''.join(row))
    return '/'.join(pattern)


def target_pattern(grid):
    """Find and read the 3x3 target pattern from a reference box (5-fill with 9-pattern)."""
    # Find the 9s that are surrounded by 5s (the reference box interior)
    nines = find_objects(grid, 9)
    # Exclude 9s in the answer box (rows 53-62) and in the movable block
    twelves = set((r, c) for r, c in find_objects(grid, 12))
    ref_nines = []
    for r, c in nines:
        if r >= 53:
            continue
        # Check if any adjacent 12 (part of movable block)
        if (r, c) in twelves or (r-1, c) in twelves or (r+1, c) in twelves:
            continue
        # Check if surrounded by 5s (reference box)
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        if any(0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 5
               for nr, nc in neighbors):
            ref_nines.append((r, c))
    if not ref_nines:
        return None
    # Find bounding box of the 3x3 pattern
    min_r, max_r = min(r for r, c in ref_nines), max(r for r, c in ref_nines)
    min_c, max_c = min(c for r, c in ref_nines), max(c for r, c in ref_nines)
    pattern = []
    for r in range(min_r, max_r + 1):
        row = []
        for c in range(min_c, max_c + 1):
            row.append('9' if grid[r][c] == 9 else '.')
        pattern.append(''.join(row))
    return '/'.join(pattern)


def level_status(obs):
    """Print a compact summary of current level state."""
    grid = frame_to_grid(obs)
    print(f"State: {obs.get('state')}  Levels: {obs.get('levels_completed')}/{obs.get('win_levels')}")
    # Block position
    c_pos = find_objects(grid, 12)
    if c_pos:
        print(f"Block c(12): rows {min(r for r,c in c_pos)}-{max(r for r,c in c_pos)}, "
              f"cols {min(c for r,c in c_pos)}-{max(c for r,c in c_pos)}")
    # Marker position
    zeros = [(r, c) for r, c in find_objects(grid, 0) if 5 <= r <= 54 and 5 <= c <= 54]
    ones = find_objects(grid, 1)
    marker_cells = zeros + ones
    # Filter to workspace markers (not box borders)
    if marker_cells:
        print(f"Marker 0s: {zeros}  1s: {ones}")
    # Answer vs target
    ans = answer_pattern(grid)
    tgt = target_pattern(grid)
    match = "MATCH" if ans == tgt else "MISMATCH"
    print(f"Answer: {ans}  Target: {tgt}  [{match}]")
    # Resources
    b_count = len([(r, c) for r, c in find_objects(grid, 11) if r >= 60])
    print(f"Resources: {b_count} b-cells ({b_count // 2} moves left)")


# ── Dashboard status tracking (do not edit) ──────────────────────────

STATUS_DIR = Path(__file__).parent / "status"


class _Status:
    """Writes experiment state to status/<guid>.json for the dashboard."""

    def __init__(self):
        self.guid = self.game_id = self.state = self.result_msg = None
        self.levels = 0
        self._title = None
        raw = sys.argv[0] if sys.argv[0] else ""
        self.experiment = Path(raw).name if raw and not raw.startswith("-") else "interactive"

    @property
    def title(self):
        if self._title is None:
            try:
                line = Path(sys.argv[0]).resolve().read_text().split("\n", 1)[0]
                self._title = line.lstrip("# ").strip() if line.startswith("#") and not line.startswith("#!") else ""
            except Exception:
                self._title = ""
        return self._title or self.experiment

    def update(self, body, data):
        try:
            guid = data.get("guid")
            if not guid or "frame" not in data:
                return
            if guid != self.guid:
                self._finalize()
            self.guid, self.game_id = guid, (body or {}).get("game_id")
            self.state = data.get("state")
            self.levels = data.get("levels_completed", 0)
            frames = data.get("frame", [[]])
            frame = frames[-1] if frames else []
            self._append_frame(frame)
            self._write_meta()
        except Exception:
            pass

    def _append_frame(self, frame):
        STATUS_DIR.mkdir(exist_ok=True)
        with open(STATUS_DIR / f"{self.guid}.frames.jsonl", "a") as f:
            f.write(json.dumps(frame) + "\n")

    def _write_meta(self):
        STATUS_DIR.mkdir(exist_ok=True)
        (STATUS_DIR / f"{self.guid}.json").write_text(json.dumps({
            "game_id": self.game_id, "guid": self.guid,
            "state": self.state, "levels_completed": self.levels,
            "experiment": self.experiment, "title": self.title,
            "result": self.result_msg, "updated_at": time.time(),
        }))

    def _finalize(self):
        try:
            if not self.guid:
                return
            path = STATUS_DIR / f"{self.guid}.json"
            if not path.exists():
                return
            s = json.loads(path.read_text())
            if s.get("state") not in ("WIN", "GAME_OVER"):
                s["state"] = "DONE"
            s["result"] = self.result_msg
            s["updated_at"] = time.time()
            path.write_text(json.dumps(s))
        except Exception:
            pass


_status = _Status()
atexit.register(_status._finalize)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "games":
        for g in api("GET", "/api/games"):
            gid = g["game_id"] if isinstance(g, dict) else g
            print(f"{gid}  {g.get('title', '') if isinstance(g, dict) else ''}")
    elif cmd == "scorecard-open":
        print(json.dumps(api("POST", "/api/scorecard/open", {})))
    elif cmd == "scorecard-close":
        print(json.dumps(api("POST", "/api/scorecard/close", {"card_id": sys.argv[2]}), indent=2))
    elif cmd == "scorecard-get":
        print(json.dumps(api("GET", f"/api/scorecard/{sys.argv[2]}"), indent=2))
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
