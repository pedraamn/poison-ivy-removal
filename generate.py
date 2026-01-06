#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import html
import re
import shutil

@dataclass(frozen=True)
class SiteConfig:

  cities_csv: Path = Path("cities.csv")
  def load_cities(self):
    return load_cities_from_csv(self.cities_csv)
  # Brand / site identity
  # Brand / site identity
  base_name: str = "Poison Ivy Removal"
  brand_name: str = "Poison Ivy Removal Company"
  cta_text: str = "Get Free Estimate"
  cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"

  # Build / assets
  output_dir: Path = Path("public")
  image_filename: str = "picture.png"  # sits next to generate.py

  # Pricing (base range; city pages may apply multipliers)
  cost_low: int = 300
  cost_high: int = 1200

  # Page H1 titles
  h1_title: str = "Poison Ivy Removal/Poison Ivy Control/Ivy Removal Services"
  h1_short: str = "Poison Ivy Removal/Poison Ivy Control Services"
  h1_sub: str = "Safe identification, removal, and control to reduce exposure risk and stop regrowth."

  cost_title: str = "Poison Ivy Removal Cost"
  cost_sub: str = "Typical pricing ranges, key cost factors, and what drives higher quotes."

  howto_title: str = "How to Remove Poison Ivy"
  howto_sub: str = "DIY removal can work for small patches—but only if you avoid spreading oils and address regrowth."

  # MAIN PAGE (shared guide)
  main_h2: list[str] = (
    "How Do I Find Poison Ivy Removal Near Me?",
    "What Are Poison Ivy Removal Services?",
    "What Does a Poison Ivy Plant Look Like?",
    "What Is a Poison Ivy Vine?",
    "Can Poison Ivy Grow in Grass?",
    "What Should You Do If You Have Poison Ivy in Your Yard?",
    "What Does Poison Ivy Control Mean?",
  )
  main_p: list[str] = (
    "The fastest way to find poison ivy removal near you is to choose a local company that can inspect the area and remove the plant safely. Because poison ivy oils spread easily through contact with tools, shoes, pets, and clothing, an on-site assessment helps prevent accidental exposure and missed growth.",
    "Poison ivy removal services are professional treatments that remove visible poison ivy and target the root systems to reduce the chance of it coming back. Many services also include containment and cleanup practices designed to avoid spreading the plant’s oils to nearby surfaces.",
    "A poison ivy plant is often recognized by its leaf clusters and the way it grows along fences, tree lines, and wooded edges. Since poison ivy can change appearance by season and location, misidentification is common without close inspection.",
    "A poison ivy vine is poison ivy that climbs trees, fences, or structures instead of staying low to the ground. Vines are harder to spot and can spread over time, which often makes infestations more difficult to remove safely.",
    "Yes, poison ivy can grow in grass, especially near borders, shaded edges, and low-maintenance areas. When it blends into turf or ground cover, it increases the chance of accidental contact during mowing, walking, or yard work.",
    "If you have poison ivy in your yard, the safest first step is to avoid disturbing it and limit contact in the area. Pulling, cutting, or trimming without proper handling can spread oils and leave roots behind, which often leads to regrowth and repeat exposure.",
    "Poison ivy control means reducing or eliminating poison ivy growth and preventing it from returning. In practice, control usually involves removing existing plants and addressing the root systems and problem areas where poison ivy tends to regrow.",
  )

  # HOW-TO PAGE
  howto_h2: list[str] = (
    "How to Remove Poison Ivy",
    "How to Get Rid of Poison Ivy",
    "How to Kill Poison Ivy",
    "What Kills Poison Ivy?",
    "What Kills Poison Ivy Permanently?",
    "How to Get Rid of Poison Ivy Without Killing Other Plants",
  )
  howto_p: list[str] = (
    "To remove poison ivy, you need to eliminate the plant and its roots without spreading oils to your skin, tools, or nearby surfaces. Small patches can sometimes be removed carefully, but missed roots are a common reason poison ivy returns.",
    "The best way to get rid of poison ivy is to remove the growth you can see and stop the plant from regrowing from remaining roots. If you only cut it back, you may see short-term improvement while the infestation continues underground.",
    "To kill poison ivy, you need to stop it at the root—not just knock down the surface growth. Many homeowners end up repeating removal attempts because the plant survives below ground and grows back in the same areas.",
    "What kills poison ivy is any approach that reaches the root system and prevents regrowth. If poison ivy keeps reappearing in the same spots, it usually means only the top growth is being removed while roots remain intact.",
    "The closest thing to killing poison ivy permanently is full root elimination and preventing regrowth in the same area. If vines have climbed trees or the infestation covers a wide footprint, professional {poison ivy removal services} are often the safer and more reliable option.",
    "To get rid of poison ivy without killing other plants, you have to be precise about what you remove and avoid spreading oils into surrounding landscaping. This is hardest when poison ivy is mixed into shrubs, groundcover, or dense plantings where accidental damage is more likely.",
  )

  # COST PAGE
  cost_h2: list[str] = (
    "How Much Does Poison Ivy Removal Cost?",
    "What Affects Poison Ivy Removal Cost?",
    "Is Poison Ivy Removal Near Me More Expensive?",
  )
  cost_p: list[str] = (
    "Poison ivy removal cost depends mostly on how much area is affected and whether vines or roots have spread into hard-to-reach places. Smaller, contained patches are typically less expensive, while widespread growth along fences, tree lines, or landscaping increases labor and disposal needs.",
    "The biggest factors that affect poison ivy removal cost are infestation size, accessibility, vine growth on structures or trees, and the likelihood of regrowth without follow-up control. The more hidden poison ivy is around edges and landscaping, the more time it usually takes to remove safely.",
    "Poison ivy removal near you can cost more or less depending on local labor rates and how quickly a provider can schedule the work. In most cases, the main driver is the severity of the infestation once someone evaluates the property.",
  )

  # LOCAL COST (city-locked variant)
  location_cost_h2: str = "How Much Does Poison Ivy Removal Cost in {City, State}?"

  location_cost_p: str = (
    "In {City, State}, most poison ivy removal projects range from {cost_lo} to {cost_hi}, "
    "depending on infestation size and how difficult the plant is to access and fully eliminate. "
    "Prices can vary based on local labor rates, property layout, and disposal requirements. "
    "For a clearer breakdown of what affects pricing, you can {view our poison ivy removal cost guide}."
  )

  # IMAGES
  image_prompt: str = (
    "A realistic outdoor photo of a landscaper removing poison ivy from a backyard fence line, "
    "wearing protective gloves, long sleeves, and eye protection, using hand tools and a heavy-duty yard bag "
    "for containment; natural lighting, real suburban yard environment, no staged stock-photo look."
  )



CONFIG = SiteConfig()

CityWithCol = tuple[str, str, float]

def load_cities_from_csv(path: Path) -> tuple[CityWithCol, ...]:
  cities: list[CityWithCol] = []

  with path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    required_fields = {"city", "state", "col"}
    if not reader.fieldnames or not required_fields.issubset(reader.fieldnames):
      raise ValueError(
          "CSV must have headers: city,state,col "
          f"(found: {reader.fieldnames})"
      )

    for i, row in enumerate(reader, start=2):  # header is line 1
      city = (row.get("city") or "").strip()
      state = (row.get("state") or "").strip().upper()
      col_raw = (row.get("col") or "").strip()

      if not city or not state or not col_raw:
        raise ValueError(f"Missing city/state/col at CSV line {i}: {row}")

      try:
        col = float(col_raw)
      except ValueError as e:
        raise ValueError(
            f"Invalid col value at CSV line {i}: {col_raw!r}"
        ) from e

      cities.append((city, state, col))

  return tuple(cities)

CITIES: tuple[CityWithCol, ...] = CONFIG.load_cities()



"""
ALSO_MENTIONED = [
    "pest control",
    "spray",
    "spray bottle",
    "dish soap",
    "wasp stings",
    "price",
    "removal",
    "nest",
    "wasp",
]
"""


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


def city_title(city: str, state: str) -> str:
    return clamp_title(f"{CONFIG.h1_short} in {city}, {state}", 70)


def write_text(out_path: Path, content: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")


def reset_output_dir(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def copy_site_image(*, src_dir: Path, out_dir: Path, filename: str) -> None:
    src = src_dir / filename
    if not src.exists():
        raise FileNotFoundError(f"Missing image next to generate.py: {src}")
    shutil.copyfile(src, out_dir / filename)


# -----------------------
# THEME (pure CSS, minimal, fast)
# Home-services vibe: warmer neutrals + trustworthy green CTA.
# -----------------------
CSS = """
:root{
  --bg:#fafaf9;
  --surface:#ffffff;
  --ink:#111827;
  --muted:#4b5563;
  --line:#e7e5e4;
  --soft:#f5f5f4;

  --cta:#16a34a;
  --cta2:#15803d;

  --max:980px;
  --radius:16px;
  --shadow:0 10px 30px rgba(17,24,39,0.06);
  --shadow2:0 10px 24px rgba(17,24,39,0.08);
}
*{box-sizing:border-box}
html{color-scheme:light}
body{
  margin:0;
  font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;
  color:var(--ink);
  background:var(--bg);
  line-height:1.6;
}
a{color:inherit}
a:focus{outline:2px solid var(--cta); outline-offset:2px}

.topbar{
  position:sticky;
  top:0;
  z-index:50;
  background:rgba(250,250,249,0.92);
  backdrop-filter:saturate(140%) blur(10px);
  border-bottom:1px solid var(--line);
}
.topbar-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:12px 18px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
}
.brand{
  font-weight:900;
  letter-spacing:-0.02em;
  text-decoration:none;
}
.nav{
  display:flex;
  align-items:center;
  gap:12px;
  flex-wrap:wrap;
  justify-content:flex-end;
}
.nav a{
  text-decoration:none;
  font-size:13px;
  color:var(--muted);
  padding:7px 10px;
  border-radius:12px;
  border:1px solid transparent;
}
.nav a:hover{
  background:var(--soft);
  border-color:var(--line);
}
.nav a[aria-current="page"]{
  color:var(--ink);
  background:var(--soft);
  border:1px solid var(--line);
}

.btn{
  display:inline-block;
  padding:9px 12px;
  background:var(--cta);
  color:#fff;
  border-radius:12px;
  text-decoration:none;
  font-weight:900;
  font-size:13px;
  border:1px solid rgba(0,0,0,0.04);
  box-shadow:0 8px 18px rgba(22,163,74,0.18);
}
.btn:hover{background:var(--cta2)}
.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

/* IMPORTANT: nav links apply grey text; ensure CTA stays white in the toolbar */
.nav a.btn{
  color:#fff;
  background:var(--cta);
  border-color:rgba(0,0,0,0.04);
}
.nav a.btn:hover{background:var(--cta2)}
.nav a.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

header{
  border-bottom:1px solid var(--line);
  background:
    radial-gradient(1200px 380px at 10% -20%, rgba(22,163,74,0.08), transparent 55%),
    radial-gradient(900px 320px at 95% -25%, rgba(17,24,39,0.06), transparent 50%),
    #fbfbfa;
}
.hero{
  max-width:var(--max);
  margin:0 auto;
  padding:34px 18px 24px;
  display:grid;
  gap:10px;
  text-align:left;
}
.hero h1{
  margin:0;
  font-size:30px;
  letter-spacing:-0.03em;
  line-height:1.18;
}
.sub{margin:0; color:var(--muted); max-width:78ch; font-size:14px}

main{
  max-width:var(--max);
  margin:0 auto;
  padding:22px 18px 46px;
}
.card{
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:18px;
  box-shadow:var(--shadow);
}
.img{
  margin-top:14px;
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--line);
  background:var(--soft);
  box-shadow:var(--shadow2);
}
.img img{display:block; width:100%; height:auto}

h2{
  margin:18px 0 8px;
  font-size:16px;
  letter-spacing:-0.01em;
}
p{margin:0 0 10px}
.muted{color:var(--muted); font-size:13px}
hr{border:0; border-top:1px solid var(--line); margin:18px 0}

.city-grid{
  list-style:none;
  padding:0;
  margin:10px 0 0;
  display:grid;
  gap:10px;
  grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
}
.city-grid a{
  display:block;
  text-decoration:none;
  color:var(--ink);
  background:#fff;
  border:1px solid var(--line);
  border-radius:14px;
  padding:12px 12px;
  font-weight:800;
  font-size:14px;
  box-shadow:0 10px 24px rgba(17,24,39,0.05);
}
.city-grid a:hover{
  transform:translateY(-1px);
  box-shadow:0 14px 28px rgba(17,24,39,0.08);
}

.callout{
  margin:16px 0 12px;
  padding:14px 14px;
  border-radius:14px;
  border:1px solid rgba(22,163,74,0.22);
  background:linear-gradient(180deg, rgba(22,163,74,0.08), rgba(22,163,74,0.03));
}
.callout-title{
  display:flex;
  align-items:center;
  gap:10px;
  font-weight:900;
  letter-spacing:-0.01em;
  margin:0 0 6px;
}
.badge{
  display:inline-block;
  padding:3px 10px;
  border-radius:999px;
  background:rgba(22,163,74,0.14);
  border:1px solid rgba(22,163,74,0.22);
  color:var(--ink);
  font-size:12px;
  font-weight:900;
}
.callout p{margin:0; color:var(--muted); font-size:13px}

footer{
  border-top:1px solid var(--line);
  background:#fbfbfa;
}
.footer-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:28px 18px;
  display:grid;
  gap:10px;
  text-align:left;
}
.footer-inner h2{margin:0; font-size:18px}
.footer-links{display:flex; gap:12px; flex-wrap:wrap}
.footer-links a{color:var(--muted); text-decoration:none; font-size:13px; padding:6px 0}
.small{color:var(--muted); font-size:12px; margin-top:8px}
""".strip()


# -----------------------
# HTML BUILDING BLOCKS
# -----------------------
def nav_html(current: str) -> str:
    def item(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{esc(href)}"{cur}>{esc(label)}</a>'

    return (
        '<nav class="nav" aria-label="Primary navigation">'
        + item("/", "Home", "home")
        + item("/cost/", "Cost", "cost")
        + item("/how-to/", "How-To", "howto")
        + f'<a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>'
        + "</nav>"
    )


def base_html(*, title: str, canonical_path: str, current_nav: str, body: str) -> str:
    # title == h1 is enforced by callers; keep this thin.
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <link rel="canonical" href="{esc(canonical_path)}" />
  <style>
{CSS}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="/">{esc(CONFIG.brand_name)}</a>
      {nav_html(current_nav)}
    </div>
  </div>
{body}
</body>
</html>
"""


def header_block(*, h1: str, sub: str) -> str:
    return f"""
<header>
  <div class="hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">{esc(sub)}</p>
  </div>
</header>
""".rstrip()


def footer_block() -> str:
    return f"""
<footer>
  <div class="footer-inner">
    <h2>Next steps</h2>
    <p class="sub">Ready to move forward? Request a free quote.</p>
    <div>
      <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    </div>
    <div class="footer-links">
      <a href="/">Home</a>
      <a href="/cost/">Cost</a>
      <a href="/how-to/">How-To</a>
    </div>
    <div class="small">© {esc(CONFIG.brand_name)}. All rights reserved.</div>
  </div>
</footer>
""".rstrip()


def page_shell(*, h1: str, sub: str, inner_html: str) -> str:
    # Single image used everywhere. Since we copy picture.png into /public/,
    # it can be referenced as "/picture.png" from any route.
    img_src = f"/{CONFIG.image_filename}"
    return (
        header_block(h1=h1, sub=sub)
        + f"""
<main>
  <section class="card">
    <div class="img">
      <img src="{esc(img_src)}" alt="Service image" loading="lazy" />
    </div>
    {inner_html}
  </section>
</main>
"""
        + footer_block()
    ).rstrip()


# -----------------------
# CONTENT SECTIONS
# -----------------------

def linkify_curly(text: str) -> str:
  """
  Replace {word} with a link to the homepage using that word as link text
  """
  parts = []
  last = 0

  for m in re.finditer(r"\{([^}]+)\}", text):
    # text before the match
    parts.append(esc(text[last:m.start()]))

    word = m.group(1)
    parts.append(f'<a href="/">{esc(word)}</a>')

    last = m.end()

  # remaining text
  parts.append(esc(text[last:]))

  return "".join(parts)

def make_section(*, headings: list[str], paras:  list[str]) -> str:
  parts = []
  for h2, p in zip(headings, paras):
    parts.append(f"<h2>{esc(h2)}</h2>")
    parts.append(f"<p>{linkify_curly(p)}</p>")
  return "\n".join(parts)

def location_cost_section(city: str, state: str, col: float) -> str:
    cost_lo = f"${int(CONFIG.cost_low * col)}"
    cost_hi = f"${int(CONFIG.cost_high * col)}"

    h2 = CONFIG.location_cost_h2.replace(
        "{City, State}", f"{city}, {state}"
    )

    p = (
        CONFIG.location_cost_p
        .replace("{City, State}", f"{city}, {state}")
        .replace("{cost_lo}", cost_lo)
        .replace("{cost_hi}", cost_hi)
    )

    return f"<h2>{esc(h2)}</h2>\n<p>{esc(p)}</p>"


def city_cost_callout_html(city: str, state: str) -> str:
    # Subtle, high-impact conversion element for city pages.
    return f"""
<div class="callout" role="note" aria-label="Typical cost range">
  <div class="callout-title">
    <span class="badge">Typical range in {esc(city)}, {esc(state)}</span>
    <span>${CONFIG.cost_low}–${CONFIG.cost_high}</span>
  </div>
</div>
""".rstrip()


# -----------------------
# PAGE FACTORY
# -----------------------
def make_page(*, h1: str, canonical: str, nav_key: str, sub: str, inner: str) -> str:
    h1 = clamp_title(h1, 70)
    title = h1  # enforce title == h1
    return base_html(
        title=title,
        canonical_path=canonical,
        current_nav=nav_key,
        body=page_shell(h1=h1, sub=sub, inner_html=inner),
    )


def homepage_html() -> str:
    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state, _ in CITIES
    )
    inner = (
        make_section(headings=CONFIG.main_h2, paras=CONFIG.main_p)
        + """
<hr />
<h2>Choose your city</h2>
<p class="muted">We provide services nationwide, including in the following cities:</p>
<ul class="city-grid">
"""
        + city_links
        + f"""
</ul>
<hr />
<p class="muted">
  Also available: <a href="/cost/">{esc(CONFIG.cost_title)}</a> and <a href="/how-to/">{esc(CONFIG.howto_title)}</a>.
</p>
"""
    )

    return make_page(
        h1=CONFIG.h1_title,
        canonical="/",
        nav_key="home",
        sub=CONFIG.h1_sub,
        inner=inner,
    )

def city_page_html(city: str, state: str, col: float) -> str:
    inner = (
      location_cost_section(city, state, col)
      + make_section(headings=CONFIG.main_h2, paras=CONFIG.main_p)
    )

    return make_page(
        h1=city_title(city, state),
        canonical=f"/{city_state_slug(city, state)}/",
        nav_key="home",
        sub=CONFIG.h1_sub,
        inner=inner,
    )


def cost_page_html() -> str:
    return make_page(
        h1=CONFIG.cost_title,
        canonical="/cost/",
        nav_key="cost",
        sub=CONFIG.cost_sub,
        inner=make_section(headings=CONFIG.cost_h2, paras=CONFIG.cost_p),
    )


def howto_page_html() -> str:
    return make_page(
        h1=CONFIG.howto_title,
        canonical="/how-to/",
        nav_key="howto",
        sub=CONFIG.howto_sub,
        inner=make_section(headings=CONFIG.howto_h2, paras=CONFIG.howto_p),
    )


# -----------------------
# ROBOTS + SITEMAP
# -----------------------
def robots_txt() -> str:
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"


def sitemap_xml(urls: list[str]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n"
    )


# -----------------------
# MAIN
# -----------------------
def main() -> None:
    script_dir = Path(__file__).resolve().parent
    out = CONFIG.output_dir

    reset_output_dir(out)

    # Copy the single shared image into /public/ so all pages can reference "/picture.png".
    copy_site_image(src_dir=script_dir, out_dir=out, filename=CONFIG.image_filename)

    # Core pages
    write_text(out / "index.html", homepage_html())
    write_text(out / "cost" / "index.html", cost_page_html())
    write_text(out / "how-to" / "index.html", howto_page_html())

    # City pages
    for city, state, col in CITIES:
        write_text(out / city_state_slug(city, state) / "index.html", city_page_html(city, state, col))

    # robots + sitemap
    urls = ["/", "/cost/", "/how-to/"] + [f"/{city_state_slug(c, s)}/" for c, s, _ in CITIES]
    write_text(out / "robots.txt", robots_txt())
    write_text(out / "sitemap.xml", sitemap_xml(urls))

    print(f"✅ Generated {len(urls)} pages into: {out.resolve()}")


if __name__ == "__main__":
    main()
