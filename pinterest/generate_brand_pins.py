"""Generate Pinterest pin images for each brand from brands.json."""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_FILE = Path(__file__).parent.parent / "data" / "brands.json"
OUTPUT_DIR = Path(__file__).parent / "brand_images"
OUTPUT_DIR.mkdir(exist_ok=True)

# Pin descriptions output
PIN_DESC_FILE = Path(__file__).parent / "brand_pin_descriptions.txt"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    brands = json.load(f)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def generate_pin_html(brand):
    """Generate a single pin HTML for a brand."""
    name = brand["brand"]
    country = brand["country"]
    categories = ", ".join(brand["category"])
    min_ring = brand.get("min_ring_size_us") or "N/A"
    min_bracelet = brand.get("min_bracelet_cm") or "N/A"
    price_min = brand.get("price_min", "?")
    price_max = brand.get("price_max", "?")
    materials = ", ".join(brand.get("materials", []))
    style = brand.get("style", "")
    note = brand.get("note", "")
    adjustable = "Yes" if brand.get("adjustable") else "No"
    intl = "Yes" if brand.get("intl_shipping") else "Japan only"

    # Determine badge
    if min_ring != "N/A" and min_ring <= 2:
        badge = f"Rings from size {min_ring}"
        badge_color = "#B76E79"
    elif min_ring != "N/A":
        badge = f"Rings from size {min_ring}"
        badge_color = "#8B7355"
    else:
        badge = f"Bracelets from {min_bracelet}cm"
        badge_color = "#5B8C7A"

    # Build feature list
    features = []
    if min_ring != "N/A":
        features.append(f"<div class='feat'><span class='feat-label'>Min Ring Size</span><span class='feat-val'>US {min_ring}</span></div>")
    if min_bracelet != "N/A":
        features.append(f"<div class='feat'><span class='feat-label'>Min Bracelet</span><span class='feat-val'>{min_bracelet}cm</span></div>")
    features.append(f"<div class='feat'><span class='feat-label'>Price Range</span><span class='feat-val'>${price_min}-${price_max}</span></div>")
    features.append(f"<div class='feat'><span class='feat-label'>Materials</span><span class='feat-val'>{materials}</span></div>")
    features.append(f"<div class='feat'><span class='feat-label'>Adjustable</span><span class='feat-val'>{adjustable}</span></div>")
    features.append(f"<div class='feat'><span class='feat-label'>Intl Shipping</span><span class='feat-val'>{intl}</span></div>")
    features_html = "\n".join(features)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; background: #f5f0ee; display: flex; justify-content: center; padding: 0; }}
.pin {{ width: 1000px; height: 1500px; background: #fff; position: relative; overflow: hidden; }}
.header {{ background: linear-gradient(135deg, #B76E79 0%, #8B5E6B 100%); padding: 60px 60px 50px; color: #fff; }}
.brand-label {{ font-size: 14px; letter-spacing: 3px; text-transform: uppercase; opacity: 0.8; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }}
.brand-label::before {{ content: ''; display: inline-block; width: 4px; height: 20px; background: #fff; border-radius: 2px; }}
.brand-name {{ font-size: 52px; font-weight: 900; line-height: 1.1; margin-bottom: 16px; }}
.brand-meta {{ font-size: 18px; opacity: 0.85; }}
.badge {{ display: inline-block; background: rgba(255,255,255,0.25); padding: 8px 20px; border-radius: 20px; font-weight: 700; font-size: 16px; margin-top: 20px; }}
.body {{ padding: 50px 60px; }}
.section-title {{ font-size: 15px; font-weight: 700; color: #B76E79; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 24px; }}
.feat {{ display: flex; justify-content: space-between; align-items: center; padding: 18px 0; border-bottom: 1px solid #F0EEEE; }}
.feat-label {{ font-size: 17px; color: #78716C; font-weight: 500; }}
.feat-val {{ font-size: 17px; color: #1C1917; font-weight: 700; }}
.note {{ margin-top: 30px; padding: 20px 24px; background: #FAF5F6; border-radius: 12px; font-size: 15px; color: #44403C; line-height: 1.6; border-left: 4px solid #B76E79; }}
.footer {{ position: absolute; bottom: 0; left: 0; right: 0; background: #1C1917; padding: 24px 60px; display: flex; justify-content: space-between; align-items: center; }}
.footer-cta {{ color: #B76E79; font-weight: 700; font-size: 15px; text-transform: uppercase; letter-spacing: 1px; }}
.footer-url {{ color: rgba(255,255,255,0.5); font-size: 13px; }}
</style>
</head>
<body>
<div class="pin">
  <div class="header">
    <div class="brand-label">TINYFIT JEWELRY</div>
    <div class="brand-name">{name}</div>
    <div class="brand-meta">{country} &middot; {categories} &middot; {style}</div>
    <div class="badge">{badge}</div>
  </div>
  <div class="body">
    <div class="section-title">Size &amp; Price Details</div>
    {features_html}
    <div class="note">{note}</div>
  </div>
  <div class="footer">
    <span class="footer-cta">View Full Size Guide &rarr;</span>
    <span class="footer-url">humancronadmin.github.io/tiny-fit-jewelry</span>
  </div>
</div>
</body>
</html>"""


def generate_pin_description(brand):
    """Generate Pinterest pin description for a brand."""
    name = brand["brand"]
    country = brand["country"]
    min_ring = brand.get("min_ring_size_us") or "N/A"
    min_bracelet = brand.get("min_bracelet_cm") or "N/A"
    price_min = brand.get("price_min", "?")
    price_max = brand.get("price_max", "?")
    style = brand.get("style", "")
    s = slug(name)

    size_info = ""
    if min_ring != "N/A":
        size_info += f"Rings from US size {min_ring}. "
    if min_bracelet != "N/A":
        size_info += f"Bracelets from {min_bracelet}cm. "

    title = f"{name}: Petite Jewelry Size Guide (Verified 2026)"
    desc = f"{name} from {country}. {size_info}${price_min}-${price_max}. {style.capitalize()} designs. We verified their actual size range so you don't have to guess. #petitejewelry #{s.replace('-','')} #smallrings #tinyfitjewelry #ringsize"
    link = f"https://humancronadmin.github.io/tiny-fit-jewelry/brands/{s}.html"

    # Determine board
    if min_ring != "N/A" and min_ring <= 2:
        board = "Ring Size 2-4 Guide"
    elif country == "Japan":
        board = "Japanese Jewelry Brands"
    else:
        board = "Jewelry for Tiny Fingers"

    return {
        "title": title,
        "description": desc[:500],
        "link": link,
        "board": board,
        "image": f"brand_{s}.png",
    }


def main():
    print(f"Generating pins for {len(brands)} brands...")

    # Generate HTML files and screenshot them
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1800})

        pin_descs = []

        for i, brand in enumerate(brands):
            name = brand["brand"]
            s = slug(name)
            html_content = generate_pin_html(brand)

            # Write temp HTML
            temp_html = OUTPUT_DIR / f"_temp_{s}.html"
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Screenshot
            page.goto(f"file:///{temp_html.resolve().as_posix()}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            pin_el = page.query_selector(".pin")
            out_path = OUTPUT_DIR / f"brand_{s}.png"
            pin_el.screenshot(path=str(out_path))
            print(f"  [{i+1}/{len(brands)}] {name} -> {out_path.name} ({out_path.stat().st_size // 1024}KB)")

            # Clean up temp
            temp_html.unlink()

            # Generate description
            pin_descs.append(generate_pin_description(brand))

        browser.close()

    # Write pin descriptions file
    with open(PIN_DESC_FILE, "w", encoding="utf-8") as f:
        f.write("Brand Pinterest Pin Descriptions — TinyFit Jewelry\n")
        f.write(f"Generated: {len(pin_descs)} pins\n")
        f.write("=" * 60 + "\n\n")
        for i, pd in enumerate(pin_descs):
            f.write(f"PIN {i+1}: {pd['title']}\n")
            f.write(f"Title: {pd['title']}\n")
            f.write(f"Description: {pd['description']}\n")
            f.write(f"Link: {pd['link']}\n")
            f.write(f"Board: {pd['board']}\n")
            f.write(f"Image: {pd['image']}\n")
            f.write("-" * 60 + "\n\n")

    print(f"\nDone! {len(pin_descs)} brand pin images + descriptions generated.")
    print(f"Images: {OUTPUT_DIR}")
    print(f"Descriptions: {PIN_DESC_FILE}")


if __name__ == "__main__":
    main()
