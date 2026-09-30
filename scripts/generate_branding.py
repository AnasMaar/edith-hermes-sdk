"""Generate the README's pixel banner and matching ASCII/ANSI assets.

The vector lettering uses the same original seven-row glyphs as the text assets.
No installed fonts, image service, or network connection is required.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

TITLE = "HERMES PYTHON ADK"
GLYPHS = {
    " ": ("000",) * 7,
    "A": ("01110", "11011", "11011", "11111", "11011", "11011", "11011"),
    "D": ("11110", "11011", "11011", "11011", "11011", "11011", "11110"),
    "E": ("11111", "11000", "11000", "11110", "11000", "11000", "11111"),
    "H": ("11011", "11011", "11011", "11111", "11011", "11011", "11011"),
    "K": ("11011", "11011", "11110", "11100", "11110", "11011", "11011"),
    "M": ("11011", "11111", "11111", "11011", "11011", "11011", "11011"),
    "N": ("110011", "111011", "111111", "111111", "110111", "110111", "110011"),
    "O": ("01110", "11011", "11011", "11011", "11011", "11011", "01110"),
    "P": ("11110", "11011", "11011", "11110", "11000", "11000", "11000"),
    "R": ("11110", "11011", "11011", "11110", "11110", "11011", "11011"),
    "S": ("01111", "11000", "11000", "01110", "00011", "00011", "11110"),
    "T": ("11111", "01110", "01110", "01110", "01110", "01110", "01110"),
    "Y": ("11011", "11011", "11011", "01110", "01110", "01110", "01110"),
}


def rows() -> list[str]:
    return ["0".join(GLYPHS[letter][row] for letter in TITLE) for row in range(7)]


def vector_path(matrix: list[str], pixel: int = 11) -> str:
    commands = []
    for y, row in enumerate(matrix):
        x = 0
        while x < len(row):
            if row[x] == "0":
                x += 1
                continue
            start = x
            while x < len(row) and row[x] == "1":
                x += 1
            commands.append(
                f"M{start * pixel},{y * pixel}h{(x - start) * pixel}v{pixel}"
                f"h{-((x - start) * pixel)}z"
            )
    return " ".join(commands)


def svg(matrix: list[str]) -> str:
    path = vector_path(matrix)
    width = len(matrix[0]) * 11
    left = (1200 - width - 10) // 2
    layers = "\n".join(
        f'      <use href="#lettering" transform="translate({offset} {offset})" fill="#492653"/>'
        for offset in range(9, 0, -1)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="220" viewBox="0 0 1200 220" role="img" aria-labelledby="title description">
  <title id="title">{escape(TITLE.title().replace("Adk", "ADK"))}</title>
  <desc id="description">Original pixel lettering in a pink-to-violet gradient, with a layered purple shadow, on a dark background. Build, provision, control.</desc>
  <defs>
    <linearGradient id="face" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
      <stop offset="0" stop-color="#ffacd9"/>
      <stop offset="0.44" stop-color="#f078c6"/>
      <stop offset="1" stop-color="#b68bff"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop stop-color="#d961ac"/>
      <stop offset="1" stop-color="#9670d8"/>
    </linearGradient>
    <path id="lettering" d="{path}"/>
  </defs>
  <rect width="1200" height="220" fill="#0d1117"/>
  <rect x="18" y="24" width="1164" height="172" rx="3" fill="#120f19" stroke="#302039"/>
  <g transform="translate({left} 65)" shape-rendering="crispEdges">
    <use href="#lettering" transform="translate(13 13)" fill="none" stroke="#78416e" stroke-width="1"/>
    <use href="#lettering" transform="translate(10 10)" fill="none" stroke="url(#edge)" stroke-width="1"/>
{layers}
    <use href="#lettering" fill="url(#face)"/>
    <use href="#lettering" transform="translate(-1 -1)" fill="none" stroke="#ffd0eb" stroke-width="0.55" opacity="0.35"/>
  </g>
  <text x="600" y="177" text-anchor="middle" fill="#c39ab9" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="12" letter-spacing="4">BUILD · PROVISION · CONTROL</text>
</svg>
'''


def ansi(matrix: list[str]) -> str:
    lines = []
    for row in matrix:
        cells = []
        for x, bit in enumerate(row):
            amount = x / (len(row) - 1)
            color = tuple(
                round(a + (b - a) * amount)
                for a, b in zip((255, 153, 212), (176, 126, 255), strict=True)
            )
            cells.append(f"\x1b[38;2;{color[0]};{color[1]};{color[2]}m#" if bit == "1" else " ")
        lines.append("".join(cells).rstrip() + "\x1b[0m")
    return "\n".join(lines) + "\n"


def main() -> None:
    destination = Path(__file__).resolve().parents[1] / "assets" / "branding"
    destination.mkdir(parents=True, exist_ok=True)
    matrix = rows()
    contents = {
        "hermes-python-adk.svg": svg(matrix),
        "hermes-python-adk.txt": "\n".join(
            row.replace("1", "#").replace("0", " ").rstrip() for row in matrix
        )
        + "\n",
        "hermes-python-adk.ansi": ansi(matrix),
    }
    for name, content in contents.items():
        (destination / name).write_text(content, encoding="utf-8", newline="\n")
        print(f"Generated assets/branding/{name}")


if __name__ == "__main__":
    main()
