/*
  TinyFit Jewelry - Programmatic SEO Page Generator
  brands.json → brand individual pages + size pages
  Run: node generate-pages.js
  Output: /brands/*.html + /size/*.html
*/
const fs = require('fs');
const path = require('path');

const brands = JSON.parse(fs.readFileSync('data/brands.json', 'utf-8'));

// Ensure directories
['brands', 'size'].forEach(d => {
  if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
});

function slug(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function headBlock(title, desc, canonicalPath, schemaJson) {
  const url = `https://humancronadmin.github.io/tiny-fit-jewelry/${canonicalPath}`;
  const schemaTag = schemaJson ? `\n  <script type="application/ld+json">${JSON.stringify(schemaJson)}</script>` : '';
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} | TinyFit Jewelry</title>
  <meta name="description" content="${desc}">
  <link rel="canonical" href="${url}">${schemaTag}
  <meta property="og:title" content="${title} | TinyFit Jewelry">
  <meta property="og:description" content="${desc}">
  <meta property="og:url" content="${url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="TinyFit Jewelry">
  <meta name="twitter:card" content="summary">
  <meta name="theme-color" content="#B76E79">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="manifest" href="../manifest.json">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
</head>`;
}

function nav() {
  return `<nav class="nav">
  <div class="container">
    <a href="../index.html" class="nav-brand">Tiny<span>Fit</span></a>
    <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('active')" aria-label="Menu">&#9776;</button>
    <ul class="nav-links">
      <li><a href="../rings.html">Ring Guide</a></li>
      <li><a href="../bracelets.html">Bracelet Guide</a></li>
      <li><a href="../database.html">Brand Database</a></li>
    </ul>
  </div>
</nav>`;
}

function footer() {
  return `<footer class="footer">
  <div class="container">
    <div class="affiliate-disclosure">
      <strong>Affiliate Disclosure:</strong> Some links on this site are affiliate links. We may earn a small commission if you make a purchase, at no extra cost to you.
    </div>
    <p>&copy; 2026 TinyFit Jewelry. Built for women who know the struggle.</p>
    <p style="margin-top:8px;"><a href="../rings.html">Ring Guide</a> &middot; <a href="../bracelets.html">Bracelet Guide</a> &middot; <a href="../database.html">Database</a> &middot; <a href="../about.html">About</a></p>
  </div>
<!-- Newsletter -->
<div style="text-align:center;padding:24px 12px;margin:24px auto;max-width:600px;background:linear-gradient(135deg,#B76E79 0%,#8B5E6B 100%);border-radius:12px;">
  <p style="font-weight:700;font-size:0.95rem;color:#fff;margin:0 0 8px;">We add new brands every week.</p>
  <p style="font-size:0.82rem;color:rgba(255,255,255,0.85);margin:0 0 12px;">Get notified when a new brand joins the database.</p>
  <form action="https://buttondown.com/api/emails/embed-subscribe/tinyfitjewelry" method="post" target="_blank" style="display:flex;gap:8px;max-width:380px;margin:0 auto;flex-wrap:wrap;justify-content:center;">
    <input type="hidden" name="tag" value="tinyfit">
    <input type="email" name="email" placeholder="your@email.com" required style="flex:1;min-width:180px;padding:10px 14px;border:none;border-radius:8px;font-size:0.9rem;">
    <button type="submit" style="padding:10px 20px;background:#1C1917;color:#fff;border:none;border-radius:8px;font-weight:600;font-size:0.9rem;cursor:pointer;">Subscribe</button>
  </form>
</div>
</footer>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6776399834647681" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-H1N5PR9Y0H"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-H1N5PR9Y0H');</script>
</body></html>`;
}

// === BRAND PAGES ===
let brandPages = 0;
for (const b of brands) {
  const s = slug(b.brand);
  const cats = b.category.join(' & ');
  const hasRing = b.min_ring_size_us !== null;
  const hasBracelet = b.min_bracelet_cm !== null;

  let sizeInfo = '';
  if (hasRing) sizeInfo += `Rings available from US size ${b.min_ring_size_us}. `;
  if (hasBracelet) sizeInfo += `Bracelets from ${b.min_bracelet_cm}cm. `;

  const title = `${b.brand} Petite Jewelry Size Guide`;
  const desc = `${b.brand} size guide for petite women. ${sizeInfo}Price $${b.price_min}-$${b.price_max}. ${b.adjustable ? 'Adjustable options available.' : ''} From ${b.country}.`;

  const brandSchema = {
    "@context": "https://schema.org",
    "@type": "Brand",
    "name": b.brand,
    "url": b.shop_url,
    "description": b.note
  };

  let sizeTags = '';
  if (hasRing) sizeTags += `<span class="tag tag-green">Ring from US ${b.min_ring_size_us}</span> `;
  if (hasBracelet) sizeTags += `<span class="tag tag-green">Bracelet from ${b.min_bracelet_cm}cm</span> `;
  if (b.adjustable) sizeTags += `<span class="tag tag-green">Adjustable</span> `;

  const materialTags = b.materials.map(m => `<span class="tag tag-gold">${m}</span>`).join(' ');

  // Find other brands in same size range for internal links
  const similarBrands = brands.filter(x =>
    x.brand !== b.brand &&
    x.category.some(c => b.category.includes(c)) &&
    (hasRing ? x.min_ring_size_us !== null && x.min_ring_size_us <= (b.min_ring_size_us + 1) : true)
  ).slice(0, 5);

  const similarLinks = similarBrands.map(x =>
    `<li><a href="${slug(x.brand)}.html">${x.brand}</a> (${x.country}${x.min_ring_size_us !== null ? ', ring from US ' + x.min_ring_size_us : ''})</li>`
  ).join('\n        ');

  // Fit Score bar generator
  const fitScore = b.fit_score || {};
  const scoreLabels = {size_range:'Size Range',materials:'Materials',adjustability:'Adjustability',accessibility:'Accessibility',value:'Value'};
  const scoreColors = {5:'#4CAF50',4:'#8BC34A',3:'#FFC107',2:'#FF9800',1:'#F44336'};
  const fitScoreHtml = Object.entries(scoreLabels).map(([key,label]) => {
    const val = fitScore[key] || 0;
    const pct = val * 20;
    return `<div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
      <span style="min-width:100px;font-size:0.82rem;color:var(--muted);">${label}</span>
      <div style="flex:1;background:#eee;border-radius:4px;height:8px;overflow:hidden;">
        <div style="width:${pct}%;height:100%;background:${scoreColors[val]||'#ccc'};border-radius:4px;"></div>
      </div>
      <span style="font-size:0.78rem;font-weight:600;min-width:20px;text-align:right;">${val}/5</span>
    </div>`;
  }).join('\n      ');
  const totalScore = Object.values(fitScore).reduce((a,c)=>a+c,0);
  const maxScore = Object.keys(scoreLabels).length * 5;

  // Recommended products
  const recProds = (b.recommended_products || []).map(p =>
    `<div style="padding:12px;background:var(--surface,#f9f7f5);border-radius:8px;margin:8px 0;">
      <strong style="font-size:0.9rem;">${p.name}</strong>
      <p style="font-size:0.82rem;color:var(--muted);margin:4px 0 0;">${p.why}</p>
    </div>`
  ).join('\n      ');

  const html = `${headBlock(title, desc, `brands/${s}.html`, brandSchema)}
<body>
${nav()}
<article class="article">
  <div class="container narrow">
    <p style="font-size:0.85rem;color:var(--muted);margin-bottom:8px;"><a href="../database.html">&larr; All Brands</a></p>
    <h1>${b.brand} Size Guide for Petite Women</h1>
    <p class="meta">${b.country} &middot; ${cats} &middot; $${b.price_min}&ndash;$${b.price_max}</p>

    ${b.verified ? '<div style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;background:#E8F5E9;border-radius:20px;font-size:0.82rem;font-weight:600;color:#2E7D32;margin:12px 0;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg> Verified by TinyFit</div>' : ''}

    <div class="brand-meta" style="margin:16px 0;">
      ${sizeTags}
    </div>
    <div class="brand-meta" style="margin:12px 0;">
      ${materialTags}
    </div>

    ${b.editorial ? `<h2>Why We Recommend ${b.brand}</h2>
    <p style="line-height:1.7;">${b.editorial}</p>` : ''}

    ${b.petite_tip ? `<div style="padding:16px;background:linear-gradient(135deg,#FFF8E1,#FFF3E0);border-radius:10px;margin:20px 0;border-left:4px solid #FFB74D;">
      <strong style="font-size:0.85rem;">&#128161; Petite Tip:</strong>
      <p style="font-size:0.88rem;margin:6px 0 0;line-height:1.6;">${b.petite_tip}</p>
    </div>` : ''}

    <h2>Petite Fit Score</h2>
    <p style="font-size:0.82rem;color:var(--muted);margin-bottom:12px;">Overall: <strong>${totalScore}/${maxScore}</strong></p>
    <div style="max-width:360px;">
      ${fitScoreHtml}
    </div>

    <h2>Size Availability</h2>
    ${hasRing ? `<p><strong>Rings:</strong> Available from US size ${b.min_ring_size_us}. ${b.min_ring_size_us <= 2 ? 'This is one of the few brands that carries sizes this small for adult women.' : b.min_ring_size_us <= 3 ? 'Size 3 is available, which is smaller than most mainstream brands.' : 'Size 4 is available, though some styles may start at 5.'}</p>` : ''}
    ${hasBracelet ? `<p><strong>Bracelets:</strong> Available from ${b.min_bracelet_cm}cm. ${b.min_bracelet_cm <= 14 ? 'This works for wrists under 14cm without modification.' : 'You may need the smallest setting or an adjustable style for wrists under 14cm.'}</p>` : ''}
    ${b.adjustable ? '<p><strong>Adjustable:</strong> Yes. Some pieces can be adjusted to fit smaller sizes.</p>' : ''}

    ${recProds ? `<h2>Best for Petite Women</h2>
      ${recProds}` : ''}

    <h2>About ${b.brand}</h2>
    <p>${b.note}</p>
    <p><strong>Style:</strong> ${b.style}</p>
    <p><strong>Materials:</strong> ${b.materials.join(', ')}</p>
    <p><strong>Price range:</strong> $${b.price_min} &ndash; $${b.price_max}</p>

    <div style="margin:24px 0;">
      <a href="${b.affiliate_url || b.shop_url}" target="_blank" rel="noopener noreferrer" class="btn">${b.intl_shipping === false ? 'View ' + b.brand + ' (Japan Only)' : 'Visit ' + b.brand}</a>
      ${b.size_chart_url && b.size_chart_url !== b.shop_url ? `<a href="${b.size_chart_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline" style="margin-left:8px;">Size Chart</a>` : ''}
      ${b.amazon_url ? `<a href="${b.amazon_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline" style="margin-left:8px;">Find on Amazon</a>` : ''}
    </div>

    ${similarBrands.length > 0 ? `<h2>Similar Brands in This Size Range</h2>
    <ul>
        ${similarLinks}
    </ul>` : ''}

    <div style="text-align:center;padding:24px 0;">
      <a href="../database.html" class="btn btn-outline">Browse All ${brands.length} Brands</a>
    </div>
  </div>
</article>
${footer()}`;

  fs.writeFileSync(`brands/${s}.html`, html);
  brandPages++;
}

// === SIZE PAGES ===
const sizeGroups = [
  { file: 'ring-size-2.html', title: 'Rings in US Size 2 or Smaller', desc: 'All jewelry brands that carry ring sizes US 2 or smaller. Verified size data for petite women with tiny fingers.', filter: b => b.min_ring_size_us !== null && b.min_ring_size_us <= 2 },
  { file: 'ring-size-3.html', title: 'Rings in US Size 3 or Smaller', desc: 'All jewelry brands that carry ring sizes US 3 or smaller for petite women.', filter: b => b.min_ring_size_us !== null && b.min_ring_size_us <= 3 },
  { file: 'ring-size-4.html', title: 'Rings in US Size 4 or Smaller', desc: 'All jewelry brands that carry ring sizes US 4 or smaller for petite women.', filter: b => b.min_ring_size_us !== null && b.min_ring_size_us <= 4 },
  { file: 'wrist-14cm.html', title: 'Bracelets for Wrists 14cm or Under', desc: 'All bracelet brands verified to fit wrists 14cm and under. No more loose bracelets.', filter: b => b.min_bracelet_cm !== null && b.min_bracelet_cm <= 14 },
  { file: 'wrist-15cm.html', title: 'Bracelets for Wrists 15cm or Under', desc: 'All bracelet brands that work for wrists 15cm and under.', filter: b => b.min_bracelet_cm !== null && b.min_bracelet_cm <= 15 },
  { file: 'adjustable.html', title: 'Adjustable Jewelry for Petite Women', desc: 'All adjustable rings and bracelets that can fit petite sizes. No guessing needed.', filter: b => b.adjustable },
  { file: 'japanese-brands.html', title: 'Japanese Jewelry Brands for Petite Sizes', desc: 'Japanese jewelry brands carry some of the smallest sizes available. Rings from US 1.5, bracelets from 13.5cm.', filter: b => b.country === 'Japan' || b.country === 'Japan/USA' },
  { file: 'under-100.html', title: 'Petite Jewelry Under $100', desc: 'Affordable jewelry in small sizes. Rings size 2-4 and thin wrist bracelets under $100.', filter: b => b.price_min < 100 },
];

let sizePages = 0;
for (const group of sizeGroups) {
  const matching = brands.filter(group.filter);
  const brandList = matching.map(b => {
    const s = slug(b.brand);
    let info = [];
    if (b.min_ring_size_us !== null) info.push(`Ring from US ${b.min_ring_size_us}`);
    if (b.min_bracelet_cm !== null) info.push(`Bracelet from ${b.min_bracelet_cm}cm`);
    return `<div class="brand-card">
      <h3><a href="../brands/${s}.html" style="color:inherit;text-decoration:none;">${b.brand}</a> <span class="country-flag">${b.country}</span></h3>
      <div class="brand-meta">${info.map(i => `<span class="tag tag-green">${i}</span>`).join(' ')} ${b.adjustable ? '<span class="tag tag-green">Adjustable</span>' : ''}</div>
      <div class="price">$${b.price_min} &ndash; $${b.price_max}</div>
      <p class="note">${b.note}</p>
      <a href="${b.affiliate_url || b.shop_url}" target="_blank" rel="noopener noreferrer" class="shop-btn">${b.intl_shipping === false ? 'View (Japan Only)' : 'Visit Brand'}</a>
      ${b.amazon_url ? `<a href="${b.amazon_url}" target="_blank" rel="noopener noreferrer" class="shop-btn shop-btn-amazon" style="margin-left:6px;background:#FF9900;color:#111;">Amazon</a>` : ''}
    </div>`;
  }).join('\n    ');

  const sizeSchema = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": group.title,
    "description": group.desc,
    "numberOfItems": matching.length,
    "itemListElement": matching.map((b, i) => ({
      "@type": "ListItem",
      "position": i + 1,
      "name": b.brand,
      "url": `https://humancronadmin.github.io/tiny-fit-jewelry/brands/${slug(b.brand)}.html`
    }))
  };

  const html = `${headBlock(group.title, group.desc, `size/${group.file}`, sizeSchema)}
<body>
${nav()}
<section style="padding-top:36px;">
  <div class="container">
    <p style="font-size:0.85rem;color:var(--muted);margin-bottom:8px;"><a href="../database.html">&larr; All Brands</a></p>
    <h1 class="section-title">${group.title}</h1>
    <p class="section-subtitle">${matching.length} brand${matching.length !== 1 ? 's' : ''} verified.</p>
    <div class="card-grid">
    ${brandList}
    </div>
    <div style="text-align:center;padding:24px 0;">
      <a href="../database.html" class="btn btn-outline">Browse All ${brands.length} Brands</a>
    </div>
  </div>
</section>
${footer()}`;

  fs.writeFileSync(`size/${group.file}`, html);
  sizePages++;
}

// Update sitemap
const existingSitemap = fs.readFileSync('sitemap.xml', 'utf-8');
let newUrls = '';
for (const b of brands) {
  newUrls += `  <url><loc>https://humancronadmin.github.io/tiny-fit-jewelry/brands/${slug(b.brand)}.html</loc><lastmod>2026-04-05</lastmod><priority>0.6</priority></url>\n`;
}
for (const group of sizeGroups) {
  newUrls += `  <url><loc>https://humancronadmin.github.io/tiny-fit-jewelry/size/${group.file}</loc><lastmod>2026-04-05</lastmod><priority>0.7</priority></url>\n`;
}
const updatedSitemap = existingSitemap.replace('</urlset>', newUrls + '</urlset>');
fs.writeFileSync('sitemap.xml', updatedSitemap);

console.log(`Generated ${brandPages} brand pages + ${sizePages} size pages = ${brandPages + sizePages} total`);
console.log(`Sitemap updated with ${brandPages + sizePages} new URLs`);
