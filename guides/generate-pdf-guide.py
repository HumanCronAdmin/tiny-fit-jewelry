"""Generate TinyFit Jewelry PDF — Champagne & Sage editorial style.

Warm white background + sage green headings + champagne gold accents.
Light, airy, jewelry-appropriate. Not dark, not financial.
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
western_brands = [b for b in brands if b not in jp_brands]
size2 = [b for b in brands if b.get("min_ring_size_us") and b["min_ring_size_us"] <= 2]
adjustable = [b for b in brands if b.get("adjustable")]

# Colors
SAGE = "#4A6259"
GOLD = "#C9A96E"
BG = "#FDFAF6"
CARD_BG = "#F0F4F1"
TEXT = "#2D2D2D"
MUTED = "#7A8580"


def brand_card(b):
    name = b["brand"]
    ring = f'Ring US {b["min_ring_size_us"]}' if b.get("min_ring_size_us") else ""
    bracelet = f'Bracelet {b["min_bracelet_cm"]} cm' if b.get("min_bracelet_cm") else ""
    sizes = " | ".join(filter(None, [ring, bracelet]))
    price = f'${b.get("price_min","?")}&ndash;${b.get("price_max","?")}'
    badges = []
    if b.get("adjustable"): badges.append('<span class="badge badge-g">Adjustable</span>')
    if b.get("intl_shipping"): badges.append('<span class="badge badge-b">Intl Shipping</span>')
    badge_html = " ".join(badges)
    return f'''<div class="bc">
      <div class="bc-name">{name}</div>
      <div class="bc-loc">{b["country"]}</div>
      <div class="bc-sizes">{sizes}</div>
      <div class="bc-price">{price}</div>
      {f'<div class="bc-badges">{badge_html}</div>' if badge_html else ''}
    </div>'''


def cards(brand_list):
    return '<div class="grid">' + "".join([brand_card(b) for b in brand_list]) + '</div>'


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Inter:wght@400;500;600;700&display=swap');
@page {{ size: A4; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',sans-serif; background:{BG}; color:{TEXT}; font-size:7.5pt; line-height:1.5; }}

/* ═══ COVER ═══ */
.cover {{
  width:210mm; height:297mm; page-break-after:always;
  background:{BG};
  display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center; position:relative;
  border-top: 6px solid {SAGE};
}}
.cover::before {{
  content:''; position:absolute; top:60px; left:50%; transform:translateX(-50%);
  width:80px; height:2px; background:{GOLD};
}}
.cv-label {{
  font-size:8pt; letter-spacing:5px; text-transform:uppercase; color:{GOLD};
  margin-bottom:24px; margin-top:40px;
}}
.cover h1 {{
  font-family:'Playfair Display',serif; font-size:38pt; font-weight:900;
  line-height:1.15; color:{SAGE}; margin-bottom:16px;
}}
.cover h1 em {{ font-style:italic; color:{GOLD}; }}
.cv-sub {{
  font-size:10.5pt; color:{MUTED}; max-width:380px; line-height:1.7;
}}
.cv-stats {{ display:flex; gap:40px; margin-top:40px; }}
.cv-stat {{ text-align:center; }}
.cv-stat .n {{ font-family:'Playfair Display',serif; font-size:32pt; font-weight:900; color:{SAGE}; }}
.cv-stat .l {{ font-size:7pt; letter-spacing:2px; text-transform:uppercase; color:{MUTED}; margin-top:2px; }}
.cv-line {{ width:120px; height:1px; background:{GOLD}; margin:40px auto 0; }}
.cv-foot {{ position:absolute; bottom:28px; font-size:7pt; color:#B8B8B0; letter-spacing:1px; }}

/* ═══ CONTENT PAGES ═══ */
.pg {{ padding:22px 28px 16px; }}
.pg-head {{
  display:flex; justify-content:space-between; align-items:center;
  border-bottom:2px solid {CARD_BG}; padding-bottom:6px; margin-bottom:14px;
}}
.pg-head .logo {{ font-family:'Playfair Display',serif; font-size:10pt; color:{SAGE}; }}
.pg-head .label {{ font-size:6.5pt; color:{MUTED}; letter-spacing:1px; text-transform:uppercase; }}

/* ═══ SECTIONS ═══ */
.sec {{ margin-bottom:12px; }}
.sec-title {{
  font-family:'Playfair Display',serif; font-size:12pt; font-weight:700; color:{SAGE};
  margin-bottom:2px;
}}
.sec-sub {{ font-size:7pt; color:{MUTED}; margin-bottom:6px; }}

/* ═══ SIZE TABLE ═══ */
.st {{
  width:100%; border-collapse:separate; border-spacing:0;
  margin:4px 0 10px; font-size:7.5pt; border-radius:8px; overflow:hidden;
  border:1px solid #DDD8D0;
}}
.st th {{
  background:{SAGE}; color:#fff; padding:6px 8px; text-align:center;
  font-weight:600; font-size:7pt; letter-spacing:0.5px;
}}
.st td {{ padding:5px 8px; text-align:center; border-bottom:1px solid #E8E4DE; }}
.st tr:nth-child(even) td {{ background:{CARD_BG}; }}
.st td:first-child {{ font-weight:700; color:{SAGE}; font-size:8pt; }}

/* ═══ BRAND CARDS ═══ */
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:5px; margin:5px 0; }}
.bc {{
  background:#fff; border:1px solid #E0DDD6; border-radius:8px; padding:7px 9px;
  page-break-inside:avoid;
}}
.bc-name {{ font-weight:700; font-size:7.5pt; color:{SAGE}; }}
.bc-loc {{ font-size:6pt; color:{GOLD}; font-weight:600; margin-bottom:2px; }}
.bc-sizes {{ color:{TEXT}; font-size:6.5pt; }}
.bc-price {{ color:{MUTED}; font-size:6pt; margin-top:1px; }}
.bc-badges {{ margin-top:2px; }}
.badge {{
  display:inline-block; padding:1px 5px; border-radius:3px;
  font-size:5pt; font-weight:600;
}}
.badge-g {{ background:#E8F0EC; color:{SAGE}; }}
.badge-b {{ background:#EDE8DF; color:#8B7B5E; }}

/* ═══ BOXES ═══ */
.tip {{
  background:{CARD_BG}; border:1px solid #D8D4CD;
  border-left:3px solid {SAGE}; border-radius:0 8px 8px 0;
  padding:8px 10px; margin:4px 0; font-size:7pt;
}}
.tip strong {{ color:{SAGE}; }}
.formula-box {{
  background:{SAGE}; color:#fff;
  padding:12px 18px; border-radius:10px; text-align:center; margin:6px 0;
}}
.formula-box .f {{ font-family:'Playfair Display',serif; font-size:14pt; font-weight:700; color:{GOLD}; }}
.formula-box .fd {{ font-size:7.5pt; margin-top:3px; opacity:0.85; }}

/* ═══ RULES ═══ */
.rules {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:5px; margin:5px 0; }}
.rule {{
  background:#fff; border:1px solid #E0DDD6; border-radius:8px; padding:6px 8px;
  display:flex; gap:6px; align-items:flex-start; font-size:6.5pt;
}}
.rule-n {{
  width:20px; height:20px; border-radius:50%; background:{SAGE}; color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-size:7pt; font-weight:700; flex-shrink:0;
}}
.rule strong {{ color:{SAGE}; }}

/* ═══ LAYOUT ═══ */
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
.cl {{ list-style:none; font-size:7pt; }}
.cl li {{ padding:2px 0 2px 14px; position:relative; }}
.cl li::before {{ content:'\\2713'; position:absolute; left:0; color:{SAGE}; font-weight:700; }}

/* ═══ FOOTER ═══ */
.ft {{
  background:{SAGE}; color:#fff; padding:8px 24px;
  display:flex; justify-content:space-between; font-size:6.5pt; font-weight:500;
  margin-top:10px; border-radius:8px;
}}
.ft strong {{ color:{GOLD}; }}
</style>
</head>
<body>

<!-- ═══ COVER ═══ -->
<div class="cover">
  <div class="cv-label">TinyFit Jewelry Presents</div>
  <h1>The Complete<br>Petite Jewelry<br><em>Size Guide</em></h1>
  <div class="cv-sub">Everything you need to find rings in size 2&ndash;4 and bracelets for wrists under 14 cm. Verified data from {len(brands)} brands across 9 countries.</div>
  <div class="cv-stats">
    <div class="cv-stat"><div class="n">{len(brands)}</div><div class="l">Brands</div></div>
    <div class="cv-stat"><div class="n">9</div><div class="l">Countries</div></div>
    <div class="cv-stat"><div class="n">2026</div><div class="l">Edition</div></div>
  </div>
  <div class="cv-line"></div>
  <div class="cv-foot">humancronadmin.github.io/tiny-fit-jewelry</div>
</div>

<!-- ═══ PAGE 2: SIZE CHARTS + RULES ═══ -->
<div class="pg">
  <div class="pg-head"><div class="logo">TinyFit Jewelry</div><div class="label">Size Charts &amp; Styling</div></div>

  <div class="sec">
    <div class="sec-title">Ring Size Conversion</div>
    <div class="sec-sub">US sizes 1&ndash;5 with Japan, UK, and EU equivalents</div>
    <table class="st">
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

  <div class="two">
    <div>
      <div class="tip">
        <strong>How to Measure Your Ring Size</strong><br>
        <strong>1.</strong> Wrap string around finger base, below knuckle<br>
        <strong>2.</strong> Mark the overlap point<br>
        <strong>3.</strong> Measure the length in mm<br>
        <strong>4.</strong> Match to the chart above<br>
        <span style="color:{GOLD};font-weight:600;">Tip: Evening + room temp. At size 2&ndash;4, half a size &lt; 1.3 mm.</span>
      </div>
    </div>
    <div>
      <div class="formula-box">
        <div class="f">Wrist + 1.5 cm = Perfect Fit</div>
        <div class="fd">13 cm wrist &rarr; 14.5 cm bracelet. Standard "small" (15&ndash;16 cm) is still too big.</div>
      </div>
      <div class="tip" style="margin-top:5px;">
        <strong>The Anklet Hack</strong><br>
        Adjustable anklets cinch to 14&ndash;15 cm. Perfect chain weight for thin wrists. Try before buying a "bracelet."
      </div>
    </div>
  </div>

  <div class="sec" style="margin-top:8px;">
    <div class="sec-title">6 Styling Rules for Petite Fingers</div>
    <div class="rules">
      <div class="rule"><div class="rule-n">1</div><div><strong>Band under 2 mm.</strong> Thin bands = elegant on small fingers.</div></div>
      <div class="rule"><div class="rule-n">2</div><div><strong>Stones under 0.5 ct.</strong> Small solitaires flatter petite hands.</div></div>
      <div class="rule"><div class="rule-n">3</div><div><strong>Stack thin rings.</strong> 2&ndash;3 delicate bands beat 1 thick ring.</div></div>
      <div class="rule"><div class="rule-n">4</div><div><strong>Bezel over prong.</strong> Lower profile, better proportions.</div></div>
      <div class="rule"><div class="rule-n">5</div><div><strong>Japanese brands first.</strong> Sizes from US 1.5 standard.</div></div>
      <div class="rule"><div class="rule-n">6</div><div><strong>Skip custom when you can.</strong> $50&ndash;$150 extra cost.</div></div>
    </div>
  </div>
</div>

<!-- ═══ PAGE 3: BRAND DIRECTORY ═══ -->
<div class="pg">
  <div class="pg-head"><div class="logo">TinyFit Jewelry</div><div class="label">Brand Directory &mdash; {len(brands)} Verified</div></div>

  <div class="sec">
    <div class="sec-title">Japanese Brands ({len(jp_brands)})</div>
    <div class="sec-sub">Best for sizes 1&ndash;3. They start where Western brands stop.</div>
    {cards(jp_brands)}
  </div>

  <div class="sec">
    <div class="sec-title">Western &amp; International ({len(western_brands)})</div>
    <div class="sec-sub">US, UK, Canada &amp; more. Growing petite-friendly selection.</div>
    {cards(western_brands)}
  </div>
</div>

<!-- ═══ PAGE 4: SPECIAL LISTS + CHECKLISTS ═══ -->
<div class="pg">
  <div class="pg-head"><div class="logo">TinyFit Jewelry</div><div class="label">Special Lists &amp; Quick Reference</div></div>

  <div class="two">
    <div class="sec">
      <div class="sec-title">Ring Size 2 Club ({len(size2)})</div>
      <div class="sec-sub">The hardest size to find. These carry it as standard.</div>
      {cards(size2)}
    </div>
    <div class="sec">
      <div class="sec-title">Adjustable ({len(adjustable)})</div>
      <div class="sec-sub">Slider chains &amp; open cuffs. No sizing guesswork.</div>
      {cards(adjustable)}
    </div>
  </div>

  <div class="two" style="margin-top:8px;">
    <div class="tip">
      <strong>Ring Shopping Checklist</strong>
      <ul class="cl">
        <li>Measure in the evening, room temperature</li>
        <li>Check brand min size on TinyFit Jewelry</li>
        <li>Read return policy (custom = no returns)</li>
        <li>Order half-size down if between sizes</li>
        <li>Band width: 1&ndash;2 mm for size 2&ndash;4</li>
        <li>Compare brands at tinyfitjewelry/compare</li>
      </ul>
    </div>
    <div class="tip">
      <strong>Bracelet Shopping Checklist</strong>
      <ul class="cl">
        <li>Wrist + 1.5 cm = your bracelet size</li>
        <li>Look for "adjustable" or "slider chain"</li>
        <li>Anklets often fit thin wrists better</li>
        <li>Avoid bangles (they slide off)</li>
        <li>Check if brand carries under 15 cm</li>
        <li>Gorjana &amp; Monica Vinader are great picks</li>
      </ul>
    </div>
  </div>

  <div class="ft">
    <div><strong>TinyFit Jewelry</strong> &bull; humancronadmin.github.io/tiny-fit-jewelry</div>
    <div>All data verified 2026 &bull; Free to share</div>
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
