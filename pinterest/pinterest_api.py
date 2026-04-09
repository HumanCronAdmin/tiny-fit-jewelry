"""Pinterest API v5 wrapper for TinyFit Jewelry auto-posting.

Uses image_base64 to upload local images directly — no public URL needed.
"""
import base64
import json
import time
from pathlib import Path

import keyring
import requests

SERVICE = "claude-workspace"
BASE_URL = "https://api.pinterest.com/v5"
SITE_BASE = "https://humancronadmin.github.io/tiny-fit-jewelry"

# Local image dir (for fallback reference)
IMAGES_DIR = Path(__file__).parent / "images"
BRAND_IMAGES_DIR = Path(__file__).parent / "brand_images"


def get_token():
    token = keyring.get_password(SERVICE, "PINTEREST_ACCESS_TOKEN")
    if not token:
        raise RuntimeError(
            "PINTEREST_ACCESS_TOKEN not found in keyring. "
            "Run pinterest_oauth.py first."
        )
    return token


def _headers():
    return {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }


def list_boards():
    """Get all boards for the authenticated user."""
    resp = requests.get(f"{BASE_URL}/boards", headers=_headers())
    resp.raise_for_status()
    boards = resp.json().get("items", [])
    return {b["name"]: b["id"] for b in boards}


def create_pin(board_id, title, description, link, image_path):
    """Create a pin via Pinterest API v5 using local image (base64).

    Args:
        board_id: Pinterest board ID (from list_boards())
        title: Pin title (max 100 chars)
        description: Pin description (max 500 chars)
        link: Destination URL when pin is clicked
        image_path: Local file path to the pin image (PNG/JPEG)
    Returns:
        dict with pin data on success, None on failure
    """
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"  [ERROR] Image not found: {img_path}")
        return None

    # Encode image as base64
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    ext = img_path.suffix.lower()
    content_type = "image/png" if ext == ".png" else "image/jpeg"

    payload = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
        "media_source": {
            "source_type": "image_base64",
            "data": img_b64,
            "content_type": content_type,
        },
    }

    resp = requests.post(f"{BASE_URL}/pins", headers=_headers(), json=payload)

    if resp.status_code == 201:
        data = resp.json()
        print(f"  [OK] Pin created: {title[:50]}")
        return data
    elif resp.status_code == 429:
        print(f"  [RATE LIMIT] Stopping. Try again later.")
        return None
    else:
        print(f"  [ERROR {resp.status_code}] {resp.text[:200]}")
        return None


def post_pin_from_queue_item(item, board_map):
    """Post a single pin from a queue item dict.

    Args:
        item: dict with keys: title, description, link, board, image_path
        board_map: dict mapping board name -> board ID
    Returns:
        True on success, False on failure
    """
    board_name = item["board"]
    board_id = board_map.get(board_name)
    if not board_id:
        print(f"  [ERROR] Board not found: {board_name}")
        print(f"  Available boards: {list(board_map.keys())}")
        return False

    result = create_pin(
        board_id=board_id,
        title=item["title"],
        description=item["description"],
        link=item["link"],
        image_path=item["image_path"],
    )
    return result is not None


if __name__ == "__main__":
    print("Fetching boards...")
    boards = list_boards()
    print(f"Found {len(boards)} boards:")
    for name, bid in boards.items():
        print(f"  {name}: {bid}")
