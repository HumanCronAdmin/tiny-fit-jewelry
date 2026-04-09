"""Auto-post 33 brand Pinterest pins. Uses English Pinterest to avoid encoding issues."""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BRAND_IMAGES = Path(__file__).parent / "brand_images"
DATA_FILE = Path(__file__).parent.parent / "data" / "brands.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    brands = json.load(f)

import re
def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def get_pin_data(brand):
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
    desc = f"{name} from {country}. {size_info}${price_min}-${price_max}. {style.capitalize()} designs. We verified their actual size range so you don't have to guess. #petitejewelry #smallrings #tinyfitjewelry #ringsize #petitewomen"
    link = f"https://humancronadmin.github.io/tiny-fit-jewelry/brands/{s}.html"

    if min_ring != "N/A" and min_ring <= 2:
        board = "Ring Size 2-4 Guide"
    elif country == "Japan":
        board = "Japanese Jewelry Brands"
    else:
        board = "Jewelry for Tiny Fingers"

    return {
        "image": BRAND_IMAGES / f"brand_{s}.png",
        "title": title[:100],
        "description": desc[:500],
        "link": link,
        "board": board,
    }


def post_pin(page, pin, num, total):
    """Post one pin using English Pinterest UI."""
    if not pin["image"].exists():
        print(f"  SKIP: image not found {pin['image'].name}")
        return False

    # Navigate to pin creation (English)
    page.goto("https://www.pinterest.com/pin-creation-tool/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")
    time.sleep(4)

    # Click "new" if drafts panel is open
    try:
        new_btn = page.locator("button").filter(has_text="New Pin")
        if new_btn.count() == 0:
            new_btn = page.locator("button").filter(has_text="新規作成")
        if new_btn.first.is_visible(timeout=2000):
            new_btn.first.click()
            time.sleep(2)
    except:
        pass

    # Upload image
    file_input = page.locator("input[type='file']").first
    file_input.set_input_files(str(pin["image"]))
    time.sleep(5)

    # Fill fields using aria labels and roles (more reliable than text matching)
    # Title
    try:
        title_input = page.locator("[data-test-id='pin-draft-title'] textarea, [data-test-id='pin-draft-title'] input").first
        if title_input.count() == 0:
            # Fallback: first visible contenteditable or textarea
            title_input = page.locator("div[contenteditable='true']").first
        title_input.click()
        time.sleep(0.3)
        page.keyboard.type(pin["title"], delay=10)
        time.sleep(0.5)
    except Exception as e:
        print(f"  Title: {e}")

    # Tab to description
    try:
        page.keyboard.press("Tab")
        time.sleep(0.3)
        page.keyboard.type(pin["description"], delay=5)
        time.sleep(0.5)
    except Exception as e:
        print(f"  Desc: {e}")

    # Link - find and fill
    try:
        link_el = page.locator("input[placeholder*='link'], input[placeholder*='リンク'], input[placeholder*='Add a destination link']").first
        if link_el.is_visible(timeout=3000):
            link_el.click()
            time.sleep(0.3)
            link_el.fill(pin["link"])
    except:
        pass

    # Board - click dropdown and select
    try:
        board_btn = page.locator("button").filter(has_text="Board").first
        if board_btn.count() == 0:
            board_btn = page.locator("button").filter(has_text="ボードを選択").first
        if board_btn.count() == 0:
            board_btn = page.locator("button").filter(has_text="Pick a board").first
        if board_btn.is_visible(timeout=3000):
            board_btn.click()
            time.sleep(2)
            # Search for board
            search = page.locator("input[type='text']").last
            search.fill(pin["board"])
            time.sleep(1)
            # Click matching option
            page.locator(f"div:has-text('{pin['board']}')").first.click()
            time.sleep(1)
    except Exception as e:
        print(f"  Board: {e}")

    time.sleep(1)

    # Publish
    try:
        pub = page.locator("button").filter(has_text="Publish")
        if pub.count() == 0:
            pub = page.locator("button").filter(has_text="公開する")
        pub.first.click()
        time.sleep(4)

        # Check for error
        try:
            err = page.locator("text=公開できませんでした, text=couldn't publish")
            if err.is_visible(timeout=2000):
                print(f"  [{num}/{total}] FAILED")
                return False
        except:
            pass

        print(f"  [{num}/{total}] OK: {pin['title'][:40]}")
        return True
    except Exception as e:
        print(f"  [{num}/{total}] Publish: {e}")
        return False


def main():
    edge_user_data = "C:/Users/user/AppData/Local/Microsoft/Edge/User Data"

    pin_list = []
    for brand in brands:
        pin_list.append(get_pin_data(brand))

    print(f"Posting {len(pin_list)} brand pins to Pinterest...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            edge_user_data,
            channel="msedge",
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=["--profile-directory=Default"],
            locale="en-US",
        )
        page = context.new_page()

        # Set language to English
        page.goto("https://www.pinterest.com/", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(5)

        ok = 0
        fail = 0
        for i, pin in enumerate(pin_list):
            success = post_pin(page, pin, i+1, len(pin_list))
            if success:
                ok += 1
            else:
                fail += 1
            if i < len(pin_list) - 1:
                time.sleep(10)

        print(f"\n=== DONE: {ok} posted, {fail} failed ===")
        time.sleep(3)
        context.close()


if __name__ == "__main__":
    main()
