# TinyFit Jewelry - Spec

> Jewelry size guide & curation for women with tiny fingers and thin wrists.

---

## Basic Info
- **Service Name:** TinyFit Jewelry
- **One-liner:** The only size database for women who wear ring sizes 2-4 and have wrists under 14cm
- **Target Need:** Petite women cannot find jewelry that fits - rings start at size 5, bracelets are 16-18cm standard
- **Type:** Static site (HTML/CSS/JS)
- **Deploy:** GitHub Pages
- **Domain:** humancronadmin.github.io/tiny-fit-jewelry (initial)
- **Language:** English only

---

## Code Base

### Approach: Build from scratch with Tailwind CSS
- **Reason:** No existing repo fits this unique niche well enough. Product comparison repos are too generic. Tailwind gives mobile-first responsive design with minimal code.
- **License:** N/A (original work)

### Reference repos (design inspiration only)
- CodyHouse products-comparison-table: comparison table UI pattern
- Petite Dressing (extrapetite.com): content structure for petite fashion

### Design Reference
- `reference/tiny-fit-jewelry/blueprint.txt`
- Color: monochrome base (#000, #FFF, #F5F5F5) + rose gold accent (#B76E79)
- Font: Inter (sans-serif, clean, modern)
- Layout: fixed header + hero CTA + product grid + comparison tables
- Mobile-first: 480px breakpoint, tap targets 44px+

---

## Core Feature (MVP): Ring Size Database

### What it does
A searchable, filterable database of jewelry brands/products that ACTUALLY carry sizes 2-4 (rings) and under-14cm bracelets.

### Data structure (per product/brand entry)
```
- Brand name
- Product category (ring / bracelet / bangle)
- Minimum size available (US ring size or cm for bracelets)
- Maximum size available
- Price range ($)
- Material (gold, silver, stainless steel, etc.)
- Adjustable? (yes/no)
- Source URL (affiliate link)
- Size chart URL (official brand page)
- Country of origin (highlight Japanese brands)
```

### MVP Pages (4 pages total)
1. **Home / Landing** - Hero + value proposition + CTA to database
2. **Ring Size Guide** - "Best Rings in US Size 2-4: Complete Brand Guide"
3. **Bracelet Guide** - "Bracelets for Wrists Under 14cm: What Actually Stays On"
4. **Brand Database** - Filterable table of all brands with size data

### MVP Excluded (for later)
- Interactive "Fit Finder" tool (enter measurements -> get recommendations)
- User reviews/ratings
- Newsletter signup
- Blog articles beyond the initial 2 guides
- Japanese brand deep-dive article
- Comparison tool (side-by-side products)

---

## Build Instructions

### Step 1: Create project structure
```
tiny-fit-jewelry/
  index.html          -- Landing page
  rings.html          -- Ring size guide article
  bracelets.html      -- Bracelet guide article
  database.html       -- Filterable brand database
  css/style.css       -- Tailwind-based styles
  js/database.js      -- Filter/sort logic for database page
  data/brands.json    -- Brand/product data (drives the database)
  images/             -- (empty initially - use brand logos via affiliate)
```

### Step 2: Landing Page (index.html)
- Hero section:
  - H1: "Finally. Jewelry That Actually Fits."
  - Subheading: "The first size database for ring sizes 2-4 and wrists under 14cm"
  - CTA: "Find Your Fit" -> database.html
- Problem section: "The Problem" - why standard jewelry doesn't fit
- Solution section: "What We Do" - curate verified tiny-size jewelry
- Quick stats: "X brands | Y products | Sizes 2-4 verified"
- Links to ring guide + bracelet guide
- Footer: About, disclaimer (affiliate disclosure)

### Step 3: Ring Guide (rings.html)
- Article format, SEO-optimized for "rings size 2", "rings size 3", "size 3 ring", "rings for small fingers"
- Sections:
  1. Why most rings don't come in size 2-4
  2. How to measure your ring size accurately (diagram)
  3. US vs Japanese vs EU size conversion chart
  4. Top brands that carry sizes 2-4 (with affiliate links)
  5. Japanese brands advantage (Agete, 4C, Nojess, Star Jewelry carry from size 1)
  6. Etsy artisan recommendations
  7. Tips: what ring styles look best on petite fingers

### Step 4: Bracelet Guide (bracelets.html)
- Article format, SEO-optimized for "bracelet for small wrist", "bracelet 14cm", "thin wrist bracelet"
- Sections:
  1. Standard bracelet sizes vs what a 14cm wrist needs
  2. How to measure your wrist accurately
  3. Types that work: adjustable chain, slider, small cuff
  4. The anklet-as-bracelet hack
  5. Top brands for thin wrists (with affiliate links)
  6. Bangle solutions (why they fall off + what to do)

### Step 5: Brand Database (database.html)
- Filter bar: Category (ring/bracelet/all) | Min size | Price range | Material | Adjustable
- Sort: by price, by minimum size, by brand name
- Card grid layout showing brand + key specs + "Shop" affiliate button
- Data loaded from data/brands.json
- No backend needed - client-side JS filtering

### Step 6: brands.json - Initial Data Collection
**CRITICAL: Real data only. No dummy data.**

Data sources (all publicly available):
- Brand websites' official size charts
- Amazon product listings (size options visible)
- Etsy shop listings (size options visible)
- Japanese brand sites (Agete, 4C, Nojess, Star Jewelry, Vendome Aoyama, Bloom, Take-Up)

Initial target: 30+ brands/products across rings and bracelets.

### Step 7: Deploy
```bash
cd projects/tiny-fit-jewelry
git init
git remote add origin https://github.com/HumanCronAdmin/tiny-fit-jewelry.git
git add -A
git commit -m "Initial MVP: TinyFit Jewelry size database"
git push -u origin main
# Enable GitHub Pages in repo settings -> main branch
```

---

## Revenue Model
- **Initial:** Free (all content accessible, build traffic + trust)
- **Revenue:** Affiliate links to brand product pages
  - Amazon Associates: 4% on jewelry (审査中 - approved soon)
  - Etsy Affiliate: 4%
  - Individual brand programs via ShareASale/CJ: 5-15%
  - Ana Luisa: 10-15%
  - Japanese brands: explore Rakuten/A8.net international programs
- **Average order value:** $50-200 (jewelry)
- **Revenue per click estimate:** $2-10 per conversion

---

## SEO Strategy
### Target Keywords (English)
- "rings size 2" / "rings size 3" / "size 3 ring"
- "bracelet for small wrist" / "thin wrist bracelet"
- "jewelry for petite women" / "jewelry for small hands"
- "bracelet 14cm wrist" / "extra small bracelet"
- "best rings for tiny fingers"

### Content-first SEO
- 2 long-form guide articles (1500-2000 words each)
- Schema.org Product markup on database entries
- Internal linking between guides and database

---

## Publish Info

- **Service URL:** https://humancronadmin.github.io/tiny-fit-jewelry
- **Target:** Petite women (under 155cm/5'1") who struggle to find fitting jewelry, especially ring sizes 2-4 and wrist circumference under 14cm
- **Hook:** "I'm 153cm with tiny fingers and wrists. I built the database I wish existed."
- **Subreddits:**
  - r/petitefashion (most relevant)
  - r/femalefashionadvice
  - r/jewelry
  - r/weddingplanning (engagement ring sizing)
  - r/PetiteFashionAdvice
- **Pinterest:** Create board "Jewelry for Tiny Hands & Wrists" with product pins
- **Note article angle:** "Why I built a jewelry size database for women who can't find rings under size 5"

---

## MVP Validation
- **Method:** Post ring guide article link on r/petitefashion + r/jewelry
- **Success criteria:** 10+ upvotes OR 3+ comments asking for more brands/info
- **Timeline:** 1 week after deploy
- **If validated:** Add Fit Finder tool + more brands + blog content
- **If not:** Pivot to broader "petite accessories" or abandon
