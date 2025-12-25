#!/usr/bin/env python3
"""
Static site generator (no JS) for a single-service, multi-city site.

Cloudflare Pages:
- Build command: (empty)
- Output directory: public

URL structure:
- /<city>-<state>/  e.g. /los-angeles-ca/

SEO rules enforced:
- Exactly one H1 per page
- <title> == H1
- Title <= 70 characters
- Controlled H2 set (city pages only use headings from H2_HEADINGS)
- Avoid over-repeating city name in body copy
- Cost section near the bottom
- Natural CTA at the bottom (exact line required)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html
import re


# -----------------------
# CONFIG
# -----------------------
@dataclass(frozen=True)
class SiteConfig:
    # Keep service_name simple for city-page H1s ("{service} in City, ST")
    service_name: str = "Poison Ivy Removal"
    brand_name: str = "Ivy Removal Company"
    cta_text: str = "Get Free Estimate"
    cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"
    output_dir: Path = Path("public")

    # Cost is highly variable; use a conservative, non-sensational range
    cost_low: int = 500
    cost_high: int = 1500


CONFIG = SiteConfig()

# Controlled H2 set (city pages ONLY pull headings from this list)
# Built to match common search intent: identify, yard spread, DIY vs pro, herbicide, landscapers, cost, service area.
H2_HEADINGS = [
    "Poison Ivy vs English Ivy: what’s the difference",
    "How to identify poison ivy",
    "How poison ivy spreads and why it comes back",
    "Can you pull poison ivy yourself?",
    "Should you spray herbicide first?",
    "Do landscapers remove poison ivy?",
    "Poison ivy removal cost",
    "Service area",
]

CITIES: list[tuple[str, str]] = [
    ("Los Angeles", "CA"),
    ("New York", "NY"),
    ("Chicago", "IL"),
    ("Houston", "TX"),
    ("Phoenix", "AZ"),
    ("Philadelphia", "PA"),
    ("San Antonio", "TX"),
    ("San Diego", "CA"),
    ("Dallas", "TX"),
    ("San Jose", "CA"),
    ("Austin", "TX"),
    ("Jacksonville", "FL"),
    ("Fort Worth", "TX"),
    ("Columbus", "OH"),
    ("Charlotte", "NC"),
    ("San Francisco", "CA"),
    ("Indianapolis", "IN"),
    ("Seattle", "WA"),
    ("Denver", "CO"),
    ("Washington", "DC"),
]

# Prefer a local image so it always works on Cloudflare Pages.
# You can replace these files with ivy-specific photos later without changing code.
LOCAL_IMAGE_CITY = "/assets/door-viewer.jpg"
LOCAL_IMAGE_HOME = "/assets/front-door.jpg"


# -----------------------
# HELPERS
# -----------------------
def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"&", " and ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def city_state_slug(city: str, state: str) -> str:
    return f"{slugify(city)}-{slugify(state)}"


def clamp_title(title: str, max_chars: int = 70) -> str:
    if len(title) <= max_chars:
        return title
    return title[: max_chars - 1].rstrip() + "…"


def make_city_h1(service: str, city: str, state: str) -> str:
    return clamp_title(f"{service} in {city}, {state}", 70)


def toolbar_html() -> str:
    return f"""
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/">{esc(CONFIG.brand_name)}</a>
    <div class="topbar-actions">
      <a class="toplink" href="/">Home</a>
      <a class="btn btn-top" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    </div>
  </div>
</div>
""".rstrip()


CSS = """
:root {
  --bg: #0b1b33;
  --bg2: #102a4d;
  --text: #0f172a;
  --muted: #475569;
  --card: #ffffff;
  --line: #e2e8f0;
  --cta: #f97316;
  --cta-hover: #ea580c;
  --max: 980px;
  --radius: 14px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
  color: var(--text);
  background: #f8fafc;
  line-height: 1.55;
  padding-top: 58px; /* room for fixed toolbar */
}

/* Fixed top toolbar (all pages) */
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 58px;
  background: rgba(255,255,255,0.98);
  border-bottom: 1px solid var(--line);
  z-index: 999;
  backdrop-filter: blur(8px);
}

.topbar-inner {
  max-width: var(--max);
  margin: 0 auto;
  height: 100%;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.brand {
  font-weight: 800;
  text-decoration: none;
  color: #0b1b33;
  letter-spacing: -0.01em;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.toplink {
  text-decoration: none;
  color: #0f172a;
  font-size: 13px;
}

header {
  background: linear-gradient(135deg, var(--bg), var(--bg2));
  color: white;
  padding: 44px 18px 34px;
}

.wrap { max-width: var(--max); margin: 0 auto; }

.hero {
  display: grid;
  gap: 14px;
  justify-items: center;
  text-align: center;
}

.hero h1 {
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.01em;
}

.sub {
  margin: 0;
  color: rgba(255,255,255,0.86);
  max-width: 68ch;
  font-size: 14px;
}

.btn {
  display: inline-block;
  padding: 10px 14px;
  background: var(--cta);
  color: white;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 800;
  font-size: 13px;
  border: 0;
}

.btn:hover { background: var(--cta-hover); }

.btn-top { padding: 9px 12px; }

main { padding: 24px 18px 42px; }

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: 0 8px 20px rgba(2, 6, 23, 0.05);
}

.grid { display: grid; gap: 16px; }

.img {
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.img img { display: block; width: 100%; height: auto; }

h2 {
  font-size: 16px;
  margin: 18px 0 8px;
  letter-spacing: -0.01em;
}

p { margin: 0 0 10px; color: var(--text); }
ul { margin: 10px 0 14px 18px; color: var(--text); }
li { margin: 6px 0; }

hr { border: none; border-top: 1px solid var(--line); margin: 18px 0; }

.muted { color: var(--muted); font-size: 13px; }

footer {
  background: linear-gradient(135deg, var(--bg), var(--bg2));
  color: rgba(255,255,255,0.9);
  padding: 34px 18px;
}

.footer-card { max-width: var(--max); margin: 0 auto; text-align: center; }

.footer-card h2 { color: white; margin: 0 0 10px; font-size: 18px; }

.footer-card p { color: rgba(255,255,255,0.85); }

.small { margin-top: 18px; font-size: 12px; color: rgba(255,255,255,0.7); }

.links a {
  color: rgba(255,255,255,0.9);
  text-decoration: underline;
  margin: 0 10px;
  font-size: 13px;
}

.pill {
  display: inline-block;
  padding: 4px 10px;
  background: #eef2ff;
  border: 1px solid #e0e7ff;
  color: #1e3a8a;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 14px;
}

.table th, .table td {
  text-align: left;
  padding: 10px 10px;
  border-top: 1px solid var(--line);
  vertical-align: top;
}

.table th {
  color: #0f172a;
  background: #f1f5f9;
  border-top: 1px solid var(--line);
}

/* Clean city buttons (simple, uncluttered) */
.city-grid {
  list-style: none;
  padding: 0;
  margin: 10px 0 0;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.city-grid a {
  display: block;
  text-decoration: none;
  color: #0f172a;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 700;
  font-size: 14px;
}

.city-grid a:hover {
  border-color: #cbd5e1;
}
""".strip()


# -----------------------
# HTML SHELL
# -----------------------
def base_html(*, title: str, canonical_path: str, description: str, body_inner: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(canonical_path)}" />
  <style>
{CSS}
  </style>
</head>
<body>
{toolbar_html()}
{body_inner}
</body>
</html>
"""


# -----------------------
# CONTENT BLOCKS (reused)
# -----------------------
def curated_intro(*, city: str | None = None, state: str | None = None) -> str:
    # Light local mention only on city pages; keep it simple and avoid repeating city name.
    if city and state:
        local = f" We serve homeowners in {esc(city)}, {esc(state)} and nearby areas."
    else:
        local = ""
    return f"""
<p>
  If ivy has started to spread across your yard, fence, or trees, it can turn into a bigger problem than it looks.
  It spreads through runners and roots, and it can come back after a quick cut.{local}
</p>
<p>
  Poison ivy also carries urushiol, an oil that can trigger a rash after contact. If anyone in your home reacts to it,
  you want the plant gone and you want it gone for good.
</p>
<p>
  We remove poison ivy, English ivy, and heavy vines. We focus on the roots, not just the leaves.
</p>
""".strip()


def section_poison_vs_english_ivy() -> str:
    return f"""
<h2>{esc(H2_HEADINGS[0])}</h2>
<p>
  Poison ivy is a native plant that can trigger a rash in many people. English ivy is a different species.
  It often climbs trees, walls, and fences. Both can spread fast.
</p>
<p>
  A good plan depends on what you have and where it grows. Ground cover needs root removal.
  Climbing ivy needs careful work so you do not damage bark, siding, or fences.
</p>
""".strip()


def section_identify_poison_ivy() -> str:
    return f"""
<h2>{esc(H2_HEADINGS[1])}</h2>
<p>
  People say “leaves of three,” and that helps, but it is not the only clue.
  Look for clusters of three leaflets, uneven edges, and vines with small aerial root hairs.
</p>
<ul>
  <li>Three leaflets per leaf cluster</li>
  <li>Uneven or jagged leaflet edges on many plants</li>
  <li>Hairy-looking vines on trees or fences</li>
  <li>Small green flowers in spring on some plants</li>
  <li>White or yellow berries later in the season</li>
</ul>
<p class="muted">
  If you are not sure what you are seeing, do not handle it with bare skin.
</p>
""".strip()


def section_spread_and_return() -> str:
    return f"""
<h2>{esc(H2_HEADINGS[2])}</h2>
<p>
  Ivy spreads through roots, runners, and seed. A cut vine can still leave roots in the soil.
  That is why it returns after a simple trim or a quick pull.
</p>
<p>
  Long-term removal means you stop new growth, remove root sections where possible,
  and monitor the area for regrowth.
</p>
""".strip()


def section_can_you_pull_it() -> str:
    return f"""
<h2>{esc(H2_HEADINGS[3])}</h2>
<p>
  You can pull small patches if you protect your skin and you remove the roots.
  The risk is exposure to urushiol and missed root pieces that sprout again.
</p>
<p>
  If the plant has spread across a yard, into brush, or up trees, the job gets harder.
  At that point, many people choose a pro so the work stays contained.
</p>
""".strip()


def section_herbicide_first() -> str:
    return f"""
<h2>{esc(H2_HEADINGS[4])}</h2>
<p>
  Many people want to spray first. In many cases, that does not help.
  It can also spread residue onto tools, gloves, and nearby plants.
</p>
<p>
  A better approach is to keep the area undisturbed until removal day.
  After that, a pro can decide if targeted treatment makes sense for regrowth.
</p>
""".strip()


def section_landscapers() -> str:
    return f"""
<h2>{esc(H2_HEADINGS[5])}</h2>
<p>
  Some landscapers remove ivy. Others cut it back or bury it during cleanup.
  If the roots stay, the plant often returns.
</p>
<p>
  If you hire help, ask how they handle roots, disposal, and follow-up regrowth.
</p>
""".strip()


def section_cost_table(*, city: str | None = None, state: str | None = None) -> str:
    loc_line = ""
    if city and state:
        loc_line = f" in {esc(city)}, {esc(state)}"
    return f"""
<hr />
<h2>{esc(H2_HEADINGS[6])}</h2>
<p class="muted">
  Typical project pricing{loc_line} depends on how much ivy has spread, access, and whether it climbs trees or structures.
</p>
<table class="table" aria-label="Cost estimate table">
  <thead>
    <tr>
      <th>Service</th>
      <th>Typical range</th>
      <th>What moves the price</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>{esc(CONFIG.service_name)}</td>
      <td>${CONFIG.cost_low}–${CONFIG.cost_high}</td>
      <td>Area size, root density, climbing height, disposal, repeat visits</td>
    </tr>
  </tbody>
</table>
<p class="muted" style="margin-top:10px;">
  A site check gives the cleanest number. Quotes can change based on access and how deep the roots run.
</p>
""".strip()


def section_service_area(*, city: str | None = None, state: str | None = None) -> str:
    if city and state:
        area = f"We serve {esc(city)}, {esc(state)} and nearby neighborhoods."
    else:
        area = "We publish local pages so you can see pricing notes by city."
    return f"""
<h2>{esc(H2_HEADINGS[7])}</h2>
<p>
  {area}
</p>
""".strip()


def footer_cta() -> str:
    # Exact required CTA line must appear at the bottom.
    return f"""
<footer>
  <div class="footer-card">
    <h2>{esc("Ready to move forward?")}</h2>
    <p>{esc("Ready to move forward? Request a free quote")}</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">
      © {esc(CONFIG.brand_name)}. All rights reserved.
      <div class="links" style="margin-top:10px;">
        <a href="/">Home</a>
      </div>
    </div>
  </div>
</footer>
""".rstrip()


# -----------------------
# PAGES
# -----------------------
def city_page(*, city: str, state: str) -> str:
    h1 = make_city_h1(CONFIG.service_name, city, state)
    title = h1  # EXACT match per rule

    description = clamp_title(
        f"Poison ivy removal pricing, what affects cost, and what to expect — {city}, {state}.",
        155,
    )

    canonical = f"/{city_state_slug(city, state)}/"

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Clear guidance on removal, common pitfalls, and typical pricing. We keep it simple and focus on the roots.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <div class="grid">
    <section class="card">
      <div class="pill">Local removal guide</div>

      <div class="img" style="margin-top:12px;">
        <img src="{esc(LOCAL_IMAGE_CITY)}" alt="Ivy and vine removal work area" loading="lazy" />
      </div>

      {curated_intro(city=city, state=state)}

      {section_poison_vs_english_ivy()}
      {section_identify_poison_ivy()}
      {section_spread_and_return()}
      {section_can_you_pull_it()}
      {section_herbicide_first()}
      {section_landscapers()}

      <!-- Cost near the bottom (required) -->
      {section_cost_table(city=city, state=state)}

      {section_service_area(city=city, state=state)}
    </section>
  </div>
</main>

{footer_cta()}
""".rstrip()

    return base_html(title=title, canonical_path=canonical, description=description, body_inner=body_inner)


def homepage(*, cities: list[tuple[str, str]]) -> str:
    # Ahrefs-style keyword stacking, kept human and <= 70 chars.
    # Title == H1 and not location-specific.
    h1 = clamp_title("Poison Ivy / English Ivy & Vine Removal Services", 70)
    title = h1

    description = clamp_title(
        "Poison ivy and ivy vine removal guidance, what affects cost, and local pages by city.",
        155,
    )

    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state in cities
    )

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Ivy spreads through roots and runners. Poison ivy can also trigger a rash after contact.
      We remove poison ivy, English ivy, and heavy vines and we focus on what makes it come back.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <section class="card">
    <div class="pill">Straight answers</div>

    <div class="img" style="margin-top:12px;">
      <img src="{esc(LOCAL_IMAGE_HOME)}" alt="Yard edge and fence line where vines can spread" loading="lazy" />
    </div>

    {curated_intro()}

    <h2>About this service</h2>
    <p>
      We remove ivy in yards, along fences, around sheds, and on trees.
      We aim to clear the plant, reduce regrowth, and keep the work contained.
    </p>

    <!-- Homepage H2s are not restricted, but we keep them aligned with the same intent -->
    {section_poison_vs_english_ivy()}
    {section_identify_poison_ivy()}
    {section_spread_and_return()}
    {section_can_you_pull_it()}
    {section_herbicide_first()}
    {section_landscapers()}

    <h2>Typical pricing range</h2>
    <p class="muted">
      Many projects fall in the ${CONFIG.cost_low}–${CONFIG.cost_high} range. Price depends on spread, access, and height.
    </p>

    <hr />

    <h2>Choose your city for local pages</h2>
    <p class="muted">Each city page keeps the same guide and adds a light local note.</p>

    <!-- Clean city buttons (grid) -->
    <ul class="city-grid">
      {city_links}
    </ul>
  </section>
</main>

{footer_cta()}
""".rstrip()

    return base_html(title=title, canonical_path="/", description=description, body_inner=body_inner)


# -----------------------
# GENERATION
# -----------------------
def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    CONFIG.output_dir.mkdir(parents=True, exist_ok=True)

    # Homepage
    write_file(CONFIG.output_dir / "index.html", homepage(cities=CITIES))

    # City pages
    for city, state in CITIES:
        slug = city_state_slug(city, state)
        out = CONFIG.output_dir / slug / "index.html"
        write_file(out, city_page(city=city, state=state))

    print(f"✅ Generated {1 + len(CITIES)} pages into: {CONFIG.output_dir.resolve()}")


if __name__ == "__main__":
    main()
