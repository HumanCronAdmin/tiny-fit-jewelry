"""Pinterest auto-posting scheduler.

Reads pin_queue.json, posts up to DAILY_LIMIT pending pins via API,
updates queue status. Designed for daily Task Scheduler execution.

Usage:
  python pinterest_scheduler.py          # Post up to 5 pins
  python pinterest_scheduler.py --dry    # Preview without posting
  python pinterest_scheduler.py --limit 3  # Post up to 3 pins
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))
from pinterest_api import list_boards, post_pin_from_queue_item

QUEUE_FILE = Path(__file__).parent / "pin_queue.json"
LOG_FILE = Path(__file__).parent / "post_log.txt"
DAILY_LIMIT = 5
PIN_INTERVAL_SEC = 30  # seconds between pins (rate limit safety)


def load_queue():
    if not QUEUE_FILE.exists():
        print("ERROR: pin_queue.json not found. Run generate_pin_queue.py first.")
        sys.exit(1)
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def log_post(pin_id, title, success):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    status = "OK" if success else "FAIL"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] [{status}] {pin_id}: {title[:60]}\n")


def get_pending_pins(queue, limit):
    """Get next batch of validated pins, rotating boards for variety."""
    pending = [p for p in queue if p["status"] == "validated"]
    if not pending:
        return []

    # Group by board, round-robin select for variety
    by_board = {}
    for p in pending:
        by_board.setdefault(p["board"], []).append(p)

    selected = []
    board_names = list(by_board.keys())
    idx = 0
    while len(selected) < limit and any(by_board.values()):
        board = board_names[idx % len(board_names)]
        if by_board[board]:
            selected.append(by_board[board].pop(0))
        idx += 1
        # Remove empty boards
        board_names = [b for b in board_names if by_board.get(b)]
        if not board_names:
            break

    return selected


def main():
    dry_run = "--dry" in sys.argv
    limit = DAILY_LIMIT
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    queue = load_queue()
    total = len(queue)
    posted = sum(1 for p in queue if p["status"] == "posted")
    pending = sum(1 for p in queue if p["status"] == "pending")
    failed = sum(1 for p in queue if p["status"] == "failed")

    print(f"=== Pinterest Scheduler ===")
    print(f"Queue: {total} total | {pending} pending | {posted} posted | {failed} failed")
    print(f"Limit: {limit} pins this run")
    print()

    batch = get_pending_pins(queue, limit)
    if not batch:
        print("No pending pins. Queue is empty or all posted.")
        return

    if dry_run:
        print("[DRY RUN] Would post:")
        for p in batch:
            print(f"  - [{p['board']}] {p['title'][:60]}")
        return

    # Fetch board map from API
    print("Fetching boards from Pinterest API...")
    try:
        board_map = list_boards()
    except Exception as e:
        print(f"ERROR: Failed to fetch boards: {e}")
        return

    if not board_map:
        print("ERROR: No boards found. Check your Pinterest account.")
        return

    print(f"Found {len(board_map)} boards: {list(board_map.keys())}")
    print()

    # Post pins
    ok_count = 0
    fail_count = 0
    for i, pin in enumerate(batch):
        print(f"[{i+1}/{len(batch)}] {pin['title'][:50]}...")

        # Find this pin in the queue and update
        queue_item = next((p for p in queue if p["id"] == pin["id"]), None)
        if not queue_item:
            continue

        success = post_pin_from_queue_item(pin, board_map)
        now = datetime.now(timezone.utc).isoformat()

        if success:
            queue_item["status"] = "posted"
            queue_item["posted_at"] = now
            ok_count += 1
        else:
            queue_item["status"] = "failed"
            queue_item["error"] = now
            fail_count += 1
            # Rate limit hit - stop immediately
            if "RATE LIMIT" in str(queue_item.get("error", "")):
                print("Rate limit detected. Stopping.")
                break

        log_post(pin["id"], pin["title"], success)
        save_queue(queue)  # Save after each pin in case of crash

        # Wait between pins
        if i < len(batch) - 1:
            print(f"  Waiting {PIN_INTERVAL_SEC}s...")
            time.sleep(PIN_INTERVAL_SEC)

    print()
    print(f"=== Done: {ok_count} posted, {fail_count} failed ===")
    remaining = sum(1 for p in queue if p["status"] == "pending")
    print(f"Remaining in queue: {remaining}")


if __name__ == "__main__":
    main()
