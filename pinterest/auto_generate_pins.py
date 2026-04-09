"""Auto-detect new site content and generate pins + images.

Scans the TinyFit Jewelry site for pages that don't have pins yet,
generates pin content (title, description, board), creates images,
and adds them to pin_queue.json as "pending".

Sources:
  - brands/*.html     -> brand pins (uses generate_brand_pins.py logic)
  - guides/*.html     -> guide pins (new)
  - size/*.html       -> size guide pins (new)
  - rings.html, bracelets.html, etc. -> topic pins (new)

Usage:
  python auto_generate_pins.py           # Detect + generate new pins
  python auto_generate_pins.py --dry     # Preview only, no changes
"""
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE_DIR = Path(__file__).parent.parent
DATA_DIR = SITE_DIR / "data"
QUEUE_FILE = Path(__file__).parent / "pin_queue.json"
GENERATED_IMAGES_DIR = Path(__file__).parent / "generated_images"
SITE_BASE = "https://humancronadmin.github.io/tiny-fit-jewelry"

# Pages to skip (not pin-worthy)
SKIP_PAGES = {"index.html", "about.html", "privacy.html", "database.html", "ring-sizer.html"}

# Board assignment rules
BOARD_RULES = {
    "guides": "Petite Style Tips",
    "size": "Ring Size 2-4 Guide",
    "brands": None,  # determined by brand data
}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def extract_page_title(html_path):
    """Extract <title> or <h1> from an HTML file."""
    content = html_path.read_text(encoding="utf-8")
    # Try <title>
    m = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    if m:
        title = m.group(1).strip()
        # Remove " | TinyFit Jewelry" suffix
        title = re.sub(r"\s*[\|–—-]\s*TinyFit\s*Jewelry.*$", "", title).strip()
        if title:
            return title
    # Try <h1>
    m = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return html_path.stem.replace("-", " ").title()


def extract_meta_description(html_path):
    """Extract meta description from HTML."""
    content = html_path.read_text(encoding="utf-8")
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""


def determine_board(page_dir, page_stem, title):
    """Pick the best board for a page."""
    if page_dir == "guides":
        if "bracelet" in title.lower() or "wrist" in title.lower():
            return "Bracelets for Thin Wrists"
        if "necklace" in title.lower():
            return "Petite Style Tips"
        return "Petite Style Tips"
    if page_dir == "size":
        if "wrist" in page_stem or "bracelet" in page_stem:
            return "Bracelets for Thin Wrists"
        if "japanese" in page_stem:
            return "Japanese Jewelry Brands"
        return "Ring Size 2-4 Guide"
    # Root pages
    if "bracelet" in page_stem:
        return "Bracelets for Thin Wrists"
    if "ring" in page_stem:
        return "Ring Size 2-4 Guide"
    return "Jewelry for Tiny Fingers"


def generate_description(title, meta_desc, page_dir):
    """Generate a Pinterest-optimized description."""
    base = meta_desc if meta_desc else title
    # Add hashtags based on content
    tags = "#petitejewelry #tinyfitjewelry"
    if "ring" in base.lower():
        tags += " #petiterings #smallrings #ringsize"
    if "bracelet" in base.lower() or "wrist" in base.lower():
        tags += " #thinwrist #petitebracelet #smallwrist"
    if "japan" in base.lower():
        tags += " #japanesejewelry"
    if "engag" in base.lower():
        tags += " #engagementring"
    if "stack" in base.lower():
        tags += " #stackablerings"
    if "necklace" in base.lower():
        tags += " #petitenecklace"
    if "under" in base.lower() or "budget" in base.lower():
        tags += " #budgetjewelry #affordable"

    desc = f"{base} {tags}"
    return desc[:500]


def generate_pin_image_html(title, subtitle, accent_color="#B76E79"):
    """Generate HTML for a Pinterest pin image (1000x1500)."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; background: #f5f0ee; display: flex; justify-content: center; }}
.pin {{ width: 1000px; height: 1500px; background: #fff; position: relative; overflow: hidden; display: flex; flex-direction: column; }}
.top-bar {{ height: 8px; background: {accent_color}; }}
.content {{ flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 80px 80px; text-align: center; }}
.icon {{ font-size: 64px; margin-bottom: 40px; }}
.title {{ font-size: 52px; font-weight: 900; color: #1C1917; line-height: 1.2; margin-bottom: 30px; max-width: 800px; }}
.subtitle {{ font-size: 22px; color: #78716C; line-height: 1.6; max-width: 700px; }}
.divider {{ width: 80px; height: 4px; background: {accent_color}; border-radius: 2px; margin: 30px 0; }}
.footer {{ background: #1C1917; padding: 30px 60px; display: flex; justify-content: space-between; align-items: center; }}
.footer-brand {{ color: {accent_color}; font-weight: 700; font-size: 16px; letter-spacing: 2px; }}
.footer-url {{ color: rgba(255,255,255,0.5); font-size: 13px; }}
</style>
</head>
<body>
<div class="pin">
  <div class="top-bar"></div>
  <div class="content">
    <div class="title">{title}</div>
    <div class="divider"></div>
    <div class="subtitle">{subtitle}</div>
  </div>
  <div class="footer">
    <span class="footer-brand">TINYFIT JEWELRY</span>
    <span class="footer-url">humancronadmin.github.io/tiny-fit-jewelry</span>
  </div>
</div>
</body>
</html>"""


def scan_new_pages(existing_ids):
    """Find site pages that don't have pins in the queue yet."""
    new_pages = []

    # Scan directories
    for page_dir in ["guides", "size"]:
        dir_path = SITE_DIR / page_dir
        if not dir_path.exists():
            continue
        for html_file in sorted(dir_path.glob("*.html")):
            pin_id = f"{page_dir}-{html_file.stem}"
            if pin_id not in existing_ids:
                new_pages.append((page_dir, html_file, pin_id))

    # Scan root pages
    for html_file in sorted(SITE_DIR.glob("*.html")):
        if html_file.name in SKIP_PAGES:
            continue
        pin_id = f"page-{html_file.stem}"
        if pin_id not in existing_ids:
            new_pages.append(("root", html_file, pin_id))

    return new_pages


def create_pin_image(playwright_page, title, subtitle, output_path):
    """Render pin image HTML and screenshot it."""
    html = generate_pin_image_html(title, subtitle)
    temp = output_path.parent / f"_temp_{output_path.stem}.html"
    temp.write_text(html, encoding="utf-8")

    playwright_page.goto(f"file:///{temp.resolve().as_posix()}")
    playwright_page.wait_for_load_state("networkidle")
    playwright_page.wait_for_timeout(1000)

    pin_el = playwright_page.query_selector(".pin")
    if pin_el:
        pin_el.screenshot(path=str(output_path))
    else:
        playwright_page.screenshot(path=str(output_path))

    temp.unlink()
    return output_path.exists()


def main():
    dry_run = "--dry" in sys.argv
    GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

    # Load existing queue
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            queue = json.load(f)
    else:
        queue = []

    existing_ids = {p["id"] for p in queue}

    # Find new pages
    new_pages = scan_new_pages(existing_ids)

    if not new_pages:
        print("No new pages found. Queue is up to date.")
        return

    print(f"Found {len(new_pages)} new pages to create pins for:\n")

    new_pins = []
    for page_dir, html_file, pin_id in new_pages:
        title = extract_page_title(html_file)
        meta_desc = extract_meta_description(html_file)
        board = determine_board(page_dir, html_file.stem, title)
        description = generate_description(title, meta_desc, page_dir)

        # Build link URL
        if page_dir == "root":
            link = f"{SITE_BASE}/{html_file.name}"
        else:
            link = f"{SITE_BASE}/{page_dir}/{html_file.name}"

        image_path = GENERATED_IMAGES_DIR / f"{pin_id}.png"

        # Subtitle for image generation
        subtitle = meta_desc[:120] if meta_desc else "Verified size guide for petite women"

        pin = {
            "id": pin_id,
            "title": title[:100],
            "description": description,
            "link": link,
            "board": board,
            "image_path": str(image_path),
            "status": "pending",
            "posted_at": None,
            "error": None,
            "_subtitle": subtitle,  # temp, used for image gen
        }
        new_pins.append(pin)
        print(f"  [{pin_id}] {title[:50]}")
        print(f"    Board: {board} | Link: {link}")

    if dry_run:
        print(f"\n[DRY RUN] Would create {len(new_pins)} pins. No changes made.")
        return

    # Generate images
    print(f"\nGenerating {len(new_pins)} pin images...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1800})

        for i, pin in enumerate(new_pins):
            ok = create_pin_image(page, pin["title"], pin["_subtitle"], Path(pin["image_path"]))
            status = "OK" if ok else "FAIL"
            size = Path(pin["image_path"]).stat().st_size // 1024 if ok else 0
            print(f"  [{i+1}/{len(new_pins)}] {status} {pin['id']} ({size}KB)")

        browser.close()

    # Remove temp subtitle field and add to queue
    for pin in new_pins:
        del pin["_subtitle"]
        queue.append(pin)

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    total = len(queue)
    pending = sum(1 for p in queue if p["status"] == "pending")
    print(f"\n=== Done ===")
    print(f"  New pins created: {len(new_pins)}")
    print(f"  Total in queue: {total} ({pending} pending)")
    print(f"\nNext: run validate_pins.py to check, then pinterest_scheduler.py to post.")


if __name__ == "__main__":
    main()
