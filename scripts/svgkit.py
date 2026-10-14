"""Tiny helpers shared by the asset generators.

Every SVG in assets/ embeds its own subset of IBM Plex Mono and Instrument Serif
as base64 woff2, so it renders the same through GitHub's image proxy (which
can't fetch web fonts) on every OS.
"""

from __future__ import annotations

import base64
import re
import io
from functools import lru_cache
from html import escape, unescape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

# palette -------------------------------------------------------------------
INK = "#0E0F13"
PANEL = "#15171D"
LINE = "#262A33"
MUTED = "#8A8F98"
DIM = "#4A4F59"
TEXT = "#E8E6E1"
AMBER = "#FFB547"
MINT = "#7CF5A8"
CYAN = "#5CE1E6"
PINK = "#FF5D8F"
VIOLET = "#A98BFF"
PAPER = "#EFE4C6"

MONO = "'Plex', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SERIF = "'Instrument', 'Times New Roman', Georgia, serif"

_FACES = {
    "mono400": ("Plex", "normal", 400, "plexmono-400.woff2"),
    "mono500": ("Plex", "normal", 500, "plexmono-500.woff2"),
    "mono600": ("Plex", "normal", 600, "plexmono-600.woff2"),
    "serif": ("Instrument", "normal", 400, "instrument-serif.woff2"),
    "serifI": ("Instrument", "italic", 400, "instrument-serif-italic.woff2"),
}


@lru_cache(maxsize=None)
def _subset(file: str, chars: str) -> bytes:
    """Cut a font down to just the glyphs this SVG uses (keeps each file small)."""
    font = TTFont(FONTS / file)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern"]
    sub = subset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return buf.getvalue()


@lru_cache(maxsize=None)
def _metrics(key: str):
    font = TTFont(FONTS / _FACES[key][3])
    return font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm


def measure(s: str, size: float, face: str = "serifI") -> float:
    """Advance width of a string in px, straight from the font's hmtx table."""
    cmap, hmtx, upm = _metrics(face)
    return sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in s) * size / upm


def font_css(*faces: str, chars: str) -> str:
    out = []
    for key in faces:
        family, style, weight, file = _FACES[key]
        data = base64.b64encode(_subset(file, chars)).decode()
        out.append(
            f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    return "\n".join(out)


def svg(width: int, height: int, body: str, *, css: str = "", fonts=(), title: str = "") -> str:
    chars = "".join(sorted(set(unescape(re.sub(r"<[^>]+>", " ", body)) + title))) + " "
    style = font_css(*fonts, chars=chars) + "\n" + css
    t = f"<title>{escape(title)}</title>" if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" fill="none">{t}'
        f"<style>{style}</style>{body}</svg>\n"
    )


def text(x, y, s, *, size=16, fill=TEXT, family=MONO, weight=400, anchor="start",
         style="", cls="", extra="") -> str:
    c = f' class="{cls}"' if cls else ""
    st = f";{style}" if style else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}" style="white-space:pre{st}"{c} {extra}>{escape(s)}</text>'
    )


def write(name: str, content: str) -> Path:
    path = ASSETS / name
    path.write_text(content, encoding="utf-8")
    return path
