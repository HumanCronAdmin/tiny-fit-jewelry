"""Generate the TinyFit Jewelry PDF lead magnet from brands.json.

Dense 4-page layout. No wasted space.
Output: guides/tinyfit-complete-size-guide.pdf
"""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_FILE = Path(__file__).parent.parent / "data" / "brands.json"
OUTPUT_PDF = Path(__file__).parent / "tinyfit-complete-size-guide.pdf"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    brands = json.load(f)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# Categorize
jp_brands = [b for b in brands if "Japan" in b["country"]]
us_brands = [b for b in brands if b["country"] in ("USA", "Kenya/USA", "Japan/USA")]
uk_brands = [b for b in brands if b["country"] == "UK"]
other_brands = [b for b in brands if b not in jp_brands + us_brands + uk_brands]
size2 = [b for b in brands if b.get("min_ring_size_us") and b["min_ring_size_us"] <= 2]
under100 = [b for b in brands if b.get("price_min", 0) < 100]
adjustable = [b for b in brands if b.get("adjustable")]


def brand_row(b):
    name = b["brand"]
    ring = b.get("min_ring_size_us") or "-"
    bracelet = f'{b["min_bracelet_cm"]}cm' if b.get("min_bracelet_cm") else "-"
    price = f'${b.get("price_min","?")}-${b.get("price_max","?")}'
    adj = "Yes" if b.get("adjustable") else ""
    intl = "Yes" if b.get("intl_shipping") else ""
    return f"<tr><td><strong>{name}</strong></td><td>{b['country']}</td><td>{ring}</td><td>{bracelet}</td><td>{price}</td><td>{adj}</td><td>{intl}</td></tr>"


def brand_table(brand_list):
    rows = "\n".join([brand_row(b) for b in brand_list])
    return f"""<table>
      <thead><tr><th>Brand</th><th>Country</th><th>Ring</th><th>Bracelet</th><th>Price</th><th>Adj.</th><th>Intl</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>"""


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
@page {{ size: A4; margin: 1cm 1.3cm; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; color: #1C1917; line-height: 1.35; font-size: 7.5pt; }}

/* Cover - compact */
.cover {{ page-break-after: always; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background: linear-gradient(135deg, #B76E79 0%, #8B5E6B 100%); color: #fff; padding: 30px; }}
.cover h1 {{ font-size: 32pt; font-weight: 900; margin-bottom: 8px; }}
.cover .sub {{ font-size: 11pt; opacity: 0.9; max-width: 400px; line-height: 1.4; }}
.cover .stats {{ display: flex; gap: 20px; margin-top: 24px; }}
.cover .stat {{ background: rgba(255,255,255,0.15); padding: 10px 16px; border-radius: 8px; }}
.cover .stat-num {{ font-size: 18pt; font-weight: 900; }}
.cover .stat-label {{ font-size: 7pt; opacity: 0.8; }}
.cover .url {{ margin-top: auto; font-size: 8pt; opacity: 0.5; }}

/* Content - no forced page breaks, tight spacing */
h2 {{ font-size: 10pt; font-weight: 800; color: #B76E79; margin: 10px 0 3px; border-bottom: 2px solid #B76E79; padding-bottom: 2px; }}
h3 {{ font-size: 8.5pt; font-weight: 700; margin: 6px 0 2px; color: #44403C; }}
p {{ margin: 2px 0; font-size: 7pt; }}

table {{ width: 100%; border-collapse: collapse; margin: 3px 0 8px; font-size: 6.5pt; }}
th {{ background: #1C1917; color: #fff; padding: 2px 4px; text-align: left; font-weight: 600; font-size: 6pt; }}
td {{ padding: 2px 4px; border-bottom: 1px solid #EEECEB; }}
tr:nth-child(even) td {{ background: #FAFAF9; }}
thead {{ display: table-header-group; }}
tr {{ page-break-inside: avoid; }}

.tip {{ background: #FAF5F6; border-left: 3px solid #B76E79; padding: 4px 8px; margin: 4px 0; border-radius: 0 4px 4px 0; font-size: 7pt; }}
.formula {{ background: #1C1917; color: #fff; padding: 6px 12px; border-radius: 4px; text-align: center; font-size: 9pt; font-weight: 700; margin: 4px 0; }}
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }}
.rule {{ background: #FAF5F6; border-radius: 6px; padding: 4px 6px; font-size: 6.5pt; }}
.rule strong {{ color: #B76E79; }}
.footer {{ text-align: center; font-size: 6.5pt; color: #A8A29E; margin-top: 10px; padding-top: 6px; border-top: 1px solid #E7E5E4; }}
/* No page breaks except after cover */
</style>
</head>
<body>

<!-- COVER -->
<div class="cover">
  <h1>The Complete<br>Petite Jewelry<br>Size Guide</h1>
  <div class="sub">Everything you need to find rings (size 2-4) and bracelets (wrists under 14cm) that actually fit.</div>
  <div class="stats">
    <div class="stat"><div class="stat-num">{len(brands)}</div><div class="stat-label">Verified Brands</div></div>
    <div class="stat"><div class="stat-num">9</div><div class="stat-label">Countries</div></div>
    <div class="stat"><div class="stat-num">2026</div><div class="stat-label">Edition</div></div>
  </div>
  <div class="url">humancronadmin.github.io/tiny-fit-jewelry</div>
</div>

<!-- PAGE 2: SIZE CHARTS + MEASURING -->
<div>
  <h2>Ring Size Conversion Chart (US 1-5)</h2>
  <table>
    <thead><tr><th>US</th><th>Japan</th><th>UK</th><th>EU</th><th>Circumference</th><th>Diameter</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>1</td><td>B</td><td>38</td><td>39.1mm</td><td>12.4mm</td></tr>
      <tr><td>1.5</td><td>2</td><td>C</td><td>39</td><td>40.4mm</td><td>12.9mm</td></tr>
      <tr><td>2</td><td>3</td><td>D</td><td>41</td><td>41.7mm</td><td>13.3mm</td></tr>
      <tr><td>2.5</td><td>4</td><td>E</td><td>42</td><td>42.9mm</td><td>13.7mm</td></tr>
      <tr><td>3</td><td>5</td><td>F</td><td>44</td><td>44.2mm</td><td>14.1mm</td></tr>
      <tr><td>3.5</td><td>6</td><td>G</td><td>45</td><td>45.5mm</td><td>14.5mm</td></tr>
      <tr><td>4</td><td>7</td><td>H</td><td>46</td><td>46.8mm</td><td>14.9mm</td></tr>
      <tr><td>4.5</td><td>8</td><td>I</td><td>48</td><td>48.0mm</td><td>15.3mm</td></tr>
      <tr><td>5</td><td>9</td><td>J</td><td>49</td><td>49.3mm</td><td>15.7mm</td></tr>
    </tbody>
  </table>

  <div class="two-col">
    <div>
      <h2>How to Measure Ring Size</h2>
      <div class="tip">
        <strong>1.</strong> Wrap string around finger base, below knuckle.<br>
        <strong>2.</strong> Mark overlap. Measure in mm.<br>
        <strong>3.</strong> Match to chart above.<br>
        <strong>4.</strong> Measure in evening, room temp. Average 2 readings.
      </div>
      <p>At sizes 2-4, half a size = less than 1.3mm. Precision matters.</p>
    </div>
    <div>
      <h2>Bracelet Formula</h2>
      <div class="formula">Wrist + 1.5cm = Perfect fit</div>
      <p>If wrist = 13cm, ideal bracelet = 14.5cm.<br>
      Standard "small" = 15-16cm (2-4cm too big).<br>
      The anklet hack: adjustable anklets cinch to 14-15cm.</p>
    </div>
  </div>

  <h2>5 Styling Rules for Petite Fingers</h2>
  <div class="two-col">
    <div class="rule"><strong>1. Band width under 2mm.</strong> On size 2-3, 1mm bands look elegant. 4mm overwhelms.</div>
    <div class="rule"><strong>2. Stones under 0.5ct.</strong> Small solitaires and bezel settings flatter petite hands.</div>
    <div class="rule"><strong>3. Stack thin rings.</strong> Layer 2-3 delicate bands instead of one thick ring.</div>
    <div class="rule"><strong>4. Try the anklet hack.</strong> Adjustable anklets = perfect thin-wrist bracelets.</div>
    <div class="rule"><strong>5. Start with Japanese brands.</strong> They carry sizes from US 1.5 as standard.</div>
    <div class="rule"><strong>6. Custom costs $50-150 extra.</strong> Buy standard-stock sizes when possible.</div>
  </div>
</div>

<!-- PAGE 3: ALL BRANDS - JAPANESE + SIZE 2 -->
<div>
  <h2>Japanese Brands ({len(jp_brands)} brands) - Best for Sizes 1-3</h2>
  <p>Japanese brands have always designed for smaller hands. Many carry rings from US 1.5 (JP 1).</p>
  {brand_table(jp_brands)}

  <h2>Brands with Ring Size 2 or Smaller ({len(size2)} brands)</h2>
  <p>The hardest size to find. Every brand below carries it as standard stock.</p>
  {brand_table(size2)}

  <h2>US and International Brands ({len(us_brands) + len(uk_brands) + len(other_brands)} brands)</h2>
  {brand_table(us_brands + uk_brands + other_brands)}
</div>

<!-- PAGE 4: BUDGET + ADJUSTABLE + QUICK REFERENCE -->
<div>
  <h2>Budget Picks: Under $100 ({len(under100)} brands)</h2>
  {brand_table(under100)}

  <h2>Adjustable Jewelry ({len(adjustable)} brands) - No Sizing Guesswork</h2>
  <p>Slider chains and open cuffs that fit wrists under 14cm without custom orders.</p>
  {brand_table(adjustable)}

  <h2>Quick Reference Card</h2>
  <div class="two-col">
    <div class="tip">
      <strong>Ring Shopping Checklist</strong><br>
      1. Measure in evening, room temp<br>
      2. Check brand min size on TinyFit<br>
      3. Read return policy (custom = no returns)<br>
      4. Order half-size down if between sizes<br>
      5. Band width: stick to 1-2mm for size 2-4
    </div>
    <div class="tip">
      <strong>Bracelet Shopping Checklist</strong><br>
      1. Wrist measurement + 1.5cm = your size<br>
      2. Look for "adjustable" or "slider chain"<br>
      3. Anklets often fit better than bracelets<br>
      4. Avoid bangles (they slide off thin wrists)<br>
      5. Check if brand carries under 15cm
    </div>
  </div>

  <div class="footer">
    <p><strong>TinyFit Jewelry</strong> | humancronadmin.github.io/tiny-fit-jewelry</p>
    <p>All data verified as of 2026. This guide is free to share and print.</p>
    <p>Questions? Email petitedevlog@gmail.com | Follow @petitedevlog on X</p>
  </div>
</div>

</body>
</html>"""

temp_html = Path(__file__).parent / "_temp_guide.html"
temp_html.write_text(html, encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{temp_html.resolve().as_posix()}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    page.pdf(path=str(OUTPUT_PDF), format="A4", print_background=True)
    browser.close()

temp_html.unlink()
print(f"OK: {OUTPUT_PDF} ({OUTPUT_PDF.stat().st_size // 1024}KB)")
