"""Generate pin_queue.json from existing pin data and brand data.

Run once to create the queue file. The scheduler reads from this queue.
New pins can be added by re-running with --append flag.
"""
import json
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
QUEUE_FILE = Path(__file__).parent / "pin_queue.json"
SITE_BASE = "https://humancronadmin.github.io/tiny-fit-jewelry"
PIN_IMAGES_DIR = Path(__file__).parent / "images"
BRAND_IMAGES_DIR = Path(__file__).parent / "brand_images"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# 5 infographic pins (hardcoded - matches existing images)
INFOGRAPHIC_PINS = [
    {
        "id": "info-01",
        "title": "Ring Size Chart: US vs Japanese vs EU Conversion for Sizes 2-4",
        "description": "Stop guessing your ring size across countries. This chart covers US 2-4 with Japanese, European, and UK equivalents plus exact mm measurements. Save this before your next jewelry purchase. #ringsize #sizeconversion #petitejewelry #ringguide #tinyfitjewelry",
        "link": f"{SITE_BASE}/rings.html",
        "board": "Ring Size 2-4 Guide",
        "image_path": str(PIN_IMAGES_DIR / "01_ring_size_conversion.png"),
    },
    {
        "id": "info-02",
        "title": "6 Brands That Actually Carry Ring Size 2 (Verified 2026)",
        "description": "Ring size 2 is the hardest to find. We verified every brand on this list. Agete, 4C, Nojess, Star Jewelry, Bloom from Japan. Automic Gold from USA. No children's jewelry. Real adult designs. #ringsize2 #smallrings #petitejewelry #agete #tinyfitjewelry",
        "link": f"{SITE_BASE}/size/ring-size-2.html",
        "board": "Ring Size 2-4 Guide",
        "image_path": str(PIN_IMAGES_DIR / "02_brands_ring_size_2.png"),
    },
    {
        "id": "info-03",
        "title": "Bracelet Math: The Formula for Wrists Under 14cm",
        "description": "Your wrist + 1.5cm = perfect bracelet length. Standard bracelets are 16-18cm but your wrist is under 14cm. This simple formula ensures your next bracelet actually stays on. #thinwrist #smallwristbracelet #petitebracelet #braceletfit #tinyfitjewelry",
        "link": f"{SITE_BASE}/bracelets.html",
        "board": "Bracelets for Thin Wrists",
        "image_path": str(PIN_IMAGES_DIR / "03_bracelet_math.png"),
    },
    {
        "id": "info-04",
        "title": "5 Ring Styles That Look Best on Petite Fingers (Size 2-4)",
        "description": "Not all ring styles work at size 2-4. Thin bands, small solitaires, and stackable rings flatter petite fingers. Wide bands and chunky cocktail rings overwhelm them. Here is what to choose and what to avoid. #petiterings #ringstyle #smallfingers #stackablerings #tinyfitjewelry",
        "link": f"{SITE_BASE}/rings.html",
        "board": "Petite Style Tips",
        "image_path": str(PIN_IMAGES_DIR / "04_ring_styles_petite.png"),
    },
    {
        "id": "info-05",
        "title": "Why Japanese Jewelry Brands Are Perfect for Petite Fingers",
        "description": "Japanese brands start where US brands stop. Agete, 4C, Nojess, Star Jewelry, Vendome Aoyama, Bloom, and Take-Up all carry rings from US size 1.5. Elegant adult designs, not children's jewelry. #japanesejewelry #petiterings #agete #nojess #tinyfitjewelry",
        "link": f"{SITE_BASE}/size/japanese-brands.html",
        "board": "Japanese Jewelry Brands",
        "image_path": str(PIN_IMAGES_DIR / "05_japanese_brand_advantage.png"),
    },
]


def generate_brand_pins():
    """Generate pin entries from brands.json."""
    brands_file = DATA_DIR / "brands.json"
    if not brands_file.exists():
        print(f"WARNING: {brands_file} not found, skipping brand pins")
        return []

    with open(brands_file, "r", encoding="utf-8") as f:
        brands = json.load(f)

    pins = []
    for brand in brands:
        name = brand["brand"]
        s = slug(name)
        country = brand["country"]
        min_ring = brand.get("min_ring_size_us") or "N/A"
        min_bracelet = brand.get("min_bracelet_cm") or "N/A"
        price_min = brand.get("price_min", "?")
        price_max = brand.get("price_max", "?")
        style = brand.get("style", "")

        size_info = ""
        if min_ring != "N/A":
            size_info += f"Rings from US size {min_ring}. "
        if min_bracelet != "N/A":
            size_info += f"Bracelets from {min_bracelet}cm. "

        title = f"{name}: Petite Jewelry Size Guide (Verified 2026)"
        desc = (
            f"{name} from {country}. {size_info}"
            f"${price_min}-${price_max}. {style.capitalize()} designs. "
            f"We verified their actual size range so you don't have to guess. "
            f"#petitejewelry #smallrings #tinyfitjewelry #ringsize #petitewomen"
        )

        if min_ring != "N/A" and min_ring <= 2:
            board = "Ring Size 2-4 Guide"
        elif country == "Japan":
            board = "Japanese Jewelry Brands"
        else:
            board = "Jewelry for Tiny Fingers"

        pins.append({
            "id": f"brand-{s}",
            "title": title[:100],
            "description": desc[:500],
            "link": f"{SITE_BASE}/brands/{s}.html",
            "board": board,
            "image_path": str(BRAND_IMAGES_DIR / f"brand_{s}.png"),
        })

    return pins


def main():
    append_mode = "--append" in sys.argv

    if append_mode and QUEUE_FILE.exists():
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_ids = {p["id"] for p in existing}
    else:
        existing = []
        existing_ids = set()

    # Generate all pins
    all_pins = INFOGRAPHIC_PINS + generate_brand_pins()

    # Add status fields to new pins
    new_count = 0
    for pin in all_pins:
        if pin["id"] not in existing_ids:
            pin["status"] = "pending"
            pin["posted_at"] = None
            pin["error"] = None
            existing.append(pin)
            new_count += 1

    # Save
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    total_pending = sum(1 for p in existing if p["status"] == "pending")
    total_posted = sum(1 for p in existing if p["status"] == "posted")

    print(f"Queue: {QUEUE_FILE}")
    print(f"  Total: {len(existing)} pins")
    print(f"  New: {new_count}")
    print(f"  Pending: {total_pending}")
    print(f"  Posted: {total_posted}")


if __name__ == "__main__":
    main()
