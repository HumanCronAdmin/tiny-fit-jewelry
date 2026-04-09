"""Generate pin images for queue items that don't have images yet.

Reads pin_queue.json, finds pins whose image_path doesn't exist,
generates a Pinterest-style image from the pin title/description.

Usage:
  python generate_missing_images.py         # Generate all missing
  python generate_missing_images.py --dry   # Preview only
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

QUEUE_FILE = Path(__file__).parent / "pin_queue.json"
GENERATED_IMAGES_DIR = Path(__file__).parent / "generated_images"

# Color schemes by board for visual variety
BOARD_COLORS = {
    "Ring Size 2-4 Guide": "#B76E79",
    "Bracelets for Thin Wrists": "#5B8C7A",
    "Japanese Jewelry Brands": "#8B5E6B",
    "Petite Style Tips": "#6B7B8E",
    "Jewelry for Tiny Fingers": "#957B5F",
}


def generate_pin_html(title, description, accent_color="#B76E79"):
    """Generate Pinterest-ready HTML pin (1000x1500)."""
    # Extract first sentence for subtitle
    subtitle = description.split(".")[0] + "." if "." in description else description[:120]
    if len(subtitle) > 140:
        subtitle = subtitle[:137] + "..."

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
.title {{ font-size: 48px; font-weight: 900; color: #1C1917; line-height: 1.2; margin-bottom: 30px; max-width: 840px; }}
.divider {{ width: 80px; height: 4px; background: {accent_color}; border-radius: 2px; margin: 24px 0; }}
.subtitle {{ font-size: 22px; color: #78716C; line-height: 1.6; max-width: 700px; }}
.badge {{ display: inline-block; background: {accent_color}; color: #fff; padding: 10px 24px; border-radius: 24px; font-weight: 700; font-size: 15px; margin-top: 30px; letter-spacing: 1px; }}
.footer {{ background: #1C1917; padding: 28px 60px; display: flex; justify-content: space-between; align-items: center; }}
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
    <div class="badge">VERIFIED SIZE GUIDE</div>
  </div>
  <div class="footer">
    <span class="footer-brand">TINYFIT JEWELRY</span>
    <span class="footer-url">humancronadmin.github.io/tiny-fit-jewelry</span>
  </div>
</div>
</body>
</html>"""


def main():
    dry_run = "--dry" in sys.argv
    GENERATED_IMAGES_DIR.mkdir(exist_ok=True)

    if not QUEUE_FILE.exists():
        print("No pin_queue.json found.")
        return

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    # Find pins with missing images
    missing = []
    for pin in queue:
        img_path = Path(pin.get("image_path", ""))
        if not img_path.exists():
            missing.append(pin)

    if not missing:
        print("All pin images exist. Nothing to generate.")
        return

    print(f"Found {len(missing)} pins with missing images.")

    if dry_run:
        for p in missing:
            print(f"  [MISSING] {p['id']}: {p['title'][:50]}")
        print(f"\n[DRY RUN] Would generate {len(missing)} images.")
        return

    # Generate images with Playwright
    print(f"Generating {len(missing)} images...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1800})

        for i, pin in enumerate(missing):
            img_path = Path(pin["image_path"])
            img_path.parent.mkdir(parents=True, exist_ok=True)

            color = BOARD_COLORS.get(pin.get("board", ""), "#B76E79")
            html = generate_pin_html(pin["title"], pin["description"], color)

            temp_html = img_path.parent / f"_temp_{img_path.stem}.html"
            temp_html.write_text(html, encoding="utf-8")

            page.goto(f"file:///{temp_html.resolve().as_posix()}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(800)

            pin_el = page.query_selector(".pin")
            if pin_el:
                pin_el.screenshot(path=str(img_path))
            else:
                page.screenshot(path=str(img_path))

            temp_html.unlink()

            size_kb = img_path.stat().st_size // 1024 if img_path.exists() else 0
            print(f"  [{i+1}/{len(missing)}] {pin['id']} ({size_kb}KB)")

        browser.close()

    print(f"\nDone. {len(missing)} images generated.")


if __name__ == "__main__":
    main()
