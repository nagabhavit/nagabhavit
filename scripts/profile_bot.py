"""Regenerate the two living SVGs on the profile:

  assets/punchcard.svg  — quote of the week, actually encoded as IBM 029 punches
  assets/telemetry.svg  — contribution history drawn as an oscilloscope trace

Run by .github/workflows/profile.yml on a schedule. Locally:

    GH_TOKEN=... python scripts/profile_bot.py
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import textwrap
import urllib.request

from svgkit import (AMBER, CYAN, DIM, INK, LINE, MINT, MUTED, PANEL, PAPER, PINK,
                    ROOT, SERIF, TEXT, VIOLET, measure, svg, text, write)

LOGIN = os.environ.get("PROFILE_LOGIN", "nagabhavit")
TODAY = dt.datetime.now(dt.timezone.utc).date()


# ==========================================================================
# punch card
# ==========================================================================
ROWS = ["12", "11", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# IBM 029 keypunch code
_SPECIAL = {
    " ": [], "&": ["12"], "-": ["11"], "/": ["0", "1"],
    ".": ["12", "3", "8"], "<": ["12", "4", "8"], "(": ["12", "5", "8"], "+": ["12", "6", "8"],
    "|": ["12", "7", "8"], "!": ["11", "2", "8"], "$": ["11", "3", "8"], "*": ["11", "4", "8"],
    ")": ["11", "5", "8"], ";": ["11", "6", "8"], ",": ["0", "3", "8"], "%": ["0", "4", "8"],
    "_": ["0", "5", "8"], ">": ["0", "6", "8"], "?": ["0", "7", "8"], ":": ["2", "8"],
    "#": ["3", "8"], "@": ["4", "8"], "'": ["5", "8"], "=": ["6", "8"], '"': ["7", "8"],
}


def punches(ch: str) -> list[str]:
    ch = ch.upper()
    if ch.isdigit():
        return [ch]
    if "A" <= ch <= "I":
        return ["12", str(ord(ch) - ord("A") + 1)]
    if "J" <= ch <= "R":
        return ["11", str(ord(ch) - ord("J") + 1)]
    if "S" <= ch <= "Z":
        return ["0", str(ord(ch) - ord("S") + 2)]
    return _SPECIAL.get(ch, [])


def card_text(quote: str) -> str:
    s = "".join(c if punches(c) or c == " " else " " for c in quote.upper())
    return s[:80].ljust(80)


def punchcard(quote: dict, index: int, total: int) -> str:
    W = 1200
    cx, cy, cw = 60, 70, 1080
    inch = cw / 7.375
    ch = 3.25 * inch
    pitch, col0 = 0.087 * inch, 0.25 * inch
    row_pitch = 0.25 * inch
    hole_w, hole_h = 0.055 * inch, 0.125 * inch
    cut = 0.25 * inch

    encoded = card_text(quote["text"])

    lines = textwrap.wrap(f"“{quote['text']}”", 66)
    qy = cy + ch + 70
    ay = qy + (len(lines) - 1) * 44 + 46
    H = int(ay + 44)

    outline = (f"M{cx + cut:.1f},{cy} H{cx + cw - 10} Q{cx + cw},{cy} {cx + cw},{cy + 10} "
               f"V{cy + ch - 10:.1f} Q{cx + cw},{cy + ch:.1f} {cx + cw - 10},{cy + ch:.1f} "
               f"H{cx + 10} Q{cx},{cy + ch:.1f} {cx},{cy + ch - 10:.1f} V{cy + cut:.1f} Z")

    printed, holes, interp = [], [], []
    for c in range(80):
        x = cx + col0 + c * pitch
        delay = f"animation-delay:{0.6 + c * 0.035:.3f}s"
        for r, row in enumerate(ROWS[2:], start=2):
            y = cy + (r + 1) * row_pitch
            printed.append(f'<text x="{x:.1f}" y="{y + 3.2:.1f}">{row}</text>')
        for row in punches(encoded[c]):
            r = ROWS.index(row)
            y = cy + (r + 1) * row_pitch
            holes.append(f'<rect class="h" style="{delay}" x="{x - hole_w / 2:.1f}" '
                         f'y="{y - hole_h / 2:.1f}" width="{hole_w:.1f}" height="{hole_h:.1f}" rx="1"/>')
        if encoded[c] != " ":
            interp.append(f'<text class="h" style="{delay}" x="{x:.1f}" y="{cy + 17:.1f}">'
                          f'{encoded[c].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</text>')
    colnums = "".join(
        f'<text x="{cx + col0 + c * pitch:.1f}" y="{cy + 2.5 * row_pitch + 1:.1f}">{c + 1}</text>'
        f'<text x="{cx + col0 + c * pitch:.1f}" y="{cy + 12.5 * row_pitch + 3:.1f}">{c + 1}</text>'
        for c in range(80)
    )

    quote_lines = "".join(
        text(cx, qy + i * 44, ln, size=36, fill=TEXT, family=SERIF, style="font-style:italic")
        for i, ln in enumerate(lines)
    )
    week = TODAY.isocalendar()
    body = f"""
<defs>
  <filter id="shadow" x="-5%" y="-5%" width="110%" height="120%">
    <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".55"/>
  </filter>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="1" fill="#ffffff" opacity="0.06"/></pattern>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  {text(cx, 42, "fig. 4", size=13, fill=AMBER, weight=500)}
  {text(cx + 64, 42, f"card {index + 1:02d} of {total:02d}  ·  week {week[1]:02d}, {week[0]}  ·  IBM 029 keypunch code", size=13, fill=MUTED)}
  {text(cx + cw, 42, "hold to light to read", size=13, fill=DIM, anchor="end")}
  <g transform="rotate(-0.8 {W / 2} {cy + ch / 2:.0f})" filter="url(#shadow)">
    <path d="{outline}" fill="{PAPER}"/>
    <g font-family="'Plex', monospace" font-size="8.5" fill="#6B5A3A" fill-opacity=".55" text-anchor="middle">{"".join(printed)}</g>
    <g font-family="'Plex', monospace" font-size="5" fill="#6B5A3A" fill-opacity=".45" text-anchor="middle">{colnums}</g>
    <g font-family="'Plex', monospace" font-size="11" font-weight="600" fill="#2B2418" text-anchor="middle">{"".join(interp)}</g>
    <g fill="{INK}">{"".join(holes)}</g>
  </g>
  {quote_lines}
  {text(cx, ay, "— " + quote["who"], size=16, fill=AMBER, weight=500)}
  {text(cx + measure("— " + quote["who"] + "  ", 16, "mono500"), ay, "·  " + quote["source"], size=15, fill=MUTED)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" stroke="{LINE}"/>
"""
    css = """
.h{animation:punch .18s steps(1) both}
@keyframes punch{from{opacity:0}to{opacity:1}}
"""
    return svg(W, H, body, css=css, fonts=("mono400", "mono500", "mono600", "serifI"),
               title=f"“{quote['text']}” — {quote['who']}, {quote['source']}")


def quote_of_the_week() -> tuple[dict, int, int]:
    quotes = json.loads((ROOT / "scripts" / "quotes.json").read_text(encoding="utf-8"))
    idx = ((TODAY.toordinal() - 1) // 7) % len(quotes)  # flips every Monday
    return quotes[idx], idx, len(quotes)


# ==========================================================================
# telemetry
# ==========================================================================
QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""


def fetch_stats() -> dict | None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise RuntimeError(f"GraphQL error: {payload.get('errors')}")
    u = payload["data"]["user"]

    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]

    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    tail = list(reversed(days))
    if tail and tail[0]["contributionCount"] == 0:  # today not over yet
        tail = tail[1:]
    for d in tail:
        if not d["contributionCount"]:
            break
        current += 1

    langs: dict[str, list] = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or MUTED])
            langs[n][0] += e["size"]

    return {
        "total": cal["totalContributions"],
        "weekly": weekly,
        "current": current,
        "longest": longest,
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "langs": sorted(((n, s, c) for n, (s, c) in langs.items()), key=lambda t: -t[1]),
    }


def smooth(points: list[tuple[float, float]], floor: float | None = None) -> str:
    """Catmull-Rom through the points, emitted as cubic Béziers.

    `floor` clamps control points so the curve never dips below the zero line."""
    d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if floor is not None:
            c1, c2 = (c1[0], min(c1[1], floor)), (c2[0], min(c2[1], floor))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def telemetry(stats: dict | None) -> str:
    W, H = 1200, 430
    sx, sy, sw, sh = 40, 74, 700, 316  # scope screen
    grid = []
    for i in range(11):
        x = sx + i * sw / 10
        grid.append(f'<line x1="{x:.1f}" y1="{sy}" x2="{x:.1f}" y2="{sy + sh}" stroke="{MINT}" stroke-opacity="{.22 if i in (0, 5, 10) else .08}"/>')
    for j in range(7):
        y = sy + j * sh / 6
        grid.append(f'<line x1="{sx}" y1="{y:.1f}" x2="{sx + sw}" y2="{y:.1f}" stroke="{MINT}" stroke-opacity="{.22 if j in (0, 3, 6) else .08}"/>')
    for i in range(51):  # minor ticks on the centre axes
        x = sx + i * sw / 50
        grid.append(f'<line x1="{x:.1f}" y1="{sy + sh / 2 - 4:.1f}" x2="{x:.1f}" y2="{sy + sh / 2 + 4:.1f}" stroke="{MINT}" stroke-opacity=".22"/>')

    if stats and stats["weekly"]:
        weekly = stats["weekly"][-53:]
        peak = max(max(weekly), 1)
        pts = [(sx + 8 + i * (sw - 16) / max(len(weekly) - 1, 1),
                sy + sh - 30 - (v / peak) * (sh - 60)) for i, v in enumerate(weekly)]
        trace = smooth(pts, floor=sy + sh - 30)
        scale = f"peak {peak}/wk"
        readouts = [
            ("CONTRIBUTIONS · 1Y", f"{stats['total']:,}", AMBER),
            ("CURRENT STREAK", f"{stats['current']}d", MINT),
            ("LONGEST STREAK", f"{stats['longest']}d", CYAN),
            ("PUBLIC REPOS", str(stats["repos"]), PINK),
            ("STARS EARNED", str(stats["stars"]), VIOLET),
            ("FOLLOWERS", str(stats["followers"]), TEXT),
        ]
        langs = stats["langs"][:6]
        status = "live from the GitHub API · refreshed daily"
    else:
        # noise floor while there's no data yet
        trace = smooth([(sx + i * sw / 70, sy + sh / 2 + math.sin(i * 2.3) * 3 + math.sin(i * 0.7) * 2)
                        for i in range(71)])
        scale = "no signal"
        readouts = [(lbl, "···", col) for lbl, col in (
            ("CONTRIBUTIONS · 1Y", AMBER), ("CURRENT STREAK", MINT), ("LONGEST STREAK", CYAN),
            ("PUBLIC REPOS", PINK), ("STARS EARNED", VIOLET), ("FOLLOWERS", TEXT))]
        langs = []
        status = "awaiting first signal · the profile action fills this in"

    rx0 = 790
    cells = []
    for i, (label, value, col) in enumerate(readouts):
        x = rx0 + (i % 2) * 190
        y = sy + 18 + (i // 2) * 76
        cells.append(text(x, y, label, size=12, fill=MUTED, weight=500))
        cells.append(text(x, y + 40, value, size=36, fill=col, weight=600))

    bar = []
    by = sy + sh - 62
    if langs:
        total = sum(s for _, s, _ in langs)
        x = rx0
        bw = 370
        for n, s, c in langs:
            w = bw * s / total
            bar.append(f'<rect x="{x:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="10" rx="2" fill="{c}"/>')
            x += w
        for i, (n, s, c) in enumerate(langs[:4]):
            lx, ly = rx0 + (i % 2) * 190, by + 32 + (i // 2) * 20
            bar.append(f'<rect x="{lx}" y="{ly - 9}" width="9" height="9" rx="2" fill="{c}"/>')
            bar.append(text(lx + 16, ly, f"{n} {100 * s / total:.0f}%", size=12, fill=MUTED))
    else:
        bar.append(f'<rect x="{rx0}" y="{by}" width="370" height="10" rx="2" fill="{LINE}"/>')
        bar.append(text(rx0, by + 34, "languages: pending", size=12, fill=DIM))
    bar.insert(0, text(rx0, by - 12, "LANGUAGE MIX · BY BYTES", size=12, fill=MUTED, weight=500))

    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <clipPath id="scr"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="6"/></clipPath>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
  <radialGradient id="crt" cx=".5" cy=".5" r=".75">
    <stop offset="0" stop-color="{MINT}" stop-opacity=".07"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  {text(sx, 42, "fig. 3", size=13, fill=AMBER, weight=500)}
  {text(sx + 64, 42, status, size=13, fill=MUTED)}
  {text(W - 40, 42, "CH1 · commits/week · 52 wk window", size=13, fill=DIM, anchor="end")}
  <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="6" fill="#0A0D0B" stroke="{LINE}"/>
  <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="6" fill="url(#crt)"/>
  <g clip-path="url(#scr)">
    {"".join(grid)}
    <path d="{trace}" stroke="{MINT}" stroke-width="6" opacity=".35" filter="url(#glow)" class="tr" pathLength="1"/>
    <path id="trace" d="{trace}" stroke="{MINT}" stroke-width="2.2" stroke-linejoin="round" class="tr" pathLength="1"/>
    <circle r="5" fill="#D8FFE6" opacity="0"><animateMotion dur="6s" repeatCount="indefinite" begin="2.2s"><mpath href="#trace"/></animateMotion>
      <animate attributeName="opacity" to="1" dur="0.01s" begin="2.2s" fill="freeze"/></circle>
    <rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#scan)"/>
  </g>
  {text(sx + 12, sy + 22, "CH1", size=12, fill=MINT, weight=600)}
  {text(sx + sw - 12, sy + 22, scale, size=12, fill=MINT, anchor="end", style="opacity:.8")}
  {text(sx + 12, sy + sh - 10, "52 wk ago", size=11, fill=MINT, style="opacity:.6")}
  {text(sx + sw - 12, sy + sh - 10, "now", size=11, fill=MINT, anchor="end", style="opacity:.6")}
  <line x1="{rx0 - 26}" y1="{sy}" x2="{rx0 - 26}" y2="{sy + sh}" stroke="{LINE}"/>
  {"".join(cells)}
  {"".join(bar)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" stroke="{LINE}"/>
"""
    css = """
.tr{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.2s cubic-bezier(.5,0,.2,1) forwards}
@keyframes draw{to{stroke-dashoffset:0}}
"""
    return svg(W, H, body, css=css, fonts=("mono400", "mono500", "mono600"),
               title="Contribution telemetry for " + LOGIN)


def main() -> None:
    q, idx, total = quote_of_the_week()
    write("punchcard.svg", punchcard(q, idx, total))

    try:
        stats = fetch_stats()
    except Exception as exc:  # keep the last good card rather than blanking it
        print(f"telemetry skipped: {exc}")
        if (ROOT / "assets" / "telemetry.svg").exists():
            return
        stats = None
    if stats is None and (ROOT / "assets" / "telemetry.svg").exists():
        return  # no token (local run): leave the committed card alone
    write("telemetry.svg", telemetry(stats))


if __name__ == "__main__":
    main()
