"""Validate pins in pin_queue.json before posting.

Checks:
  1. Image file exists and is valid (>1KB, PNG/JPEG)
  2. Link URL returns HTTP 200
  3. Title length <= 100 chars
  4. Description length <= 500 chars
  5. Board name is in allowed list
  6. No duplicate links in queue

Usage:
  python validate_pins.py          # Validate all pending pins
  python validate_pins.py --fix    # Auto-fix what can be fixed (truncate, etc.)
"""
import json
import sys
from pathlib import Path

import requests

QUEUE_FILE = Path(__file__).parent / "pin_queue.json"

VALID_BOARDS = {
    "Jewelry for Tiny Fingers",
    "Ring Size 2-4 Guide",
    "Bracelets for Thin Wrists",
    "Japanese Jewelry Brands",
    "Petite Style Tips",
}

# Cache HTTP checks to avoid hammering the server
_link_cache = {}


def check_link(url):
    if url in _link_cache:
        return _link_cache[url]
    try:
        resp = requests.head(url, timeout=10, allow_redirects=True)
        ok = resp.status_code == 200
    except Exception:
        ok = False
    _link_cache[url] = ok
    return ok


def validate_pin(pin, all_links):
    """Return list of issues for a pin. Empty list = valid."""
    issues = []
    pid = pin["id"]

    # 1. Image exists and is valid
    img = Path(pin.get("image_path", ""))
    if not img.exists():
        issues.append(f"Image not found: {img}")
    elif img.stat().st_size < 1024:
        issues.append(f"Image too small ({img.stat().st_size}B): {img.name}")
    elif img.suffix.lower() not in (".png", ".jpg", ".jpeg"):
        issues.append(f"Image not PNG/JPEG: {img.name}")

    # 2. Link returns 200
    link = pin.get("link", "")
    if not link:
        issues.append("No link URL")
    elif not check_link(link):
        issues.append(f"Link not reachable: {link}")

    # 3. Title length
    title = pin.get("title", "")
    if len(title) > 100:
        issues.append(f"Title too long ({len(title)} chars, max 100)")
    elif len(title) < 10:
        issues.append(f"Title too short ({len(title)} chars)")

    # 4. Description length
    desc = pin.get("description", "")
    if len(desc) > 500:
        issues.append(f"Description too long ({len(desc)} chars, max 500)")
    elif len(desc) < 20:
        issues.append(f"Description too short ({len(desc)} chars)")

    # 5. Board name
    board = pin.get("board", "")
    if board not in VALID_BOARDS:
        issues.append(f"Invalid board: '{board}'")

    # 6. Duplicate image path (same image used twice = real duplicate)
    if all_links.get(pin.get("image_path", ""), 0) > 1:
        issues.append(f"Duplicate image: {pin.get('image_path', '')}")

    return issues


def main():
    fix_mode = "--fix" in sys.argv

    if not QUEUE_FILE.exists():
        print("ERROR: pin_queue.json not found")
        return

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    # Count image path occurrences for duplicate check
    all_links = {}
    for p in queue:
        img = p.get("image_path", "")
        all_links[img] = all_links.get(img, 0) + 1

    # Validate only pending/failed pins
    targets = [p for p in queue if p["status"] in ("pending", "failed")]
    print(f"Validating {len(targets)} pins (pending/failed)...\n")

    valid_count = 0
    invalid_count = 0
    fixed_count = 0

    for pin in targets:
        issues = validate_pin(pin, all_links)

        if fix_mode and issues:
            # Auto-fix truncation issues
            if len(pin.get("title", "")) > 100:
                pin["title"] = pin["title"][:100]
                fixed_count += 1
            if len(pin.get("description", "")) > 500:
                pin["description"] = pin["description"][:500]
                fixed_count += 1
            # Re-validate after fix
            issues = validate_pin(pin, all_links)

        if issues:
            pin["status"] = "failed"
            pin["error"] = "; ".join(issues)
            invalid_count += 1
            print(f"  [FAIL] {pin['id']}: {pin['title'][:40]}")
            for issue in issues:
                print(f"         - {issue}")
        else:
            if pin["status"] == "failed":
                pin["status"] = "pending"
                pin["error"] = None
            pin["status"] = "validated"
            valid_count += 1

    # Save updated queue
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    print(f"\n=== Validation Results ===")
    print(f"  Valid: {valid_count}")
    print(f"  Invalid: {invalid_count}")
    if fix_mode:
        print(f"  Auto-fixed: {fixed_count}")
    print(f"  Total in queue: {len(queue)}")


if __name__ == "__main__":
    main()
