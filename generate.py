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
- Natural CTA at the bottom
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
    service_name: str = "Poison Ivy Removal"
    brand_name: str = "Poison Ivy Removal Company"
    cta_text: str = "Get Free Estimate"
    cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"
    output_dir: Path = Path("public")
    # NOTE: Set these to your real pricing bands. Kept simple placeholders.
    cost_low: int = 250
    cost_high: int = 750


CONFIG = SiteConfig()

# Controlled H2 set (city pages ONLY pull headings from this list)
# Built from Ahrefs intent patterns around:
# "how to kill poison ivy in your yard", "kill roots", "what will kill poison ivy",
# "without killing other plants", "permanently kill poison ivy", etc.
H2_HEADINGS = [
    "How to identify poison ivy",
    "What makes poison ivy come back",
    "Manual removal vs herbicide treatments",
    "How to kill poison ivy roots permanently",
    "Protecting nearby plants, pets, and kids",
    "Cleanup and disposal to avoid spreading oils",
    "When to hire a professional",
    "Cost estimate",
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
# Reusing your existing local assets (you can swap to a poison-ivy photo later if you add one).
LOCAL_IMAGE_CITY = "/assets/front-door.jpg"
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
# PAGES
# -----------------------
def city_page(*, city: str, state: str) -> str:
    h1 = make_city_h1(CONFIG.service_name, city, state)
    title = h1  # EXACT match per your rule

    description = clamp_title(
        f"Poison ivy removal guidance: how pros kill roots, limit regrowth, and what affects cost in {city}, {state}.",
        155,
    )

    canonical = f"/{city_state_slug(city, state)}/"

    body_inner = f"""
<header>
  <div class="wrap hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">
      Practical guidance on removing poison ivy, preventing regrowth, and what typically affects the total cost.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <div class="grid">
    <section class="card">
      <div class="pill">Local removal guide</div>

      <div class="img" style="margin-top:12px;">
        <img src="{esc(LOCAL_IMAGE_CITY)}" alt="Exterior entryway and surrounding landscaping" loading="lazy" />
      </div>

      <h2>{esc(H2_HEADINGS[0])}</h2>
      <p>
        Poison ivy often grows as a ground cover or climbing vine with clusters of three leaflets.
        Because look-alikes exist, identification usually focuses on growth pattern, leaflet shape, and where the plant is spreading.
      </p>

      <h2>{esc(H2_HEADINGS[1])}</h2>
      <p>
        Regrowth is common when roots remain, vines re-sprout from buried stems, or birds spread seeds.
        A lasting plan usually includes removing visible growth and treating the root system over time.
      </p>

      <h2>{esc(H2_HEADINGS[2])}</h2>
      <p>
        Manual removal can work for small patches if done carefully, but it can be labor-intensive.
        Targeted herbicide treatments may be more effective for established vines—especially when the goal is permanent control.
      </p>

      <h2>{esc(H2_HEADINGS[3])}</h2>
      <p>
        “Permanent” results typically come from addressing roots and repeating control steps as needed.
        Timing, coverage, and follow-up matter—particularly for mature vines climbing fences, trees, or structures.
      </p>

      <h2>{esc(H2_HEADINGS[4])}</h2>
      <p>
        A careful approach helps protect nearby plants and reduces exposure risk for pets and kids.
        Pros often use targeted application and containment so the treatment stays where it’s needed.
      </p>

      <h2>{esc(H2_HEADINGS[5])}</h2>
      <p>
        Oils from the plant can transfer to gloves, tools, clothing, and yard waste.
        Cleanup usually includes bagging debris properly, cleaning tools, and avoiding actions that spread residue around the property.
      </p>

      <h2>{esc(H2_HEADINGS[6])}</h2>
      <p>
        Professional help is most useful when vines are extensive, climbing high, mixed into landscaping,
        or when you need a plan that reduces regrowth and limits exposure risk.
      </p>

      <hr />

      <h2>{esc(H2_HEADINGS[7])}</h2>
      <p class="muted">
        Estimated service cost in {esc(city)}, {esc(state)} (many projects):
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
            <td>Area size, vine maturity, access, disposal needs, follow-up visits</td>
          </tr>
        </tbody>
      </table>

      <p class="muted" style="margin-top:10px;">
        These are typical ranges—actual quotes vary by site conditions and how established the growth is.
      </p>
    </section>
  </div>
</main>

<footer>
  <div class="footer-card">
    <h2>Ready to move forward?</h2>
    <p>Ready to move forward? Request a free quote</p>
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

    return base_html(title=title, canonical_path=canonical, description=description, body_inner=body_inner)


def homepage(*, cities: list[tuple[str, str]]) -> str:
    # Homepage H1 must be general (NOT location-specific), title == H1, <= 70 chars
    h1 = clamp_title("Poison Ivy Removal: How to Kill It Permanently", 70)
    title = h1

    description = clamp_title(
        "Learn how poison ivy is removed, what kills roots, what affects cost, and find local estimates by city.",
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
      Most poison ivy removal projects fall between ${CONFIG.cost_low} and ${CONFIG.cost_high}, depending on how established the growth is.
      Choose your city for local estimates.
    </p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
  </div>
</header>

<main class="wrap">
  <section class="card">
    <div class="pill">Nationwide overview</div>

    <div class="img" style="margin-top:12px;">
      <img src="{esc(LOCAL_IMAGE_HOME)}" alt="Exterior entryway and surrounding landscaping" loading="lazy" />
    </div>

    <h2>What kills poison ivy permanently?</h2>
    <p>
      Long-term control usually means addressing the root system and planning for follow-up.
      Many properties need more than a single pass—especially where vines are mature or spreading through landscaping beds.
    </p>

    <h2>Remove poison ivy from your yard safely</h2>
    <p>
      Poison ivy can transfer oils onto tools, gloves, clothing, and yard waste.
      A safe removal plan focuses on containment, careful handling, and cleanup steps that reduce accidental spread.
    </p>

    <h2>Manual removal vs targeted treatments</h2>
    <p>
      Small patches may be manageable with careful manual removal, while established vines often require a more structured approach.
      Targeted treatments can help reduce regrowth, especially when vines climb fences, trees, or structures.
    </p>

    <h2>Kill poison ivy without damaging other plants</h2>
    <p>
      When poison ivy is mixed into hedges or garden beds, precision matters.
      Pros often focus on targeted application and site-specific steps to protect nearby plants while controlling the vine.
    </p>

    <h2>Poison ivy removal cost: what affects the price</h2>
    <p>
      Pricing usually depends on the size of the area, how established the vines are, access, disposal needs,
      and whether follow-up visits are recommended for regrowth control.
    </p>

    <hr />

    <h2>Choose your city for local estimates</h2>
    <p class="muted">City pages use clean URLs that include city + state for clarity.</p>

    <!-- Clean city buttons (grid) -->
    <ul class="city-grid">
      {city_links}
    </ul>
  </section>
</main>

<footer>
  <div class="footer-card">
    <h2>Ready to move forward?</h2>
    <p>Ready to move forward? Request a free quote</p>
    <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    <div class="small">© {esc(CONFIG.brand_name)}. All rights reserved.</div>
  </div>
</footer>
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
