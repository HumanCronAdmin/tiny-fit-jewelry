"""Auto-post Pinterest pins using Playwright with Edge browser profile. v3"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

IMAGES_DIR = Path(__file__).parent / "images"

PINS = [
    {
        "image": "01_ring_size_conversion.png",
        "title": "Ring Size Chart: US vs Japanese vs EU Conversion for Sizes 2-4",
        "description": "Stop guessing your ring size across countries. This chart covers US 2-4 with Japanese, European, and UK equivalents plus exact mm measurements. Save this before your next jewelry purchase. #ringsize #sizeconversion #petitejewelry #ringguide #tinyfitjewelry",
        "link": "https://humancronadmin.github.io/tiny-fit-jewelry/rings.html",
        "board": "Ring Size 2-4 Guide",
    },
    {
        "image": "02_brands_ring_size_2.png",
        "title": "6 Brands That Actually Carry Ring Size 2 (Verified 2026)",
        "description": "Ring size 2 is the hardest to find. We verified every brand on this list. Agete, 4C, Nojess, Star Jewelry, Bloom from Japan. Automic Gold from USA. No children's jewelry. Real adult designs. #ringsize2 #smallrings #petitejewelry #agete #tinyfitjewelry",
        "link": "https://humancronadmin.github.io/tiny-fit-jewelry/size/ring-size-2.html",
        "board": "Ring Size 2-4 Guide",
    },
    {
        "image": "03_bracelet_math.png",
        "title": "Bracelet Math: The Formula for Wrists Under 14cm",
        "description": "Your wrist + 1.5cm = perfect bracelet length. Standard bracelets are 16-18cm but your wrist is under 14cm. This simple formula ensures your next bracelet actually stays on. #thinwrist #smallwristbracelet #petitebracelet #braceletfit #tinyfitjewelry",
        "link": "https://humancronadmin.github.io/tiny-fit-jewelry/bracelets.html",
        "board": "Bracelets for Thin Wrists",
    },
    {
        "image": "04_ring_styles_petite.png",
        "title": "5 Ring Styles That Look Best on Petite Fingers (Size 2-4)",
        "description": "Not all ring styles work at size 2-4. Thin bands, small solitaires, and stackable rings flatter petite fingers. Wide bands and chunky cocktail rings overwhelm them. Here is what to choose and what to avoid. #petiterings #ringstyle #smallfingers #stackablerings #tinyfitjewelry",
        "link": "https://humancronadmin.github.io/tiny-fit-jewelry/rings.html",
        "board": "Petite Style Tips",
    },
    {
        "image": "05_japanese_brand_advantage.png",
        "title": "Why Japanese Jewelry Brands Are Perfect for Petite Fingers",
        "description": "Japanese brands start where US brands stop. Agete, 4C, Nojess, Star Jewelry, Vendome Aoyama, Bloom, and Take-Up all carry rings from US size 1.5. Elegant adult designs, not children's jewelry. #japanesejewelry #petiterings #agete #nojess #tinyfitjewelry",
        "link": "https://humancronadmin.github.io/tiny-fit-jewelry/size/japanese-brands.html",
        "board": "Japanese Jewelry Brands",
    },
]


def post_pin(page, pin_data, pin_num):
    """Post a single pin to Pinterest."""
    image_path = IMAGES_DIR / pin_data["image"]
    if not image_path.exists():
        print(f"  Image not found: {image_path}")
        return False

    # Go to pin creation page
    page.goto("https://jp.pinterest.com/pin-creation-tool/", timeout=60000)
    page.wait_for_load_state("domcontentloaded")
    time.sleep(4)

    # If there's a "new" button, click it to start fresh
    try:
        new_btn = page.locator("button:has-text('新規作成')").first
        if new_btn.is_visible(timeout=3000):
            new_btn.click()
            time.sleep(2)
    except:
        pass

    # Upload image via hidden file input
    file_input = page.locator("input[type='file']").first
    file_input.set_input_files(str(image_path))
    print("  Image uploaded...")
    time.sleep(6)

    # === BOARD FIRST (must select before publish) ===
    print("  Selecting board...")
    try:
        # Click the board dropdown
        page.click("button:has-text('ボードを選択')", timeout=5000)
        time.sleep(2)
        # Type board name to search
        board_search = page.locator("input[placeholder*='検索']").first
        if board_search.is_visible(timeout=3000):
            board_search.fill(pin_data["board"])
            time.sleep(2)
        # Click the matching board
        page.locator(f"div[role='option']:has-text('{pin_data['board']}'), li:has-text('{pin_data['board']}'), div:has-text('{pin_data['board']}') >> nth=0").click()
        time.sleep(2)
        print(f"  Board: {pin_data['board']}")
    except Exception as e:
        print(f"  Board selection attempt 1 failed: {e}")
        try:
            # Fallback: try clicking any dropdown with board text
            dropdowns = page.locator("button[aria-haspopup], button:has-text('ボード')")
            for i in range(dropdowns.count()):
                btn = dropdowns.nth(i)
                if btn.is_visible():
                    btn.click()
                    time.sleep(2)
                    # Look for board name in dropdown
                    page.locator(f"text='{pin_data['board']}'").first.click()
                    time.sleep(1)
                    print(f"  Board (fallback): {pin_data['board']}")
                    break
        except Exception as e2:
            print(f"  Board selection failed completely: {e2}")

    # === TITLE ===
    try:
        title_el = page.locator("textarea").first
        title_el.click()
        time.sleep(0.5)
        title_el.fill(pin_data["title"])
        print("  Title filled")
    except Exception as e:
        print(f"  Title failed: {e}")

    # === DESCRIPTION ===
    try:
        # Find all editable text areas, pick the one for description
        textareas = page.locator("textarea")
        count = textareas.count()
        desc_filled = False
        for idx in range(count):
            el = textareas.nth(idx)
            val = el.input_value()
            # Skip if it already has the title
            if val == pin_data["title"]:
                continue
            if not val.strip():
                el.click()
                time.sleep(0.5)
                el.fill(pin_data["description"])
                print("  Description filled")
                desc_filled = True
                break
        if not desc_filled:
            # Try contenteditable div
            ce = page.locator("div[contenteditable='true']").first
            ce.click()
            time.sleep(0.5)
            ce.fill(pin_data["description"])
            print("  Description filled (contenteditable)")
    except Exception as e:
        print(f"  Description failed: {e}")

    # === LINK ===
    try:
        link_input = page.locator("input[placeholder*='リンク'], input[placeholder*='link']").first
        if link_input.is_visible(timeout=3000):
            link_input.click()
            time.sleep(0.5)
            link_input.fill(pin_data["link"])
            print("  Link filled")
        else:
            # Fallback: find text inputs
            inputs = page.locator("input[type='text']")
            for idx in range(inputs.count()):
                el = inputs.nth(idx)
                val = el.input_value()
                if not val.strip():
                    el.click()
                    time.sleep(0.5)
                    el.fill(pin_data["link"])
                    print("  Link filled (fallback)")
                    break
    except Exception as e:
        print(f"  Link failed: {e}")

    time.sleep(2)

    # Save debug screenshot
    page.screenshot(path=str(IMAGES_DIR / f"debug_v3_{pin_num}.png"))

    # === PUBLISH ===
    try:
        publish = page.locator("button:has-text('公開する')").first
        if publish.is_visible(timeout=5000):
            publish.click()
            time.sleep(5)
            # Check if error appeared
            error = page.locator("text='公開できませんでした'")
            if error.is_visible(timeout=3000):
                print("  ERROR: Publish failed!")
                return False
            print("  Published!")
            return True
        else:
            print("  Publish button not visible")
            return False
    except Exception as e:
        # Might have succeeded and navigated away
        print(f"  Publish result: {e}")
        return True


def main():
    edge_user_data = "C:/Users/user/AppData/Local/Microsoft/Edge/User Data"

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            edge_user_data,
            channel="msedge",
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=["--profile-directory=Default"],
        )
        page = context.new_page()

        page.goto("https://jp.pinterest.com/", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(5)
        print(f"Logged in as: {page.title()}")

        results = []
        for i, pin in enumerate(PINS):
            print(f"\n[{i+1}/{len(PINS)}] {pin['title'][:50]}...")
            try:
                success = post_pin(page, pin, i+1)
                results.append((pin["title"][:40], success))
            except Exception as e:
                print(f"  Error: {e}")
                results.append((pin["title"][:40], False))
            if i < len(PINS) - 1:
                print("  Waiting 15 seconds...")
                time.sleep(15)

        print("\n=== RESULTS ===")
        for title, ok in results:
            status = "OK" if ok else "FAILED"
            print(f"  [{status}] {title}")

        time.sleep(3)
        context.close()


if __name__ == "__main__":
    main()
