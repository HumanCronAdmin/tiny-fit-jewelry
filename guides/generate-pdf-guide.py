"""Generate the TinyFit Jewelry PDF lead magnet from brands.json.

Creates a multi-page HTML guide, then converts to PDF via Playwright.
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


# Categorize brands
jp_brands = [b for b in brands if "Japan" in b["country"]]
us_brands = [b for b in brands if b["country"] in ("USA", "Kenya/USA", "Japan/USA")]
uk_brands = [b for b in brands if b["country"] == "UK"]
size2 = [b for b in brands if b.get("min_ring_size_us") and b["min_ring_size_us"] <= 2]
under100 = [b for b in brands if b.get("price_min", 0) < 100]
adjustable = [b for b in brands if b.get("adjustable")]


def brand_row(b):
    name = b["brand"]
    ring = b.get("min_ring_size_us") or "-"
    bracelet = b.get("min_bracelet_cm") or "-"
    price = f"${b.get('price_min','?')}-${b.get('price_max','?')}"
    country = b["country"]
    return f"<tr><td>{name}</td><td>{country}</td><td>{ring}</td><td>{bracelet}cm</td><td>{price}</td></tr>"


def brand_table(brand_list, caption=""):
    rows = "\n".join([brand_row(b) for b in brand_list])
    return f"""
    {f'<p class="caption">{caption}</p>' if caption else ''}
    <table>
      <thead><tr><th>Brand</th><th>Country</th><th>Min Ring</th><th>Min Bracelet</th><th>Price</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>"""


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
@page {{ size: A4; margin: 2cm; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; color: #1C1917; line-height: 1.6; font-size: 11pt; }}

.cover {{ page-break-after: always; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background: linear-gradient(135deg, #B76E79 0%, #8B5E6B 100%); color: #fff; padding: 60px; }}
.cover h1 {{ font-size: 42pt; font-weight: 900; margin-bottom: 16px; }}
.cover .sub {{ font-size: 16pt; opacity: 0.9; max-width: 500px; }}
.cover .badge {{ margin-top: 30px; background: rgba(255,255,255,0.2); padding: 10px 30px; border-radius: 30px; font-size: 12pt; }}
.cover .url {{ margin-top: auto; font-size: 10pt; opacity: 0.6; }}

.page {{ page-break-before: always; padding: 20px 0; }}
h2 {{ font-size: 18pt; font-weight: 800; color: #B76E79; margin: 30px 0 12px; border-bottom: 3px solid #B76E79; padding-bottom: 6px; }}
h3 {{ font-size: 13pt; font-weight: 700; margin: 20px 0 8px; }}
p {{ margin: 8px 0; }}
.caption {{ font-size: 10pt; color: #78716C; margin-bottom: 8px; }}

table {{ width: 100%; border-collapse: collapse; margin: 12px 0 24px; font-size: 10pt; }}
th {{ background: #1C1917; color: #fff; padding: 8px 10px; text-align: left; font-weight: 600; }}
td {{ padding: 7px 10px; border-bottom: 1px solid #E7E5E4; }}
tr:nth-child(even) td {{ background: #FAF9F8; }}

.tip {{ background: #FAF5F6; border-left: 4px solid #B76E79; padding: 12px 16px; margin: 16px 0; border-radius: 0 8px 8px 0; font-size: 10pt; }}
.formula {{ background: #1C1917; color: #fff; padding: 16px 20px; border-radius: 8px; text-align: center; font-size: 14pt; font-weight: 700; margin: 16px 0; }}
.footer {{ text-align: center; font-size: 9pt; color: #A8A29E; margin-top: 40px; }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <h1>The Complete<br>Petite Jewelry<br>Size Guide</h1>
  <div class="sub">Everything you need to find rings (size 2-4) and bracelets (wrists under 14cm) that actually fit.</div>
  <div class="badge">{len(brands)} Verified Brands | 2026 Edition</div>
  <div class="url">humancronadmin.github.io/tiny-fit-jewelry</div>
</div>

<!-- PAGE 1: SIZE CONVERSION -->
<div class="page">
  <h2>Ring Size Conversion Chart</h2>
  <p>Ring sizes vary by country. This chart covers the petite range (US 1-5) with exact measurements.</p>
  <table>
    <thead><tr><th>US Size</th><th>Japan (JP)</th><th>UK</th><th>EU</th><th>Circumference (mm)</th><th>Diameter (mm)</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>1</td><td>B</td><td>38</td><td>39.1</td><td>12.4</td></tr>
      <tr><td>1.5</td><td>2</td><td>C</td><td>39</td><td>40.4</td><td>12.9</td></tr>
      <tr><td>2</td><td>3</td><td>D</td><td>41</td><td>41.7</td><td>13.3</td></tr>
      <tr><td>2.5</td><td>4</td><td>E</td><td>42</td><td>42.9</td><td>13.7</td></tr>
      <tr><td>3</td><td>5</td><td>F</td><td>44</td><td>44.2</td><td>14.1</td></tr>
      <tr><td>3.5</td><td>6</td><td>G</td><td>45</td><td>45.5</td><td>14.5</td></tr>
      <tr><td>4</td><td>7</td><td>H</td><td>46</td><td>46.8</td><td>14.9</td></tr>
      <tr><td>4.5</td><td>8</td><td>I</td><td>48</td><td>48.0</td><td>15.3</td></tr>
      <tr><td>5</td><td>9</td><td>J</td><td>49</td><td>49.3</td><td>15.7</td></tr>
    </tbody>
  </table>

  <h2>How to Measure Your Ring Size</h2>
  <p>You need: string or paper strip + ruler.</p>
  <div class="tip">
    <strong>Step 1:</strong> Wrap string around your finger at the base, below the knuckle.<br>
    <strong>Step 2:</strong> Mark where the string overlaps.<br>
    <strong>Step 3:</strong> Measure the length in mm. That is your circumference.<br>
    <strong>Step 4:</strong> Match it to the chart above.
  </div>
  <div class="tip">
    <strong>Pro tips:</strong> Measure in the evening (fingers are largest). Measure at room temperature. Take 2 readings on different days and average. At sizes 2-4, half a size = less than 1.3mm.
  </div>

  <h2>Bracelet Sizing Formula</h2>
  <div class="formula">Your wrist (cm) + 1.5cm = Perfect bracelet length</div>
  <p>If your wrist is 13cm, your ideal bracelet is 14.5cm. Not 16cm. Standard "small" bracelets are still 2-4cm too big for you.</p>
</div>

<!-- PAGE 2: BRANDS BY SIZE -->
<div class="page">
  <h2>Brands with Ring Size 2 or Smaller ({len(size2)} brands)</h2>
  <p>The hardest size to find. These brands carry it as standard.</p>
  {brand_table(size2)}

  <h2>Japanese Brands ({len(jp_brands)} brands)</h2>
  <p>Japanese brands start where Western brands stop. Many carry rings from US size 1.</p>
  {brand_table(jp_brands)}
</div>

<!-- PAGE 3: US/UK + BUDGET -->
<div class="page">
  <h2>US and International Brands ({len(us_brands) + len(uk_brands)} brands)</h2>
  {brand_table(us_brands + uk_brands)}

  <h2>Budget-Friendly: Under $100 ({len(under100)} brands)</h2>
  <p>Small sizes do not have to mean big prices.</p>
  {brand_table(under100, "Sorted by country. Prices are for entry-level pieces.")}
</div>

<!-- PAGE 4: ADJUSTABLE + TIPS -->
<div class="page">
  <h2>Adjustable Jewelry ({len(adjustable)} brands)</h2>
  <p>Slider chains and open cuffs that fit wrists under 14cm.</p>
  {brand_table(adjustable)}

  <h2>5 Rules for Petite Jewelry</h2>

  <h3>1. Band width under 2mm</h3>
  <p>On a size 2-3 finger, a 1mm band looks elegant. A 4mm band overwhelms.</p>

  <h3>2. Stones under 0.5ct</h3>
  <p>Large stones overpower small fingers. Bezel settings sit lower and snag less.</p>

  <h3>3. Stack thin rings</h3>
  <p>Layer 2-3 delicate bands (1-1.5mm each) instead of one thick ring.</p>

  <h3>4. Try the anklet hack</h3>
  <p>Adjustable anklets cinch down to 14-15cm. Same chain weight, perfect for thin wrists.</p>

  <h3>5. Japanese brands first</h3>
  <p>If you need size 1-3, start with Japanese brands. They have the widest selection.</p>

  <div class="footer">
    <p>TinyFit Jewelry | humancronadmin.github.io/tiny-fit-jewelry</p>
    <p>All data verified as of 2026. Free to share.</p>
  </div>
</div>

</body>
</html>"""

# Write HTML and convert to PDF
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
