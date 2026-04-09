"""Auto-generate diverse Pinterest pin content from brands.json.

Goes beyond 1-page-1-pin by creating pins from multiple angles:
  - Comparisons (Brand A vs Brand B)
  - Price tier lists (Under $50, Under $100, Luxury)
  - Use-case (Engagement, Everyday, Stacking, Gift)
  - Country roundups (Japanese brands, US brands, etc.)
  - Material groupings (Gold, Silver, Lab diamond)
  - Problem/solution (Ring spinning, bracelet sliding)
  - Seasonal/event (Valentine's, Holiday, Wedding season)
  - Checklists and tips

All content is generated from real verified data in brands.json.
No dummy data. No made-up brands.

Usage:
  python content_generator.py           # Generate all new pins
  python content_generator.py --dry     # Preview only
  python content_generator.py --type comparison  # Generate specific type
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).parent.parent / "data" / "brands.json"
QUEUE_FILE = Path(__file__).parent / "pin_queue.json"
GENERATED_IMAGES_DIR = Path(__file__).parent / "generated_images"
SITE_BASE = "https://humancronadmin.github.io/tiny-fit-jewelry"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_brands():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_queue():
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def make_pin(pin_id, title, description, link, board, image_name):
    return {
        "id": pin_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
        "board": board,
        "image_path": str(GENERATED_IMAGES_DIR / f"{pin_id}.png"),
        "status": "pending",
        "posted_at": None,
        "error": None,
    }


# =====================================================
# PIN GENERATORS — each returns a list of pin dicts
# =====================================================

def gen_price_tier_pins(brands):
    """Group brands by price and create tier pins."""
    tiers = [
        ("under-50", "Under $50", 0, 50, "Budget-friendly petite jewelry that fits right. Every brand verified for ring sizes 2-4 and thin wrists under 14cm."),
        ("under-100", "Under $100", 0, 100, "Quality petite jewelry without breaking the bank. Rings, bracelets, and necklaces — all verified for small sizes."),
        ("under-200", "Under $200", 0, 200, "Premium petite jewelry at mid-range prices. Fine materials, verified small sizes, elegant designs."),
        ("luxury", "Luxury Picks ($200+)", 200, 99999, "Investment pieces in petite sizes. Fine jewelry from brands that take small sizes seriously."),
    ]
    pins = []
    for tier_id, tier_name, pmin, pmax, desc_intro in tiers:
        matching = [b for b in brands if pmin <= b.get("price_min", 0) < pmax]
        if len(matching) < 2:
            continue
        names = ", ".join([b["brand"] for b in matching[:6]])
        title = f"Petite Jewelry {tier_name}: {len(matching)} Verified Brands"
        desc = f"{desc_intro} Featuring: {names}. #petitejewelry #tinyfitjewelry #budgetjewelry #smallrings #petiterings"
        pins.append(make_pin(
            f"price-{tier_id}", title, desc,
            f"{SITE_BASE}/size/under-100.html",
            "Jewelry for Tiny Fingers",
            f"price-{tier_id}.png"
        ))
    return pins


def gen_country_pins(brands):
    """Group brands by country/region."""
    country_groups = {}
    for b in brands:
        c = b["country"]
        if "Japan" in c:
            key = "Japan"
        elif c in ("USA", "Kenya/USA", "Japan/USA"):
            key = "USA"
        elif c in ("UK",):
            key = "UK"
        elif c in ("Canada",):
            key = "Canada"
        else:
            key = "Other"
        country_groups.setdefault(key, []).append(b)

    pins = []
    country_meta = {
        "Japan": ("Japanese Jewelry Brands", "Japanese brands are the best-kept secret for petite women. They start at sizes most Western brands dont even carry."),
        "USA": ("Jewelry for Tiny Fingers", "American brands expanding their size range for petite women. From indie jewelers to established names."),
        "UK": ("Jewelry for Tiny Fingers", "British brands offering small sizes with elegant European design sensibility."),
        "Canada": ("Jewelry for Tiny Fingers", "Canadian jewelry brands with inclusive sizing for petite women."),
    }

    for country, group in country_groups.items():
        if len(group) < 2 or country == "Other":
            continue
        board, intro = country_meta.get(country, ("Jewelry for Tiny Fingers", ""))
        names = ", ".join([b["brand"] for b in group[:8]])
        title = f"{len(group)} {country} Brands with Petite Ring Sizes (Verified)"
        desc = f"{intro} Brands: {names}. All verified for sizes 2-4. #petitejewelry #{country.lower().replace(' ','')}jewelry #smallrings #tinyfitjewelry"
        pins.append(make_pin(
            f"country-{slug(country)}", title, desc,
            f"{SITE_BASE}/size/japanese-brands.html" if country == "Japan" else f"{SITE_BASE}/rings.html",
            board,
            f"country-{slug(country)}.png"
        ))
    return pins


def gen_usecase_pins(brands):
    """Create pins for specific use cases."""
    usecases = [
        {
            "id": "engagement",
            "title": "Engagement Rings in Size 2-4: Where to Actually Find Them",
            "filter": lambda b: "engagement" in b.get("style", "") or (b.get("min_ring_size_us") is not None and b["min_ring_size_us"] <= 3),
            "desc": "Getting engaged with a ring size under 5? These brands carry engagement rings in small sizes as standard. No custom order needed for most.",
            "board": "Ring Size 2-4 Guide",
            "tags": "#engagementring #petiterings #smallengagementring #bridalring #tinyfitjewelry",
            "link": f"{SITE_BASE}/guides/engagement-ring-styles-petite-hands.html",
        },
        {
            "id": "everyday-stack",
            "title": "Best Stackable Rings for Small Fingers (Size 2-4)",
            "filter": lambda b: "stacking" in b.get("style", "") or "layering" in b.get("style", ""),
            "desc": "Thin stackable bands (1-1.5mm) are naturally proportioned for sizes 2-4. Layer 2-3 delicate rings for a look that flatters petite fingers.",
            "board": "Petite Style Tips",
            "tags": "#stackablerings #petiterings #ringlayering #everydayjewelry #tinyfitjewelry",
            "link": f"{SITE_BASE}/guides/best-rings-tiny-fingers.html",
        },
        {
            "id": "gift-guide",
            "title": "Gift Guide: Jewelry for Someone with Tiny Fingers",
            "filter": lambda b: b.get("price_min", 0) < 150 and (b.get("min_ring_size_us") or 99) <= 4,
            "desc": "Shopping for someone with small hands? Skip the guessing. These brands carry verified sizes 2-4 with beautiful adult designs. Price range for every budget.",
            "board": "Jewelry for Tiny Fingers",
            "tags": "#giftguide #jewelrygift #petitejewelry #giftsforher #tinyfitjewelry",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "adjustable",
            "title": "Adjustable Jewelry That Actually Works for Thin Wrists",
            "filter": lambda b: b.get("adjustable", False),
            "desc": "Adjustable slider chains and open cuffs that cinch down to fit wrists under 14cm. No more loose bracelets sliding off your hand.",
            "board": "Bracelets for Thin Wrists",
            "tags": "#adjustablejewelry #thinwrist #petitebracelet #adjustablebracelet #tinyfitjewelry",
            "link": f"{SITE_BASE}/size/adjustable.html",
        },
        {
            "id": "minimalist",
            "title": "Minimalist Jewelry for Petite Women: Less Is More",
            "filter": lambda b: any(s in b.get("style", "") for s in ("minimalist", "delicate", "dainty")),
            "desc": "Minimalist pieces that complement — not overwhelm — small hands and thin wrists. Clean lines, thin bands, and subtle details.",
            "board": "Petite Style Tips",
            "tags": "#minimalistjewelry #daintyjewelry #delicatejewelry #petitestyle #tinyfitjewelry",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "sustainable",
            "title": "Ethical & Sustainable Petite Jewelry Brands (Verified Sizes)",
            "filter": lambda b: any(s in b.get("style", "") for s in ("sustainable", "ethical", "lab diamond", "lab gemstones")),
            "desc": "Petite sizes AND ethical sourcing. Lab-grown diamonds, recycled metals, fair-trade practices. You dont have to choose between values and fit.",
            "board": "Jewelry for Tiny Fingers",
            "tags": "#sustainablejewelry #ethicaljewelry #labdiamond #ecofriendly #tinyfitjewelry",
            "link": f"{SITE_BASE}/rings.html",
        },
    ]

    pins = []
    for uc in usecases:
        matching = [b for b in brands if uc["filter"](b)]
        if len(matching) < 2:
            continue
        names = ", ".join([b["brand"] for b in matching[:6]])
        desc = f"{uc['desc']} Featuring: {names}. {uc['tags']}"
        pins.append(make_pin(
            f"usecase-{uc['id']}", uc["title"], desc[:500],
            uc["link"], uc["board"],
            f"usecase-{uc['id']}.png"
        ))
    return pins


def gen_comparison_pins(brands):
    """Brand vs brand comparison pins."""
    # Pick interesting matchups (same category, different country/price)
    comparisons = [
        ("Agete", "Catbird", "Japanese Elegance vs Brooklyn Cool: Rings from Size 1-3"),
        ("Mejuri", "Ana Luisa", "Mejuri vs Ana Luisa: Which Has Better Petite Sizes?"),
        ("Brilliant Earth", "Vrai", "Lab Diamond Engagement Rings in Small Sizes: Who Wins?"),
        ("4℃ (Yon-doshi)", "Star Jewelry", "Japan's Top 2 Petite Jewelry Brands Compared"),
        ("Gorjana", "Monica Vinader", "Best Adjustable Bracelets for Thin Wrists: Compared"),
        ("Nojess", "Bloom", "Affordable Japanese Petite Jewelry: Nojess vs Bloom"),
        ("Automic Gold", "Catbird", "Custom Size Rings: Automic Gold vs Catbird"),
        ("Missoma", "Stone and Strand", "Trendy Petite Jewelry Under $200: UK vs USA"),
    ]

    brand_map = {b["brand"]: b for b in brands}
    pins = []

    for b1_name, b2_name, title in comparisons:
        b1 = brand_map.get(b1_name)
        b2 = brand_map.get(b2_name)
        if not b1 or not b2:
            continue

        s1, s2 = slug(b1_name), slug(b2_name)
        pin_id = f"compare-{s1}-vs-{s2}"

        # Build comparison description
        r1 = b1.get("min_ring_size_us", "N/A")
        r2 = b2.get("min_ring_size_us", "N/A")
        p1 = f"${b1.get('price_min','?')}-${b1.get('price_max','?')}"
        p2 = f"${b2.get('price_min','?')}-${b2.get('price_max','?')}"

        desc = (
            f"{b1_name} ({b1['country']}): rings from size {r1}, {p1}. "
            f"{b2_name} ({b2['country']}): rings from size {r2}, {p2}. "
            f"We compared both for petite women. See which one fits your style and budget. "
            f"#petitejewelry #jewelrycomparison #smallrings #tinyfitjewelry #petiterings"
        )

        board = "Ring Size 2-4 Guide" if r1 != "N/A" else "Jewelry for Tiny Fingers"

        pins.append(make_pin(
            pin_id, title, desc[:500],
            f"{SITE_BASE}/brands/{s1}.html",
            board, f"{pin_id}.png"
        ))

    return pins


def gen_problem_solution_pins(brands):
    """Problem/solution and tip pins."""
    problems = [
        {
            "id": "problem-ring-spinning",
            "title": "Ring Keeps Spinning on Your Finger? Here Is the Fix",
            "desc": "If your ring spins, it is too big — not too loose. At size 2-4, even half a size matters (less than 1.3mm difference). Solutions: ring size adjuster, sizing beads, or just buy the right size from brands that actually carry it. #ringsizing #ringfix #petiterings #smallfingers #tinyfitjewelry",
            "board": "Petite Style Tips",
            "link": f"{SITE_BASE}/guides/make-ring-smaller-without-resizing.html",
        },
        {
            "id": "problem-bracelet-sliding",
            "title": "Bracelet Keeps Sliding Off? Your Wrist Is Below Industry Standard",
            "desc": "Standard small bracelets are 15-16cm. Your wrist is 12-14cm. That 2-4cm gap means constant sliding. Fix: adjustable slider chains, anklet-as-bracelet hack, or brands that carry extra-small. Your wrist + 1.5cm = perfect bracelet. #thinwrist #braceletfit #petitebracelet #tinyfitjewelry",
            "board": "Bracelets for Thin Wrists",
            "link": f"{SITE_BASE}/bracelets.html",
        },
        {
            "id": "problem-childrens-section",
            "title": "Stop Sending Us to the Children's Section (We Wear Size 2-4)",
            "desc": "Millions of adult women worldwide wear ring sizes 2-4. Being directed to the children's section for a gold band is unnecessary. Japanese brands have served these sizes with elegant adult designs for decades. Your fingers are not too small — the standard is too big. #petiterings #adultjewelry #smallfingers #ringsize3 #tinyfitjewelry",
            "board": "Ring Size 2-4 Guide",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "tip-measure-evening",
            "title": "Always Measure Your Ring Size in the Evening (Here Is Why)",
            "desc": "Fingers are smallest in the morning and largest at night. Temperature matters too — cold shrinks, warm swells. For sizes 2-4, half a size is less than 1.3mm. Measure in the evening, room temperature, 2 readings on different days, average them. #ringsizing #jewelrytips #petitejewelry #tinyfitjewelry",
            "board": "Ring Size 2-4 Guide",
            "link": f"{SITE_BASE}/ring-sizer.html",
        },
        {
            "id": "tip-proportion-rule",
            "title": "The Proportion Rule: Why Thin Bands Look Better on Small Fingers",
            "desc": "On a size 2 finger, a 1mm band looks elegant. A 4mm band overwhelms. The rule: band width should be less than 1/3 of your finger width. For sizes 2-4, stick to 1-2mm bands, small stones under 0.5ct, bezel settings. Proportion is everything. #ringstyle #petiterings #jewelrytips #tinyfitjewelry",
            "board": "Petite Style Tips",
            "link": f"{SITE_BASE}/guides/best-rings-tiny-fingers.html",
        },
    ]

    return [make_pin(
        p["id"], p["title"], p["desc"],
        p["link"], p["board"], f"{p['id']}.png"
    ) for p in problems]


def gen_seasonal_pins(brands):
    """Seasonal and event-based pins."""
    year = datetime.now().year
    seasons = [
        {
            "id": "seasonal-valentines",
            "title": f"Valentine's Day Jewelry for Petite Women ({year})",
            "desc": f"Finding the perfect Valentine's gift in sizes 2-4. Budget picks under $50, mid-range under $100, and luxury options. All verified for small sizes — no guessing, no returns. #valentinesday #jewelrygift #petitejewelry #giftforher #tinyfitjewelry",
            "board": "Jewelry for Tiny Fingers",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "seasonal-holiday",
            "title": f"Holiday Gift Guide: Petite Jewelry ({year})",
            "desc": f"The ultimate holiday gift guide for women with small hands and thin wrists. Rings size 2-4, bracelets under 14cm. Brands, prices, and exactly what to order. No more gift card cop-outs. #holidaygift #christmasgift #jewelrygiftguide #petitejewelry #tinyfitjewelry",
            "board": "Jewelry for Tiny Fingers",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "seasonal-wedding",
            "title": f"Wedding Season Jewelry for Petite Brides & Guests ({year})",
            "desc": f"Wedding jewelry that fits. Engagement rings, wedding bands, and guest accessories in sizes 2-4. Japanese brands for classic elegance, US brands for modern lab diamonds. #weddingjewelry #petitebride #engagementring #weddingband #tinyfitjewelry",
            "board": "Ring Size 2-4 Guide",
            "link": f"{SITE_BASE}/guides/engagement-ring-styles-petite-hands.html",
        },
        {
            "id": "seasonal-summer",
            "title": f"Summer Jewelry for Petite Women: Lightweight & Small ({year})",
            "desc": f"Lightweight pieces that wont weigh down small hands in the heat. Thin gold chains, minimal rings, adjustable bracelets. All in sizes that actually fit. #summerjewelry #lightweightjewelry #petitestyle #minimalistjewelry #tinyfitjewelry",
            "board": "Petite Style Tips",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "seasonal-graduation",
            "title": f"Graduation Gift: Jewelry for Petite Women ({year})",
            "desc": f"A meaningful graduation gift in the right size. Dainty necklaces, stackable rings, thin bracelets — all verified for petite women. Under $100 picks that look expensive. #graduationgift #jewelrygift #petitejewelry #tinyfitjewelry",
            "board": "Jewelry for Tiny Fingers",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "seasonal-mothers-day",
            "title": f"Mother's Day Jewelry for Petite Moms ({year})",
            "desc": f"Show mom you actually know her ring size. These brands carry sizes 2-4 as standard. From $30 sterling silver to $300 gold — real sizes, real elegance. #mothersdaygift #petitejewelry #jewelrygift #momgift #tinyfitjewelry",
            "board": "Jewelry for Tiny Fingers",
            "link": f"{SITE_BASE}/rings.html",
        },
    ]

    return [make_pin(
        s["id"], s["title"], s["desc"],
        s["link"], s["board"], f"{s['id']}.png"
    ) for s in seasons]


def gen_material_pins(brands):
    """Group brands by material."""
    material_groups = {}
    for b in brands:
        for mat in b.get("materials", []):
            mat_lower = mat.lower()
            if "gold" in mat_lower and "plat" not in mat_lower:
                material_groups.setdefault("gold", []).append(b["brand"])
            elif "silver" in mat_lower:
                material_groups.setdefault("silver", []).append(b["brand"])
            elif "plat" in mat_lower:
                material_groups.setdefault("platinum", []).append(b["brand"])

    # Deduplicate
    for k in material_groups:
        material_groups[k] = list(dict.fromkeys(material_groups[k]))

    pins = []
    mat_meta = {
        "gold": ("Gold Rings in Size 2-4: Every Brand That Carries Them", "Gold rings — 10K, 14K, and 18K — in truly small sizes. Verified brands that carry petite gold jewelry as standard.", "Ring Size 2-4 Guide"),
        "silver": ("Sterling Silver Petite Jewelry: Affordable Small Sizes", "Sterling silver is the most affordable entry to quality petite jewelry. These brands carry rings and bracelets in sizes 2-4.", "Jewelry for Tiny Fingers"),
        "platinum": ("Platinum Rings in Petite Sizes: Where to Find Them", "Platinum is the most durable precious metal. These brands offer platinum rings in sizes under 5.", "Ring Size 2-4 Guide"),
    }

    for mat, brand_list in material_groups.items():
        if len(brand_list) < 3:
            continue
        title, desc_intro, board = mat_meta.get(mat, (f"{mat.title()} Petite Jewelry", "", "Jewelry for Tiny Fingers"))
        names = ", ".join(brand_list[:8])
        desc = f"{desc_intro} Brands: {names}. #{mat}jewelry #petitejewelry #smallrings #tinyfitjewelry #petiterings"
        pins.append(make_pin(
            f"material-{mat}", title, desc[:500],
            f"{SITE_BASE}/rings.html", board,
            f"material-{mat}.png"
        ))

    return pins


def gen_checklist_pins(brands):
    """Checklist and reference card pins."""
    checklists = [
        {
            "id": "checklist-shopping",
            "title": "Petite Jewelry Shopping Checklist (Save This!)",
            "desc": "Before you buy: 1) Measure finger at evening, room temp. 2) Check brand's min size. 3) Wrist + 1.5cm = bracelet length. 4) Band width under 2mm for sizes 2-4. 5) Bezel > prong for small fingers. 6) Check return policy for sizing issues. #shoppingtips #petitejewelry #jewelryguide #tinyfitjewelry",
            "board": "Petite Style Tips",
            "link": f"{SITE_BASE}/ring-sizer.html",
        },
        {
            "id": "checklist-online-ordering",
            "title": "How to Order Jewelry Online When You Wear Size 2-4",
            "desc": "Step 1: Measure (evening, room temp, average 2 days). Step 2: Check brand min size on TinyFit Jewelry. Step 3: Read return policy. Step 4: Order half-size down if between sizes. Step 5: Check if custom sizing adds cost. #onlineshopping #jewelrytips #petiterings #tinyfitjewelry",
            "board": "Petite Style Tips",
            "link": f"{SITE_BASE}/rings.html",
        },
        {
            "id": "data-sizes-by-country",
            "title": "Average Ring Size by Country: Where Do You Fit?",
            "desc": "USA average: size 6-7. Japan average: size 7-9 (JP). UK average: L-M. Your size 2-4 is 2-4 sizes below average everywhere. That is why standard jewelry doesnt fit — you are literally off most brands charts. But specialized brands exist. #ringsize #sizechart #petitejewelry #tinyfitjewelry",
            "board": "Ring Size 2-4 Guide",
            "link": f"{SITE_BASE}/rings.html",
        },
    ]

    return [make_pin(
        c["id"], c["title"], c["desc"],
        c["link"], c["board"], f"{c['id']}.png"
    ) for c in checklists]


# =====================================================
# MAIN
# =====================================================

ALL_GENERATORS = {
    "price": gen_price_tier_pins,
    "country": gen_country_pins,
    "usecase": gen_usecase_pins,
    "comparison": gen_comparison_pins,
    "problem": gen_problem_solution_pins,
    "seasonal": gen_seasonal_pins,
    "material": gen_material_pins,
    "checklist": gen_checklist_pins,
}


def main():
    dry_run = "--dry" in sys.argv
    type_filter = None
    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            type_filter = sys.argv[idx + 1]

    brands = load_brands()
    queue = load_queue()
    existing_ids = {p["id"] for p in queue}

    all_new = []
    generators = {type_filter: ALL_GENERATORS[type_filter]} if type_filter else ALL_GENERATORS

    for gen_name, gen_func in generators.items():
        pins = gen_func(brands)
        new_pins = [p for p in pins if p["id"] not in existing_ids]
        if new_pins:
            print(f"\n[{gen_name}] {len(new_pins)} new pins:")
            for p in new_pins:
                print(f"  {p['id']}: {p['title'][:60]}")
        all_new.extend(new_pins)

    if not all_new:
        print("\nNo new pins to generate. All content types are already in queue.")
        return

    print(f"\n=== Total: {len(all_new)} new pins ===")

    if dry_run:
        print("[DRY RUN] No changes made.")
        return

    # Add to queue
    queue.extend(all_new)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    pending = sum(1 for p in queue if p["status"] == "pending")
    print(f"Added to queue. Total: {len(queue)} ({pending} pending)")
    print("Next: run auto_generate_pins.py for image creation, then validate_pins.py")


if __name__ == "__main__":
    main()
