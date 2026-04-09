"""Generate Pinterest pin images from infographic_pins.html using Playwright."""
from playwright.sync_api import sync_playwright
from pathlib import Path

html_path = Path(__file__).parent / "infographic_pins.html"
output_dir = Path(__file__).parent / "images"
output_dir.mkdir(exist_ok=True)

pin_names = [
    "01_ring_size_conversion",
    "02_brands_ring_size_2",
    "03_bracelet_math",
    "04_ring_styles_petite",
    "05_japanese_brand_advantage",
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 1800})
    page.goto(f"file:///{html_path.resolve().as_posix()}")
    page.wait_for_load_state("networkidle")
    # Wait for fonts
    page.wait_for_timeout(2000)

    pins = page.query_selector_all(".pin")
    print(f"Found {len(pins)} pins")

    for i, pin in enumerate(pins):
        if i < len(pin_names):
            filename = pin_names[i]
        else:
            filename = f"pin_{i+1}"
        out_path = output_dir / f"{filename}.png"
        pin.screenshot(path=str(out_path))
        print(f"Saved: {out_path.name} ({out_path.stat().st_size // 1024}KB)")

    browser.close()

print(f"\nDone! {len(pins)} images saved to {output_dir}")
