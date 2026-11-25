"""Regenerate the site's binary assets from a checkout of laughing-loop/OSflux.

Usage:
    python tools/build_assets.py PATH/TO/OSflux

Needs Python 3 with Pillow (WebP support), fontTools and brotli:
    python -m pip install pillow fonttools brotli

Writes into site/assets/:
    fonts/   IBM Plex Sans (300, 400, 600) and Mono (400, 500) as WOFF2,
             subset to Latin, plus the OFL licence
    brand/   the ink and white lockups and the three-bar small mark used as
             the SVG favicon (copied as they are)
    img/     Studio frames 02 and 07, dark and light, as WebP at 720 and 1200 px
    icons/   favicon-32.png (copied from the Windows icon set) and
             apple-touch-icon.png
and, at the site root, favicon.ico (16, 32 and 48 px frames of the Windows
icon) and og-image.png (1200 x 630).

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
    for name in ["osflux-lockup-ink.svg", "osflux-lockup-white.svg", "osflux-mark-small3-16.svg"]:
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


ICO_SIZES = [16, 32, 48]


def build_icons(src: Path) -> None:
    """Favicons, taken from the brand pack as drawn, never redrawn or resampled.

    favicon-32.png  the full three-bar mark, icons/windows/osflux-32.png
    favicon.ico     the 16, 32 and 48 px frames of icons/windows/osflux.ico
    The SVG favicon (svg/osflux-mark-small3-16.svg) is copied by copy_brand.
    """
    out = ASSETS / "icons"
    out.mkdir(parents=True, exist_ok=True)
    brand = src / "assets" / "brand"
    windows = brand / "icons" / "windows"

    shutil.copyfile(windows / "osflux-32.png", out / "favicon-32.png")

    ico = Image.open(windows / "osflux.ico")
    frames = [ico.ico.getimage((size, size)).convert("RGBA") for size in ICO_SIZES]
    for size, frame in zip(ICO_SIZES, frames):
        if frame.size != (size, size):
            sys.exit(f"osflux.ico has no {size} px frame")
    # The largest frame is the base; the smaller ones are stored as they are
    # (append_images), so Pillow does not scale the 48 px frame down for them.
    frames[-1].save(
        SITE / "favicon.ico",
        format="ICO",
        sizes=[(size, size) for size in ICO_SIZES],
        append_images=frames[:-1],
    )

    tile = Image.open(brand / "icons" / "tile" / "osflux-tile-512.png")
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
