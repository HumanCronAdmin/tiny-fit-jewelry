"""Generate TinyFit Jewelry PDF — editorial/magazine style.

Luxury jewelry lookbook aesthetic. Not a spreadsheet.
"""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_FILE = Path(__file__).parent.parent / "data" / "brands.json"
OUTPUT_PDF = Path(__file__).parent / "tinyfit-complete-size-guide.pdf"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    brands = json.load(f)

jp_brands = [b for b in brands if "Japan" in b["country"]]
us_uk_brands = [b for b in brands if b["country"] in ("USA", "Kenya/USA", "Japan/USA", "UK", "Canada")]
other_brands = [b for b in brands if b not in jp_brands and b not in us_uk_brands]
size2 = [b for b in brands if b.get("min_ring_size_us") and b["min_ring_size_us"] <= 2]
adjustable = [b for b in brands if b.get("adjustable")]


def brand_card(b):
    name = b["brand"]
    ring = f'Ring: US {b["min_ring_size_us"]}' if b.get("min_ring_size_us") else ""
    bracelet = f'Bracelet: {b["min_bracelet_cm"]} cm' if b.get("min_bracelet_cm") else ""
    sizes = " &bull; ".join(filter(None, [ring, bracelet]))
    price = f'${b.get("price_min","?")}&ndash;${b.get("price_max","?")}'
    tags = []
    if b.get("adjustable"):
        tags.append('<span class="tag tag-adj">Adjustable</span>')
    if b.get("intl_shipping"):
        tags.append('<span class="tag tag-intl">Ships Intl</span>')
    tags_html = " ".join(tags)
    return f'''<div class="brand-card">
      <div class="bc-header">
        <div class="bc-name">{name}</div>
        <div class="bc-country">{b["country"]}</div>
      </div>
      <div class="bc-sizes">{sizes}</div>
      <div class="bc-price">{price}</div>
      <div class="bc-tags">{tags_html}</div>
    </div>'''


def brand_cards_grid(brand_list):
    cards = "\n".join([brand_card(b) for b in brand_list])
    return f'<div class="card-grid">{cards}</div>'


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600;700&display=swap');
@page {{ size: A4; margin: 0; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; color: #2D2926; }}

/* ── COVER ── */
.cover {{
  width: 210mm; height: 297mm;
  background: linear-gradient(160deg, #1C1917 0%, #2D2926 40%, #44403C 100%);
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  text-align: center; color: #fff; position: relative; page-break-after: always;
}}
.cover::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 30% 20%, rgba(183,110,121,0.3) 0%, transparent 60%),
              radial-gradient(ellipse at 70% 80%, rgba(201,169,110,0.2) 0%, transparent 50%);
}}
.cover * {{ position: relative; z-index: 1; }}
.cover-label {{ font-size: 9pt; letter-spacing: 5px; text-transform: uppercase; color: #C9A96E; margin-bottom: 20px; }}
.cover h1 {{ font-family: 'Playfair Display', serif; font-size: 38pt; font-weight: 900; line-height: 1.15; margin-bottom: 16px; }}
.cover h1 em {{ font-style: italic; color: #C9A96E; }}
.cover .sub {{ font-size: 11pt; color: rgba(255,255,255,0.7); max-width: 380px; line-height: 1.6; }}
.cover-stats {{ display: flex; gap: 32px; margin-top: 36px; }}
.cover-stat {{ text-align: center; }}
.cover-stat .num {{ font-family: 'Playfair Display', serif; font-size: 28pt; font-weight: 900; color: #C9A96E; }}
.cover-stat .label {{ font-size: 7pt; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.5); margin-top: 2px; }}
.cover-footer {{ position: absolute; bottom: 24px; font-size: 7pt; color: rgba(255,255,255,0.3); letter-spacing: 1px; }}

/* ── PAGE LAYOUT ── */
.content-page {{
  padding: 28px 32px 20px;
  font-size: 8pt;
  line-height: 1.5;
}}
.page-header {{
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid #E7E5E4; padding-bottom: 6px; margin-bottom: 14px;
}}
.page-header .brand {{ font-family: 'Playfair Display', serif; font-size: 10pt; font-weight: 700; color: #B76E79; }}
.page-header .page-num {{ font-size: 7pt; color: #A8A29E; }}

/* ── SECTION HEADERS ── */
.section {{
  margin-bottom: 14px;
}}
.section-header {{
  display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
}}
.section-icon {{
  width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 13px; flex-shrink: 0;
}}
.section-icon.rose {{ background: #B76E79; color: #fff; }}
.section-icon.gold {{ background: #C9A96E; color: #fff; }}
.section-icon.dark {{ background: #1C1917; color: #fff; }}
.section-icon.green {{ background: #5B8C7A; color: #fff; }}
.section-title {{
  font-family: 'Playfair Display', serif; font-size: 13pt; font-weight: 700; color: #1C1917;
}}
.section-subtitle {{ font-size: 7.5pt; color: #78716C; margin-top: -2px; }}

/* ── SIZE CHART ── */
.size-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 6px 0 10px; font-size: 7.5pt; border-radius: 8px; overflow: hidden; }}
.size-table th {{ background: #1C1917; color: #C9A96E; padding: 6px 8px; text-align: center; font-weight: 600; font-size: 7pt; letter-spacing: 0.5px; }}
.size-table td {{ padding: 5px 8px; text-align: center; border-bottom: 1px solid #F0EEEE; }}
.size-table tr:nth-child(even) td {{ background: #FAF9F8; }}
.size-table tr:hover td {{ background: #FAF5F6; }}
.size-table td:first-child {{ font-weight: 700; color: #B76E79; }}

/* ── BRAND CARDS ── */
.card-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 6px 0; }}
.brand-card {{
  background: #FAFAF9; border: 1px solid #E7E5E4; border-radius: 8px; padding: 8px 10px;
  font-size: 7pt; transition: border-color 0.2s;
}}
.bc-header {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 3px; }}
.bc-name {{ font-weight: 700; font-size: 8pt; color: #1C1917; }}
.bc-country {{ font-size: 6.5pt; color: #B76E79; font-weight: 600; }}
.bc-sizes {{ color: #44403C; font-size: 7pt; margin-bottom: 2px; }}
.bc-price {{ color: #78716C; font-size: 6.5pt; }}
.bc-tags {{ margin-top: 3px; }}
.tag {{ display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 5.5pt; font-weight: 600; }}
.tag-adj {{ background: #E8F5E9; color: #2E7D32; }}
.tag-intl {{ background: #E3F2FD; color: #1565C0; }}

/* ── TIP BOXES ── */
.tip-box {{
  background: linear-gradient(135deg, #FAF5F6, #FFF5F6);
  border: 1px solid #F0D4D8; border-radius: 8px; padding: 10px 12px; margin: 6px 0;
}}
.tip-box .tip-title {{ font-weight: 700; font-size: 8pt; color: #B76E79; margin-bottom: 3px; }}
.tip-box p {{ font-size: 7.5pt; line-height: 1.5; }}

.formula-box {{
  background: linear-gradient(135deg, #1C1917, #2D2926);
  color: #fff; padding: 14px 18px; border-radius: 10px; text-align: center; margin: 8px 0;
}}
.formula-box .formula {{ font-family: 'Playfair Display', serif; font-size: 14pt; font-weight: 700; color: #C9A96E; }}
.formula-box .formula-desc {{ font-size: 7.5pt; color: rgba(255,255,255,0.7); margin-top: 4px; }}

/* ── STYLING RULES ── */
.rules-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin: 6px 0; }}
.rule-card {{
  background: #fff; border: 1px solid #E7E5E4; border-radius: 8px; padding: 8px 10px;
  display: flex; gap: 8px; align-items: flex-start;
}}
.rule-num {{
  width: 22px; height: 22px; border-radius: 50%; background: #B76E79; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 7pt; font-weight: 700; flex-shrink: 0;
}}
.rule-text {{ font-size: 7pt; line-height: 1.4; }}
.rule-text strong {{ color: #1C1917; }}

/* ── TWO COLUMN ── */
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}

/* ── CHECKLIST ── */
.checklist {{ list-style: none; font-size: 7.5pt; }}
.checklist li {{ padding: 3px 0; padding-left: 16px; position: relative; }}
.checklist li::before {{ content: '\\2713'; position: absolute; left: 0; color: #B76E79; font-weight: 700; }}

/* ── FOOTER ── */
.pdf-footer {{
  background: #1C1917; color: rgba(255,255,255,0.6); padding: 14px 32px;
  display: flex; justify-content: space-between; align-items: center; font-size: 7pt;
  margin-top: 12px;
}}
.pdf-footer strong {{ color: #C9A96E; }}
</style>
</head>
<body>

<!-- ════════ COVER ════════ -->
<div class="cover">
  <div class="cover-label">TinyFit Jewelry Presents</div>
  <h1>The Complete<br>Petite Jewelry<br><em>Size Guide</em></h1>
  <div class="sub">Everything you need to find rings in size 2&ndash;4 and bracelets for wrists under 14 cm. Verified data. Real brands. No guesswork.</div>
  <div class="cover-stats">
    <div class="cover-stat"><div class="num">{len(brands)}</div><div class="label">Brands</div></div>
    <div class="cover-stat"><div class="num">9</div><div class="label">Countries</div></div>
    <div class="cover-stat"><div class="num">2026</div><div class="label">Edition</div></div>
  </div>
  <div class="cover-footer">humancronadmin.github.io/tiny-fit-jewelry</div>
</div>

<!-- ════════ PAGE 2: SIZE GUIDE + FORMULAS ════════ -->
<div class="content-page">
  <div class="page-header">
    <div class="brand">TinyFit Jewelry</div>
    <div class="page-num">Size Charts &amp; Measurement</div>
  </div>

  <div class="section">
    <div class="section-header">
      <div class="section-icon rose">&#128141;</div>
      <div>
        <div class="section-title">Ring Size Conversion</div>
        <div class="section-subtitle">US sizes 1&ndash;5 with international equivalents</div>
      </div>
    </div>
    <table class="size-table">
      <thead><tr><th>US</th><th>Japan</th><th>UK</th><th>EU</th><th>Circumference</th><th>Diameter</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>1</td><td>B</td><td>38</td><td>39.1 mm</td><td>12.4 mm</td></tr>
        <tr><td>1.5</td><td>2</td><td>C</td><td>39</td><td>40.4 mm</td><td>12.9 mm</td></tr>
        <tr><td>2</td><td>3</td><td>D</td><td>41</td><td>41.7 mm</td><td>13.3 mm</td></tr>
        <tr><td>2.5</td><td>4</td><td>E</td><td>42</td><td>42.9 mm</td><td>13.7 mm</td></tr>
        <tr><td>3</td><td>5</td><td>F</td><td>44</td><td>44.2 mm</td><td>14.1 mm</td></tr>
        <tr><td>3.5</td><td>6</td><td>G</td><td>45</td><td>45.5 mm</td><td>14.5 mm</td></tr>
        <tr><td>4</td><td>7</td><td>H</td><td>46</td><td>46.8 mm</td><td>14.9 mm</td></tr>
        <tr><td>4.5</td><td>8</td><td>I</td><td>48</td><td>48.0 mm</td><td>15.3 mm</td></tr>
        <tr><td>5</td><td>9</td><td>J</td><td>49</td><td>49.3 mm</td><td>15.7 mm</td></tr>
      </tbody>
    </table>
  </div>

  <div class="two-col">
    <div class="tip-box">
      <div class="tip-title">How to Measure Your Ring Size</div>
      <p><strong>1.</strong> Wrap string around finger base, below knuckle<br>
      <strong>2.</strong> Mark the overlap point<br>
      <strong>3.</strong> Measure the length in mm<br>
      <strong>4.</strong> Match to the chart above</p>
      <p style="margin-top:4px;color:#B76E79;font-weight:600;">Pro tip: Measure in the evening at room temperature. Take 2 readings on different days. At sizes 2&ndash;4, half a size is less than 1.3 mm.</p>
    </div>
    <div>
      <div class="formula-box">
        <div class="formula">Wrist + 1.5 cm = Perfect Fit</div>
        <div class="formula-desc">13 cm wrist &rarr; 14.5 cm bracelet. Standard "small" is 15&ndash;16 cm (too big).</div>
      </div>
      <div class="tip-box" style="margin-top:6px;">
        <div class="tip-title">The Anklet Hack</div>
        <p>Adjustable anklets cinch down to 14&ndash;15 cm. Same chain weight, perfect proportions for thin wrists. Try it before buying a "bracelet."</p>
      </div>
    </div>
  </div>

  <div class="section" style="margin-top:10px;">
    <div class="section-header">
      <div class="section-icon gold">&#10024;</div>
      <div>
        <div class="section-title">6 Styling Rules for Petite Fingers</div>
      </div>
    </div>
    <div class="rules-grid">
      <div class="rule-card"><div class="rule-num">1</div><div class="rule-text"><strong>Band width under 2 mm.</strong> On size 2&ndash;3, thin bands look elegant. Wide bands overwhelm.</div></div>
      <div class="rule-card"><div class="rule-num">2</div><div class="rule-text"><strong>Stones under 0.5 ct.</strong> Small solitaires and bezel settings flatter petite hands.</div></div>
      <div class="rule-card"><div class="rule-num">3</div><div class="rule-text"><strong>Stack thin rings.</strong> Layer 2&ndash;3 delicate bands (1&ndash;1.5 mm each) instead of one thick ring.</div></div>
      <div class="rule-card"><div class="rule-num">4</div><div class="rule-text"><strong>Bezel over prong.</strong> Lower profile, less snagging, better proportions on small fingers.</div></div>
      <div class="rule-card"><div class="rule-num">5</div><div class="rule-text"><strong>Japanese brands first.</strong> They carry sizes from US 1.5 as standard. Widest selection.</div></div>
      <div class="rule-card"><div class="rule-num">6</div><div class="rule-text"><strong>Skip custom when possible.</strong> Custom sizing costs $50&ndash;$150 extra. Buy standard-stock sizes.</div></div>
    </div>
  </div>
</div>

<!-- ════════ PAGE 3: BRAND DIRECTORY ════════ -->
<div class="content-page">
  <div class="page-header">
    <div class="brand">TinyFit Jewelry</div>
    <div class="page-num">Brand Directory</div>
  </div>

  <div class="section">
    <div class="section-header">
      <div class="section-icon rose">&#127471;&#127477;</div>
      <div>
        <div class="section-title">Japanese Brands ({len(jp_brands)})</div>
        <div class="section-subtitle">Best for sizes 1&ndash;3. They start where Western brands stop.</div>
      </div>
    </div>
    {brand_cards_grid(jp_brands)}
  </div>

  <div class="section">
    <div class="section-header">
      <div class="section-icon dark">&#127468;&#127463;</div>
      <div>
        <div class="section-title">US, UK &amp; International ({len(us_uk_brands)})</div>
        <div class="section-subtitle">Growing selection of petite-friendly Western brands.</div>
      </div>
    </div>
    {brand_cards_grid(us_uk_brands)}
  </div>

  {"<div class='section'><div class='section-header'><div class='section-icon gold'>&#127758;</div><div><div class='section-title'>Other Regions (" + str(len(other_brands)) + ")</div></div></div>" + brand_cards_grid(other_brands) + "</div>" if other_brands else ""}
</div>

<!-- ════════ PAGE 4: SPECIAL LISTS + CHECKLIST ════════ -->
<div class="content-page">
  <div class="page-header">
    <div class="brand">TinyFit Jewelry</div>
    <div class="page-num">Special Lists &amp; Quick Reference</div>
  </div>

  <div class="two-col">
    <div class="section">
      <div class="section-header">
        <div class="section-icon rose">&#128142;</div>
        <div>
          <div class="section-title">Ring Size 2 Club ({len(size2)})</div>
          <div class="section-subtitle">The hardest size. These carry it.</div>
        </div>
      </div>
      {brand_cards_grid(size2)}
    </div>
    <div class="section">
      <div class="section-header">
        <div class="section-icon green">&#128279;</div>
        <div>
          <div class="section-title">Adjustable ({len(adjustable)})</div>
          <div class="section-subtitle">No guessing. Slider chains &amp; open cuffs.</div>
        </div>
      </div>
      {brand_cards_grid(adjustable)}
    </div>
  </div>

  <div class="two-col" style="margin-top:10px;">
    <div class="tip-box">
      <div class="tip-title">Ring Shopping Checklist</div>
      <ul class="checklist">
        <li>Measure in the evening, room temperature</li>
        <li>Check brand's min size on TinyFit Jewelry</li>
        <li>Read return policy (custom = no returns)</li>
        <li>Order half-size down if between sizes</li>
        <li>Band width: 1&ndash;2 mm for size 2&ndash;4</li>
        <li>Compare brands at tinyfitjewelry/compare</li>
      </ul>
    </div>
    <div class="tip-box">
      <div class="tip-title">Bracelet Shopping Checklist</div>
      <ul class="checklist">
        <li>Wrist + 1.5 cm = your bracelet size</li>
        <li>Look for "adjustable" or "slider chain"</li>
        <li>Anklets often fit thin wrists better</li>
        <li>Avoid bangles (they slide off)</li>
        <li>Check if brand carries under 15 cm</li>
        <li>Gorjana &amp; Monica Vinader have great options</li>
      </ul>
    </div>
  </div>

  <div class="pdf-footer">
    <div><strong>TinyFit Jewelry</strong> &bull; humancronadmin.github.io/tiny-fit-jewelry</div>
    <div>All data verified 2026 &bull; Free to share &bull; @petitedevlog</div>
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
