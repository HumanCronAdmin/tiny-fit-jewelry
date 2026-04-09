"""Generate TinyFit Jewelry PDF — dark luxury editorial style.

Consistent dark+gold tone throughout. No page-break mid-content.
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


def brand_card(b):
    name = b["brand"]
    ring = f'Ring US {b["min_ring_size_us"]}' if b.get("min_ring_size_us") else ""
    bracelet = f'Bracelet {b["min_bracelet_cm"]} cm' if b.get("min_bracelet_cm") else ""
    sizes = " | ".join(filter(None, [ring, bracelet]))
    price = f'${b.get("price_min","?")}-${b.get("price_max","?")}'
    badges = []
    if b.get("adjustable"): badges.append("Adj")
    if b.get("intl_shipping"): badges.append("Intl")
    badge_html = " ".join([f'<span class="badge">{x}</span>' for x in badges])
    return f'''<div class="bc">
      <div class="bc-top"><span class="bc-name">{name}</span><span class="bc-loc">{b["country"]}</span></div>
      <div class="bc-mid">{sizes}</div>
      <div class="bc-bot"><span>{price}</span>{badge_html}</div>
    </div>'''


def cards(brand_list):
    return '<div class="grid">' + "".join([brand_card(b) for b in brand_list]) + '</div>'


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Inter:wght@400;500;600;700&display=swap');
@page {{ size: A4; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}

/* ── GLOBAL: dark luxury tone ── */
body {{ font-family:'Inter',sans-serif; background:#1C1917; color:#E7E5E4; font-size:7.5pt; line-height:1.45; }}

/* ── COVER ── */
.cover {{
  width:210mm; height:297mm; page-break-after:always;
  background: linear-gradient(160deg,#0F0E0D 0%,#1C1917 40%,#2D2926 100%);
  display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center; color:#fff; position:relative;
}}
.cover::before {{
  content:''; position:absolute; inset:0;
  background: radial-gradient(ellipse at 30% 25%,rgba(201,169,110,0.15) 0%,transparent 60%),
              radial-gradient(ellipse at 70% 75%,rgba(201,169,110,0.1) 0%,transparent 50%);
}}
.cover *{{ position:relative; }}
.cv-label {{ font-size:8pt; letter-spacing:5px; text-transform:uppercase; color:#C9A96E; margin-bottom:18px; }}
.cover h1 {{ font-family:'Playfair Display',serif; font-size:36pt; font-weight:900; line-height:1.15; margin-bottom:14px; }}
.cover h1 em {{ font-style:italic; color:#C9A96E; }}
.cv-sub {{ font-size:10pt; color:rgba(255,255,255,0.6); max-width:360px; line-height:1.6; }}
.cv-stats {{ display:flex; gap:28px; margin-top:32px; }}
.cv-stat .n {{ font-family:'Playfair Display',serif; font-size:26pt; font-weight:900; color:#C9A96E; }}
.cv-stat .l {{ font-size:6.5pt; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.4); }}
.cv-foot {{ position:absolute; bottom:20px; font-size:6.5pt; color:rgba(255,255,255,0.25); letter-spacing:1px; }}

/* ── CONTENT PAGES ── */
.pg {{ padding:20px 24px 16px; }}
.pg-head {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #333; padding-bottom:5px; margin-bottom:12px; }}
.pg-head .logo {{ font-family:'Playfair Display',serif; font-size:9pt; color:#C9A96E; }}
.pg-head .label {{ font-size:6.5pt; color:#666; letter-spacing:1px; text-transform:uppercase; }}

/* ── SECTIONS ── */
.sec {{ margin-bottom:10px; }}
.sec-head {{ margin-bottom:6px; }}
.sec-title {{ font-family:'Playfair Display',serif; font-size:11pt; color:#C9A96E; }}
.sec-sub {{ font-size:7pt; color:#888; }}

/* ── SIZE TABLE ── */
.st {{ width:100%; border-collapse:separate; border-spacing:0; margin:4px 0 8px; font-size:7pt; border-radius:6px; overflow:hidden; }}
.st th {{ background:#C9A96E; color:#1C1917; padding:5px 7px; text-align:center; font-weight:700; font-size:6.5pt; letter-spacing:0.5px; }}
.st td {{ padding:4px 7px; text-align:center; border-bottom:1px solid #2D2926; background:#242220; }}
.st tr:nth-child(even) td {{ background:#1C1917; }}
.st td:first-child {{ font-weight:700; color:#C9A96E; }}

/* ── BRAND CARDS ── */
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:4px; margin:4px 0; }}
.bc {{
  background:#242220; border:1px solid #333; border-radius:6px; padding:5px 7px;
  page-break-inside:avoid;
}}
.bc-top {{ display:flex; justify-content:space-between; align-items:baseline; }}
.bc-name {{ font-weight:700; font-size:7pt; color:#E7E5E4; }}
.bc-loc {{ font-size:5.5pt; color:#C9A96E; font-weight:600; }}
.bc-mid {{ color:#999; font-size:6pt; margin:2px 0 1px; }}
.bc-bot {{ display:flex; justify-content:space-between; align-items:center; color:#777; font-size:6pt; }}
.badge {{ background:#333; color:#C9A96E; padding:0 4px; border-radius:2px; font-size:5pt; font-weight:600; margin-left:2px; }}

/* ── BOXES ── */
.tip {{
  background:#242220; border:1px solid #333; border-left:3px solid #C9A96E;
  border-radius:0 6px 6px 0; padding:7px 10px; margin:4px 0; font-size:7pt;
}}
.tip strong {{ color:#C9A96E; }}
.formula-box {{
  background:linear-gradient(135deg,#C9A96E,#B8943E); color:#1C1917;
  padding:10px 16px; border-radius:8px; text-align:center; margin:6px 0;
}}
.formula-box .f {{ font-family:'Playfair Display',serif; font-size:13pt; font-weight:900; }}
.formula-box .fd {{ font-size:7pt; margin-top:3px; opacity:0.8; }}

/* ── RULES ── */
.rules {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:4px; margin:5px 0; }}
.rule {{
  background:#242220; border:1px solid #333; border-radius:6px; padding:6px 8px;
  display:flex; gap:6px; align-items:flex-start; font-size:6.5pt;
}}
.rule-n {{
  width:18px; height:18px; border-radius:50%; background:#C9A96E; color:#1C1917;
  display:flex; align-items:center; justify-content:center;
  font-size:7pt; font-weight:700; flex-shrink:0;
}}
.rule strong {{ color:#C9A96E; }}

/* ── TWO COL / CHECKLIST ── */
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.cl {{ list-style:none; font-size:7pt; }}
.cl li {{ padding:2px 0 2px 14px; position:relative; }}
.cl li::before {{ content:'\\2713'; position:absolute; left:0; color:#C9A96E; font-weight:700; }}

/* ── FOOTER ── */
.ft {{
  background:#C9A96E; color:#1C1917; padding:8px 24px;
  display:flex; justify-content:space-between; font-size:6.5pt; font-weight:600;
  margin-top:8px; border-radius:6px;
}}
</style>
</head>
<body>

<!-- ═══ COVER ═══ -->
<div class="cover">
  <div class="cv-label">TinyFit Jewelry Presents</div>
  <h1>The Complete<br>Petite Jewelry<br><em>Size Guide</em></h1>
  <div class="cv-sub">Everything you need to find rings in size 2&ndash;4 and bracelets for wrists under 14 cm.</div>
  <div class="cv-stats">
    <div class="cv-stat"><div class="n">{len(brands)}</div><div class="l">Brands</div></div>
    <div class="cv-stat"><div class="n">9</div><div class="l">Countries</div></div>
    <div class="cv-stat"><div class="n">2026</div><div class="l">Edition</div></div>
  </div>
  <div class="cv-foot">humancronadmin.github.io/tiny-fit-jewelry</div>
</div>

<!-- ═══ PAGE 2: SIZE + RULES ═══ -->
<div class="pg">
  <div class="pg-head"><div class="logo">TinyFit Jewelry</div><div class="label">Size Charts &amp; Styling</div></div>

  <div class="sec">
    <div class="sec-head"><div class="sec-title">Ring Size Conversion</div><div class="sec-sub">US 1&ndash;5 with Japan, UK, EU equivalents</div></div>
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
      <div class="tip"><strong>How to Measure</strong><br>1. Wrap string around finger base<br>2. Mark overlap, measure mm<br>3. Match to chart above<br>4. Evening + room temp = best accuracy<br><em style="color:#C9A96E;">At size 2&ndash;4, half a size &lt; 1.3 mm</em></div>
    </div>
    <div>
      <div class="formula-box"><div class="f">Wrist + 1.5 cm = Perfect Fit</div><div class="fd">13 cm wrist = 14.5 cm bracelet. Standard "small" is 15&ndash;16 cm (too big).</div></div>
      <div class="tip" style="margin-top:4px;"><strong>Anklet Hack:</strong> Adjustable anklets cinch to 14&ndash;15 cm. Perfect for thin wrists.</div>
    </div>
  </div>

  <div class="sec" style="margin-top:8px;">
    <div class="sec-head"><div class="sec-title">6 Styling Rules</div></div>
    <div class="rules">
      <div class="rule"><div class="rule-n">1</div><div><strong>Band under 2 mm.</strong> Thin = elegant on small fingers.</div></div>
      <div class="rule"><div class="rule-n">2</div><div><strong>Stones under 0.5 ct.</strong> Small solitaires flatter petite hands.</div></div>
      <div class="rule"><div class="rule-n">3</div><div><strong>Stack thin rings.</strong> 2&ndash;3 delicate bands &gt; 1 thick ring.</div></div>
      <div class="rule"><div class="rule-n">4</div><div><strong>Bezel over prong.</strong> Lower profile, better proportions.</div></div>
      <div class="rule"><div class="rule-n">5</div><div><strong>Japanese brands first.</strong> Sizes from US 1.5 as standard.</div></div>
      <div class="rule"><div class="rule-n">6</div><div><strong>Skip custom.</strong> $50&ndash;$150 extra. Buy standard stock.</div></div>
    </div>
  </div>
</div>

<!-- ═══ PAGE 3: ALL BRANDS ═══ -->
<div class="pg">
  <div class="pg-head"><div class="logo">TinyFit Jewelry</div><div class="label">Brand Directory &mdash; {len(brands)} Verified Brands</div></div>

  <div class="sec">
    <div class="sec-head"><div class="sec-title">Japanese Brands ({len(jp_brands)})</div><div class="sec-sub">Best for sizes 1&ndash;3. They start where Western brands stop.</div></div>
    {cards(jp_brands)}
  </div>

  <div class="sec">
    <div class="sec-head"><div class="sec-title">Western &amp; International ({len(western_brands)})</div><div class="sec-sub">US, UK, Canada, and more. Growing petite-friendly selection.</div></div>
    {cards(western_brands)}
  </div>
</div>

<!-- ═══ PAGE 4: SPECIAL LISTS + CHECKLISTS ═══ -->
<div class="pg">
  <div class="pg-head"><div class="logo">TinyFit Jewelry</div><div class="label">Special Lists &amp; Quick Reference</div></div>

  <div class="two">
    <div class="sec">
      <div class="sec-head"><div class="sec-title">Ring Size 2 Club ({len(size2)})</div><div class="sec-sub">Hardest size. These carry it as standard.</div></div>
      {cards(size2)}
    </div>
    <div class="sec">
      <div class="sec-head"><div class="sec-title">Adjustable ({len(adjustable)})</div><div class="sec-sub">Slider chains &amp; open cuffs. No sizing stress.</div></div>
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
    <div>TinyFit Jewelry &bull; humancronadmin.github.io/tiny-fit-jewelry</div>
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
