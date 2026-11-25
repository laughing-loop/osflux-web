"""Regenerate the site's binary assets from a checkout of laughing-loop/OSflux.

Usage:
    python tools/build_assets.py PATH/TO/OSflux

Needs Python 3 with Pillow (WebP support), fontTools and brotli:
    python -m pip install pillow fonttools brotli

Writes into site/assets/:
    fonts/   IBM Plex Sans (300, 400, 600) and Mono (400, 500) as WOFF2,
             subset to Latin, plus the OFL licence
    brand/   the ink and white lockups and the small mark (copied as they are)
    img/     Studio frames 02 and 07, dark and light, as WebP at 720 and 1200 px
    icons/   favicon-32.png and apple-touch-icon.png
and site/og-image.png (1200 x 630).

The OSflux repo is only read, never changed.
"""

import shutil
import sys
from pathlib import Path

from fontTools import subset
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ASSETS = SITE / "assets"

BLUE = (0, 104, 219, 255)

# Basic Latin, Latin-1, common punctuation (dashes, quotes, bullet, ellipsis),
# euro, trademark, arrows, minus and multiplication signs.
UNICODES = (
    "U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,"
    "U+2000-206F,U+20AC,U+2122,U+2190-2193,U+2212,U+2215"
)

FONTS = {
    "IBMPlexSans-Light": "plex-sans-300",
    "IBMPlexSans-Regular": "plex-sans-400",
    "IBMPlexSans-SemiBold": "plex-sans-600",
    "IBMPlexMono-Regular": "plex-mono-400",
    "IBMPlexMono-Medium": "plex-mono-500",
}

FRAMES = ["02-image-windows-ready", "07-safety-check-ready"]


def build_fonts(src: Path) -> None:
    out = ASSETS / "fonts"
    out.mkdir(parents=True, exist_ok=True)
    fonts_dir = src / "crates" / "osflux-studio" / "ui" / "fonts"
    for ttf, name in FONTS.items():
        options = subset.Options()
        options.flavor = "woff2"
        options.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "zero"]
        options.name_IDs = ["*"]  # keep copyright and licence names
        options.hinting = False
        font = subset.load_font(str(fonts_dir / f"{ttf}.ttf"), options)
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=subset.parse_unicodes(UNICODES))
        subsetter.subset(font)
        subset.save_font(font, str(out / f"{name}.woff2"), options)
    shutil.copyfile(fonts_dir / "OFL.txt", out / "OFL.txt")


def copy_brand(src: Path) -> None:
    out = ASSETS / "brand"
    out.mkdir(parents=True, exist_ok=True)
    svg = src / "assets" / "brand" / "svg"
    for name in ["osflux-lockup-ink.svg", "osflux-lockup-white.svg", "osflux-mark-small-blue.svg"]:
        shutil.copyfile(svg / name, out / name)


def build_frames(src: Path) -> None:
    out = ASSETS / "img"
    out.mkdir(parents=True, exist_ok=True)
    studio = src / "DOCUMENTS" / "studio"
    for frame in FRAMES:
        for theme in ["dark", "light"]:
            image = Image.open(studio / f"{frame}-{theme}.png").convert("RGB")
            for width in [720, 1200]:
                height = round(image.height * width / image.width)
                resized = image.resize((width, height), Image.LANCZOS)
                resized.save(out / f"{frame}-{theme}-{width}.webp", "WEBP", quality=80, method=6)


def small_mark(size: int) -> Image.Image:
    """Draw osflux-mark-small-blue.svg (16-unit grid) at `size` px.

    The SVG: centre (8.5, 8); ring between radius 4 and 7, open on the left
    where |y| < 4; bars from x -7.5 to 1.5 at y -3..-1 and -5.5 to -0.5 at y 1..3.
    """
    scale = 16  # supersample, then reduce
    s = size * scale / 16  # pixels per unit
    big = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    mask = Image.new("L", big.size, 0)
    d = ImageDraw.Draw(mask)
    cx, cy = 8.5, 8

    def box(x0, y0, x1, y1):
        return [(cx + x0) * s, (cy + y0) * s, (cx + x1) * s - 1, (cy + y1) * s - 1]

    d.ellipse(box(-7, -7, 7, 7), fill=255)
    d.ellipse(box(-4, -4, 4, 4), fill=0)
    d.rectangle(box(-8.5, -4, 0, 4), fill=0)  # opening on the left
    d.rectangle(box(-7.5, -3, 1.5, -1), fill=255)
    d.rectangle(box(-5.5, 1, -0.5, 3), fill=255)
    big.paste(Image.new("RGBA", big.size, BLUE), (0, 0), mask)
    return big.resize((size, size), Image.LANCZOS)


def build_icons(src: Path) -> None:
    out = ASSETS / "icons"
    out.mkdir(parents=True, exist_ok=True)
    small_mark(32).save(out / "favicon-32.png", optimize=True)
    tile = Image.open(src / "assets" / "brand" / "icons" / "tile" / "osflux-tile-512.png")
    tile.convert("RGBA").resize((180, 180), Image.LANCZOS).save(out / "apple-touch-icon.png", optimize=True)


def build_og(src: Path) -> None:
    width, height = 1200, 630
    bg = (20, 20, 20)  # Studio dark bg #141414
    og = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(og)

    lockup = Image.open(src / "assets" / "brand" / "png" / "lockup" / "osflux-lockup-white-2400w.png").convert("RGBA")
    lw = 560
    lockup = lockup.resize((lw, round(lockup.height * lw / lockup.width)), Image.LANCZOS)
    left = 96
    og.paste(lockup, (left, 180), lockup)

    fonts_dir = src / "crates" / "osflux-studio" / "ui" / "fonts"
    light = ImageFont.truetype(str(fonts_dir / "IBMPlexSans-Light.ttf"), 44)
    mono = ImageFont.truetype(str(fonts_dir / "IBMPlexMono-Regular.ttf"), 24)
    y = 180 + lockup.height + 64
    draw.text((left, y), "Bootable USB sticks for Windows and Linux,", font=light, fill=(242, 242, 242))
    draw.text((left, y + 60), "made safely.", font=light, fill=(242, 242, 242))
    draw.text((left, height - 96), "Free and open source  ·  GPL-3.0-or-later", font=mono, fill=(168, 168, 168))
    draw.rectangle([0, 0, width, 8], fill=BLUE[:3])
    og.save(SITE / "og-image.png", optimize=True)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    if not (src / "assets" / "brand").is_dir():
        sys.exit(f"{src} does not look like an OSflux checkout")
    build_fonts(src)
    copy_brand(src)
    build_frames(src)
    build_icons(src)
    build_og(src)
    print("Assets written to", ASSETS)


if __name__ == "__main__":
    main()
