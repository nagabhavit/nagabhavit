"""Generate the hand-designed (non-data) SVGs: banner, section headers,
man-page project cards, the periodic table of tools, and the footer.

    python scripts/build_static.py
"""

from __future__ import annotations

import math
import textwrap

from svgkit import (AMBER, CYAN, DIM, INK, LINE, MINT, MONO, MUTED, PANEL, PINK,
                    SERIF, TEXT, VIOLET, measure, svg, text, write)

SCANLINES = """
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#ffffff" opacity="0.035"/>
</pattern>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
  <circle cx="1" cy="1" r="1" fill="#ffffff" opacity="0.06"/>
</pattern>
"""


# --------------------------------------------------------------------------
# banner
# --------------------------------------------------------------------------
def banner() -> str:
    W, H = 1200, 440
    cmd = "./pipeline --from molecules --to models"
    cw = 19 * 0.6  # Plex Mono advance is 600/1000 em
    n = len(cmd)

    # typing: n+1 discrete states over 55% of the loop, hold, then clear
    steps = list(range(n + 1))
    t_type = 0.45
    key_times = [round(t_type * i / n, 4) for i in steps] + [0.92, 1]
    widths = [round(i * cw, 1) for i in steps] + [round(n * cw, 1), 0]
    kt = ";".join(map(str, key_times))
    cursor_x = ";".join(str(round(84 + w, 1)) for w in widths)
    clip_w = ";".join(map(str, widths))

    # molecule / knowledge-graph
    cx, cy, r = 962, 238, 58
    hexv = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in (-90, -30, 30, 90, 150, 210)]
    hex_path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in hexv) + " Z"

    # inner bonds on alternating edges (Kekulé structure)
    inner = []
    for i in (0, 2, 4):
        (x1, y1), (x2, y2) = hexv[i], hexv[(i + 1) % 6]
        k = 0.78
        ix1, iy1 = cx + (x1 - cx) * k, cy + (y1 - cy) * k
        ix2, iy2 = cx + (x2 - cx) * k, cy + (y2 - cy) * k
        # shorten a touch
        dx, dy = ix2 - ix1, iy2 - iy1
        ix1, iy1, ix2, iy2 = ix1 + dx * .12, iy1 + dy * .12, ix2 - dx * .12, iy2 - dy * .12
        inner.append(f'<line x1="{ix1:.1f}" y1="{iy1:.1f}" x2="{ix2:.1f}" y2="{iy2:.1f}" '
                     f'stroke="{TEXT}" stroke-opacity=".55" stroke-width="2"/>')

    subs = [  # (vertex, node, label, color, label anchor offset)
        (0, (962, 120), "SMILES", PINK, (0, -18, "middle")),
        (1, (1068, 180), "BioKG", AMBER, (16, 5, "start")),
        (2, (1074, 302), "Vina", CYAN, (16, 5, "start")),
        (3, (962, 360), "ADMET", MINT, (0, 30, "middle")),
        (4, (850, 302), "EFO", VIOLET, (-16, 5, "end")),
        (5, (852, 180), "MeSH", AMBER, (-16, 5, "end")),
    ]
    mol = []
    for i, (v, (nx, ny), label, col, (ox, oy, anc)) in enumerate(subs):
        vx, vy = hexv[v]
        length = math.hypot(nx - vx, ny - vy)
        mol.append(
            f'<line class="bond" style="--len:{length:.0f};animation-delay:{0.5 + i * .18:.2f}s" '
            f'x1="{vx:.1f}" y1="{vy:.1f}" x2="{nx}" y2="{ny}" stroke="{col}" stroke-opacity=".7" '
            f'stroke-width="2" stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}"/>'
        )
        mol.append(
            f'<circle cx="{nx}" cy="{ny}" r="11" fill="{col}" opacity=".14">'
            f'<animate attributeName="r" values="9;15;9" dur="{3 + i * .4:.1f}s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{nx}" cy="{ny}" r="5.5" fill="{col}"/>'
        )
        mol.append(text(nx + ox, ny + oy, label, size=15, fill=col, weight=500, anchor=anc))

    vertices = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{TEXT}"/>' for x, y in hexv)

    body = f"""
<defs>
  {SCANLINES}
  <linearGradient id="nameGrad" x1="56" y1="0" x2="520" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{AMBER}"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".045"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="glow" cx="962" cy="238" r="260" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{PINK}" stop-opacity=".16"/>
    <stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="panel"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="typed"><rect x="84" y="340" height="30" width="0">
    <animate attributeName="width" values="{clip_w}" keyTimes="{kt}" dur="9s" calcMode="discrete" repeatCount="indefinite"/>
  </rect></clipPath>
</defs>
<g clip-path="url(#panel)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>

  {text(40, 36, "TTY/00", size=13, fill=AMBER, weight=500)}
  {text(102, 36, "──  NAGABHAVIT.PAMPATI  ──  12.97°N 77.59°E  ──  REV 2026.10", size=13, fill=MUTED)}
  <circle cx="1088" cy="31" r="4.5" fill="{MINT}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
  {text(1100, 36, "ONLINE", size=13, fill=MINT, weight=500)}
  <line x1="40" y1="54" x2="{W - 40}" y2="54" stroke="{LINE}"/>

  {text(56, 112, "// data science  ·  ai engineering  ·  computational drug discovery", size=16, fill=AMBER)}
  {text(50, 206, "Nagabhavit", size=104, fill=TEXT, family=SERIF)}
  {text(50, 300, "Pampati.", size=104, fill="url(#nameGrad)", family=SERIF, style="font-style:italic")}

  {text(56, 362, "$", size=19, fill=PINK, weight=600)}
  <g clip-path="url(#typed)">{text(84, 362, cmd, size=19, fill=MINT)}</g>
  <rect x="84" y="345" width="11" height="22" fill="{MINT}">
    <animate attributeName="x" values="{cursor_x}" keyTimes="{kt}" dur="9s" calcMode="discrete" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/>
  </rect>
  {text(56, 400, "B.Tech CSE (Data Science)  ·  Manipal Institute of Technology  ·  class of '27", size=15, fill=MUTED)}

  <circle cx="{cx}" cy="{cy}" r="150" stroke="{LINE}" stroke-dasharray="2 7"/>
  <g class="orbit"><ellipse cx="{cx}" cy="{cy}" rx="190" ry="70" stroke="{VIOLET}" stroke-opacity=".28"/>
    <circle cx="{cx + 190}" cy="{cy}" r="3.5" fill="{VIOLET}"/></g>
  {"".join(mol)}
  <path d="{hex_path}" stroke="{TEXT}" stroke-opacity=".85" stroke-width="2.2" stroke-linejoin="round"/>
  {"".join(inner)}
  {vertices}
  <circle r="3.5" fill="{PINK}"><animateMotion dur="4s" repeatCount="indefinite" path="{hex_path}"/></circle>
  <circle r="2.5" fill="{CYAN}"><animateMotion dur="6s" repeatCount="indefinite" keyPoints="1;0" keyTimes="0;1" calcMode="linear" path="{hex_path}"/></circle>
  {text(1160, 418, "fig. 1 — a molecule and a knowledge graph are the same data structure.", size=12.5, fill=DIM, anchor="end")}

  <rect width="{W}" height="{H}" fill="url(#scan)"/>
  <rect class="sweep" width="{W}" height="120" fill="url(#sweep)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" stroke="{LINE}"/>
"""
    css = """
.bond{animation:draw 1.1s cubic-bezier(.6,0,.2,1) forwards}
@keyframes draw{to{stroke-dashoffset:0}}
.orbit{transform-origin:962px 238px;animation:spin 26s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.sweep{animation:sweep 7s linear infinite}
@keyframes sweep{from{transform:translateY(-120px)}to{transform:translateY(440px)}}
"""
    return svg(W, H, body, css=css, fonts=("mono400", "mono500", "mono600", "serif", "serifI"),
               title="Nagabhavit Pampati — data science, AI engineering, computational drug discovery")


# --------------------------------------------------------------------------
# section headers — transparent, legible on both light and dark GitHub themes
# --------------------------------------------------------------------------
HEAD_PINK = "#E5487A"
HEAD_AMBER = "#D98E1F"
HEAD_GRAY = "#7D8590"

SECTIONS = [
    ("01", "whoami", "cat about.c"),
    ("02", "git log --career", "where I've shipped"),
    ("03", "man ./projects", "selected work"),
    ("04", "the periodic table", "of things I build with"),
    ("05", "telemetry", "contribution signal, live"),
    ("06", "from the archives", "re-punched every monday"),
]


def section(num: str, title: str, note: str) -> str:
    W, H = 1200, 84
    rule_start = 88 + measure(title, 52) + 28
    rule_end = W - 4 - measure("// " + note, 16, "mono400") - 24
    body = f"""
{text(2, 58, num, size=18, fill=HEAD_AMBER, weight=600)}
<line x1="36" y1="52" x2="72" y2="52" stroke="{HEAD_AMBER}" stroke-width="2"/>
{text(88, 64, title, size=52, fill=HEAD_PINK, family=SERIF, style="font-style:italic")}
<line x1="{rule_start:.0f}" y1="52" x2="{rule_end:.0f}" y2="52" stroke="{HEAD_GRAY}" stroke-opacity=".45" stroke-dasharray="2 6"/>
{text(W - 4, 58, "// " + note, size=16, fill=HEAD_GRAY, anchor="end")}
"""
    return svg(W, H, body, fonts=("mono400", "mono600", "serifI"), title=f"{num} {title}")


# --------------------------------------------------------------------------
# project cards, formatted like Unix man pages
# --------------------------------------------------------------------------
RED = "#FF5A4E"

PROJECTS = [
    dict(slug="fraudguard", page="FRAUDGUARD(1)", name="FraudGuard", color=MINT, pill="p99 ≤ 100 ms",
         synopsis="fastapi · kafka · redis · postgres · lightgbm · k8s",
         desc="Distributed fraud detection that scores card transactions inline in the "
              "authorization path. Features are precomputed off a Kafka stream and served "
              "from Redis; if a dependency dies it degrades to rules, never fails open.",
         foot="nagabhavit/FraudGuard"),
    dict(slug="chaos", page="CHAOS(8)", name="Kubernetes Chaos", color=PINK, pill="fault injection",
         synopsis="kubernetes · kind · locust · python · matplotlib",
         desc="Load-tests Google's Online Boutique microservices on a local Kind cluster, "
              "then scales services to zero mid-traffic to measure failure rate, tail "
              "latency and how long the system takes to heal.",
         foot="nagabhavit/kubernetes-chaos-engineering"),
    dict(slug="gaze", page="GAZE(1)", name="Gaze & Attention", color=CYAN, pill="78% acc · <100 ms",
         synopsis="opencv · mediapipe · webgazer.js · gradient boosting",
         desc="Fuses webcam eye-tracking with scroll, click, idle and tab-switch telemetry "
              "into 24-d features to classify attentive / distracted / disengaged, and "
              "paints live heatmaps that surface UI blind spots.",
         foot="source available on request", cta="ask me ↗"),
    dict(slug="scraper", page="SCRAPE(1)", name="Course Scraper", color=AMBER, pill="multithreaded",
         synopsis="python · flask · beautifulsoup · selenium · pandas",
         desc="Crawls course listings across platforms (BeautifulSoup for static pages, "
              "Selenium for JS-rendered ones) with retries and timeouts, normalises them "
              "into one dataset, and plots pricing and ratings.",
         foot="nagabhavit/web_scrapper"),
    dict(slug="attendly", page="ATTENDLY(1)", name="Attendly", color=VIOLET, pill="the 75% line",
         synopsis="react · vite · node · express · mysql · chart.js",
         desc="A subject-wise attendance tracker for students. Charts your stats and warns "
              "you before you slip under the 75% line, which is the only time a warning is "
              "actually useful.",
         foot="nagabhavit/Attendly"),
    dict(slug="pitwall", page="PITWALL(6)", name="F1 Pit Wall", color=RED, pill="box, box",
         synopsis="html · css · vanilla js · netlify",
         desc="A Ferrari-red Formula 1 dashboard with standings, a race countdown, the "
              "season calendar and paddock news, animated in hand-rolled CSS. Forza "
              "Ferrari, forza Leclerc.",
         foot="f1-pitwall-bhavit.netlify.app"),
]


def card(p: dict) -> str:
    W, H = 600, 340
    col = p["color"]
    pill_w = measure(p["pill"], 14, "mono500") + 26
    lines = textwrap.wrap(p["desc"], 60)
    desc = "".join(text(36, 222 + i * 22, ln, size=14, fill="#BDBAB2") for i, ln in enumerate(lines))
    body = f"""
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>{SCANLINES}</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <rect width="{W}" height="4" fill="{col}"/>
  {text(24, 34, p["page"], size=12.5, fill=MUTED)}
  {text(W / 2, 34, "Nagabhavit's Manual", size=12.5, fill=DIM, anchor="middle")}
  {text(W - 24, 34, p["page"], size=12.5, fill=MUTED, anchor="end")}

  {text(24, 72, "NAME", size=13, fill=col, weight=600)}
  {text(34, 112, p["name"], size=40, fill=TEXT, family=SERIF)}
  <rect x="{W - 24 - pill_w:.0f}" y="86" width="{pill_w:.0f}" height="28" rx="14" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".6"/>
  {text(W - 24 - pill_w / 2, 105, p["pill"], size=14, fill=col, weight=500, anchor="middle")}

  {text(24, 148, "SYNOPSIS", size=13, fill=col, weight=600)}
  {text(36, 172, p["synopsis"], size=14, fill=TEXT, weight=500)}

  {text(24, 202, "DESCRIPTION", size=13, fill=col, weight=600)}
  {desc}

  <line x1="24" y1="{H - 38}" x2="{W - 24}" y2="{H - 38}" stroke="{LINE}"/>
  {text(24, H - 16, p["foot"], size=12.5, fill=MUTED)}
  {text(W - 24, H - 16, p.get("cta", "open ↗"), size=12.5, fill=col, weight=500, anchor="end")}
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" stroke="{LINE}"/>
"""
    return svg(W, H, body, fonts=("mono400", "mono500", "mono600", "serif"),
               title=f"{p['name']} — {p['synopsis']}")


# --------------------------------------------------------------------------
# periodic table of tools
# --------------------------------------------------------------------------
GROUPS = [
    ("languages", AMBER, [("Py", "Python"), ("C", "C"), ("Jv", "Java"), ("Js", "JavaScript"),
                          ("Ts", "TypeScript"), ("Sq", "SQL")]),
    ("data & ml", MINT, [("Np", "NumPy"), ("Pd", "Pandas"), ("Sk", "scikit-learn"), ("Lg", "LightGBM"),
                         ("Mt", "Matplotlib"), ("Cv", "OpenCV"), ("Mp", "MediaPipe"), ("Jp", "Jupyter")]),
    ("life sciences", PINK, [("Vi", "AutoDock Vina"), ("Ad", "ADMET"), ("Bk", "BioKG"),
                             ("Lx", "lxml"), ("Pn", "Pydantic")]),
    ("web", CYAN, [("Fl", "Flask"), ("Fa", "FastAPI"), ("Re", "React"), ("Hc", "HTML/CSS"),
                   ("Bs", "BeautifulSoup"), ("Se", "Selenium")]),
    ("infra & tooling", VIOLET, [("Ga", "GH Actions"), ("Dk", "Docker"), ("Ks", "Kubernetes"),
                                 ("Kf", "Kafka"), ("Rd", "Redis"), ("Pg", "PostgreSQL"),
                                 ("Ms", "MySQL"), ("Ru", "ruff"), ("My", "mypy")]),
]


def periodic() -> str:
    W, H = 1200, 712
    cols, rows, tile, gap = 9, 5, 112, 13
    x0 = (W - (cols * tile + (cols - 1) * gap)) / 2
    y0 = 64
    # periodic-table silhouette: the classic notch at the top-middle holds the legend
    open_slots = {(0, 0), (8, 0)}
    open_slots |= {(c, r) for r in (1, 2) for c in (0, 1, 4, 5, 6, 7, 8)}
    open_slots |= {(c, r) for r in (3, 4) for c in range(9)}
    order = sorted(open_slots)  # column-major: (col, row)

    elements = [(sym, name, gname, gcol) for gname, gcol, items in GROUPS for sym, name in items]
    assert len(elements) == len(order), (len(elements), len(order))

    def pos(c, r):
        return x0 + c * (tile + gap), y0 + r * (tile + gap)

    tiles = []
    for i, ((c, r), (sym, name, _g, gcol)) in enumerate(zip(order, elements)):
        x, y = pos(c, r)
        delay = 0.04 * (c * 2 + r)
        ns = 12.5 if len(name) <= 12 else 11
        tiles.append(f"""
<g class="el" style="animation-delay:{delay:.2f}s">
  <rect x="{x:.1f}" y="{y:.1f}" width="{tile}" height="{tile}" rx="8" fill="{PANEL}" stroke="{gcol}" stroke-opacity=".45"/>
  <rect x="{x:.1f}" y="{y:.1f}" width="{tile}" height="{tile}" rx="8" fill="{gcol}" fill-opacity=".05"/>
  {text(x + 10, y + 21, str(i + 1), size=13, fill=MUTED)}
  {text(x + tile - 10, y + 21, "•", size=13, fill=gcol, anchor="end")}
  {text(x + tile / 2, y + 70, sym, size=40, fill=gcol, weight=600, anchor="middle")}
  {text(x + tile / 2, y + 96, name, size=ns, fill=TEXT, anchor="middle")}
</g>""")

    # title in the top notch
    tx, ty = pos(1, 0)
    title = (text(tx + 6, ty + 52, "The Periodic Table of Things I Build With", size=44, fill=TEXT, family=SERIF,
                  style="font-style:italic")
             + text(tx + 8, ty + 88, "34 elements, mostly stable. reactivity increases sharply near deadlines.",
                    size=14, fill=MUTED))

    # legend in the 2x2 hole (cols 2-3, rows 1-2)
    lx, ly = pos(2, 1)
    legend = [text(lx + 6, ly + 16, "LEGEND", size=13, fill=MUTED, weight=600)]
    for i, (gname, gcol, items) in enumerate(GROUPS):
        yy = ly + 52 + i * 38
        legend.append(f'<rect x="{lx + 6}" y="{yy - 14}" width="18" height="18" rx="4" fill="{gcol}" fill-opacity=".18" stroke="{gcol}"/>')
        legend.append(text(lx + 36, yy, gname, size=15, fill=TEXT))
        legend.append(text(lx + 230, yy, f"{len(items):02d}", size=13, fill=DIM, anchor="end"))

    body = f"""
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>{SCANLINES}</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  {text(40, 38, "fig. 2", size=13, fill=AMBER, weight=500)}
  {text(W - 40, 38, "IUPAC would not approve", size=13, fill=DIM, anchor="end")}
  {title}
  {"".join(legend)}
  {"".join(tiles)}
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" stroke="{LINE}"/>
"""
    css = """
.el{animation:rise .6s cubic-bezier(.2,.7,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
"""
    names = ", ".join(n for _, n, _, _ in elements)
    return svg(W, H, body, css=css, fonts=("mono400", "mono500", "mono600", "serifI"),
               title=f"Periodic table of tools: {names}")


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------
def footer() -> str:
    W, H = 1200, 230
    pts = []
    for i in range(0, W + 1, 6):
        env = math.exp(-((i - 600) / 330) ** 2)
        y = 186 + math.sin(i / 19) * 22 * env + math.sin(i / 7.3) * 4 * env
        pts.append(f"{i},{y:.1f}")
    wave = " ".join(pts)
    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>{SCANLINES}
  <linearGradient id="wg" x1="0" x2="{W}" y1="0" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".3" stop-color="{CYAN}"/>
    <stop offset=".7" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
  </linearGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  {text(48, 82, "That's the whole tape.", size=50, fill=TEXT, family=SERIF, style="font-style:italic")}
  {text(50, 120, "Collaborations, internships and unusual problems welcome. Bring data.", size=15, fill=MUTED)}
  {text(W - 64, 82, "[process completed with exit code 0]", size=15, fill=MINT, anchor="end")}
  <rect x="{W - 58}" y="68" width="9" height="18" fill="{MINT}"><animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>
  {text(W - 48, 120, "EOF", size=13, fill=DIM, anchor="end")}
  <polyline class="wave" points="{wave}" stroke="url(#wg)" stroke-width="2"/>
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" stroke="{LINE}"/>
"""
    css = """
.wave{stroke-dasharray:1400;stroke-dashoffset:1400;animation:trace 2.6s ease-out forwards}
@keyframes trace{to{stroke-dashoffset:0}}
"""
    return svg(W, H, body, css=css, fonts=("mono400", "serifI"), title="That's the whole tape.")


def main() -> None:
    write("banner.svg", banner())
    for num, title, note in SECTIONS:
        write(f"section-{num}.svg", section(num, title, note))
    for p in PROJECTS:
        write(f"card-{p['slug']}.svg", card(p))
    write("periodic-table.svg", periodic())
    write("footer.svg", footer())


if __name__ == "__main__":
    main()
