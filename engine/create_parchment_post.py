#!/usr/bin/env python3
"""
Neville Goddard Parchment-Style Quote Card Generator

Generates a 1:1 (or 4:5 / 9:16) social media image with:
- Warm parchment/old paper texture background
- Title (bold serif) + long italic quote text
- Small B&W/sepia portrait photo bottom-left
- Attribution bottom-right

PIL/Pillow only — no external dependencies.

Usage:
    python create_parchment_post.py \
        --title "ASSUMPTION" \
        --body "An assumption, though false, if persisted in, will harden into fact." \
        --portrait /path/to/neville.jpg \
        --output ./output.png \
        --ratio 1:1
"""

import argparse
import math
import os
import random
import textwrap
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

try:
    import config as C          # when run from project root
except ImportError:
    from . import config as C   # when run as package

# ---------------------------------------------------------------------------
# Font paths (macOS system fonts, with graceful fallback)
# ---------------------------------------------------------------------------

_FONT_DIR = "/System/Library/Fonts/Supplemental"

_FONT_BOLD_PATHS = [
    os.path.join(_FONT_DIR, "Georgia Bold.ttf"),
    os.path.join(_FONT_DIR, "Times New Roman Bold.ttf"),
    "/System/Library/Fonts/Palatino.ttc",
]

_FONT_ITALIC_PATHS = [
    os.path.join(_FONT_DIR, "Georgia Italic.ttf"),
    os.path.join(_FONT_DIR, "Times New Roman Italic.ttf"),
    "/System/Library/Fonts/Palatino.ttc",
]

_FONT_REGULAR_PATHS = [
    os.path.join(_FONT_DIR, "Georgia.ttf"),
    os.path.join(_FONT_DIR, "Times New Roman.ttf"),
    "/System/Library/Fonts/Palatino.ttc",
]


def _load_font(paths: List[str], size: int) -> ImageFont.FreeTypeFont:
    """Try loading fonts from a list of paths; fall back to Pillow default."""
    for p in paths:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Ratio presets
# ---------------------------------------------------------------------------

# Backward-compatible alias — source of truth is config.py
RATIO_PRESETS = {k: v for k, v in C.RATIO_SIZES.items()}

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

# Parchment warm beige/cream tones
PARCHMENT_LIGHT = (245, 230, 200)   # #f5e6c8
PARCHMENT_DARK = (232, 213, 163)    # #e8d5a3
TEXT_DARK = (44, 24, 16)            # #2c1810
TEXT_SHADOW = (120, 80, 40)         # subtle shadow

# ---------------------------------------------------------------------------
# Parchment texture generation
# ---------------------------------------------------------------------------


def _lerp_color(c1: Tuple[int, ...], c2: Tuple[int, ...], t: float) -> Tuple[int, ...]:
    """Linearly interpolate between two RGB tuples."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def create_parchment_background(width: int, height: int) -> Image.Image:
    """
    Generate a realistic parchment / aged-paper background.

    Layers:
      1. Gradient base (warm beige → darker cream)
      2. Perlin-like noise for paper grain
      3. Subtle radial vignette
      4. Slight Gaussian blur for softness
    """
    img = Image.new("RGB", (width, height))

    # --- 1. Gradient base ---
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / max(height - 1, 1)
        # Slight vertical gradient: lighter at top, darker at bottom
        color = _lerp_color(PARCHMENT_LIGHT, PARCHMENT_DARK, t * 0.35)
        draw.line([(0, y), (width, y)], fill=color)

    # --- 2. Paper grain noise (fine grain) ---
    noise = Image.new("L", (width, height))
    pixels = noise.load()
    rng = random.Random(42)
    for y in range(height):
        for x in range(width):
            # Subtle noise: ±12 around mid-grey
            pixels[x, y] = 128 + rng.randint(-12, 12)

    # Blur the noise to create softer grain
    noise_blur = noise.filter(ImageFilter.GaussianBlur(radius=1.2))
    # Convert noise to an RGB overlay (warm tinted)
    noise_rgb = Image.new("RGB", (width, height))
    np = noise_rgb.load()
    nb = noise_blur.load()
    for y in range(height):
        for x in range(width):
            v = nb[x, y]
            # Warm-tinted noise (slightly amber)
            np[x, y] = (v, int(v * 0.97), int(v * 0.90))

    # Blend noise with base
    img = Image.blend(img, noise_rgb, 0.08)

    # --- 3. Larger blotchy texture for aged look ---
    blotch = Image.new("L", (width, height))
    bp = blotch.load()
    rng2 = random.Random(99)
    for y in range(height):
        for x in range(width):
            # Low-frequency variations
            bp[x, y] = 128 + rng2.randint(-20, 20)

    blotch = blotch.filter(ImageFilter.GaussianBlur(radius=18))
    # Convert to warm tint
    blotch_rgb = Image.new("RGB", (width, height))
    brp = blotch_rgb.load()
    for y in range(height):
        for x in range(width):
            v = blotch.load()[x, y]
            brp[x, y] = (v, int(v * 0.94), int(v * 0.82))

    img = Image.blend(img, blotch_rgb, 0.12)

    # --- 4. Subtle vignette (darker edges) ---
    # Build a smooth radial gradient using numpy-free pixel math.
    # For each pixel, compute normalised distance from centre and map to
    # a smooth falloff curve: centre bright (keep original), edges dark.
    vignette = Image.new("L", (width, height))
    vp = vignette.load()
    cx, cy = width / 2.0, height / 2.0
    max_dist = math.sqrt(cx ** 2 + cy ** 2)
    for y_v in range(height):
        for x_v in range(width):
            d = math.sqrt((x_v - cx) ** 2 + (y_v - cy) ** 2) / max_dist
            # Smooth hermite falloff: 1 at centre, ~0.7 at edges
            t = min(d / 0.85, 1.0)          # normalise so vignette starts ~85% out
            v = int(255 * (1 - t * t))       # quadratic ease-out
            vp[x_v, y_v] = v

    vig_rgb = Image.new("RGB", (width, height), (180, 150, 110))
    img = Image.composite(img, vig_rgb, vignette)

    # --- 5. Final soft blur for paper smoothness ---
    img = img.filter(ImageFilter.GaussianBlur(radius=0.4))

    return img


# ---------------------------------------------------------------------------
# Text rendering helpers
# ---------------------------------------------------------------------------


def _wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw
) -> List[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple = TEXT_DARK,
    shadow: bool = True,
):
    """Draw text with a subtle drop shadow for depth."""
    x, y = xy
    if shadow:
        draw.text((x + 1, y + 1), text, font=font, fill=TEXT_SHADOW)
    draw.text((x, y), text, font=font, fill=fill)


# ---------------------------------------------------------------------------
# Portrait compositing
# ---------------------------------------------------------------------------


def prepare_portrait(
    portrait_path: str, size: int = 120
) -> Optional[Image.Image]:
    """
    Load portrait, resize, desaturate slightly, apply sepia tint,
    and return with rounded-feel border.
    """
    if not portrait_path or not os.path.isfile(portrait_path):
        return None

    try:
        img = Image.open(portrait_path).convert("RGB")
    except Exception:
        return None

    # Resize to fit within `size x size`
    img.thumbnail((size, size), Image.LANCZOS)

    # Create square canvas
    canvas = Image.new("RGB", (size, size), PARCHMENT_DARK)
    offset_x = (size - img.width) // 2
    offset_y = (size - img.height) // 2
    canvas.paste(img, (offset_x, offset_y))

    # Desaturate
    enhancer = ImageEnhance.Color(canvas)
    canvas = enhancer.enhance(0.3)  # 70% desaturated

    # Sepia tint via colour balance
    sepia = Image.new("RGB", (size, size))
    sp = sepia.load()
    cp = canvas.load()
    for y in range(size):
        for x in range(size):
            r, g, b = cp[x, y]
            # Classic sepia transformation
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            sp[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))

    canvas = sepia

    # Add a subtle border
    border = 3
    bordered = Image.new("RGB", (size + border * 2, size + border * 2), TEXT_DARK)
    bordered.paste(canvas, (border, border))

    return bordered


# ---------------------------------------------------------------------------
# Main composition
# ---------------------------------------------------------------------------


def create_post(
    title: str,
    body: str,
    portrait_path: Optional[str] = None,
    output_path: str = "parchment_post.png",
    ratio: str = "1:1",
    attribution: str = "NEVILLE GODDARD",
) -> str:
    """Generate the full parchment-style quote card and save to disk."""

    width, height = RATIO_PRESETS.get(ratio, RATIO_PRESETS["1:1"])

    # --- Background ---
    bg = create_parchment_background(width, height)
    draw = ImageDraw.Draw(bg)

    # --- Margins & layout ---
    margin_x = int(width * 0.08)
    margin_top = int(height * 0.10)
    margin_bottom = int(height * 0.06)
    content_width = width - margin_x * 2

    # --- Load fonts ---
    title_size = max(28, int(width * 0.044))
    quote_size = max(22, int(width * 0.036))
    attr_size = max(18, int(width * 0.028))

    font_title = _load_font(_FONT_BOLD_PATHS, title_size)
    font_quote = _load_font(_FONT_ITALIC_PATHS, quote_size)
    font_attr = _load_font(_FONT_BOLD_PATHS, attr_size)

    # --- Portrait placement ---
    portrait_img = prepare_portrait(portrait_path, size=int(width * 0.11))
    portrait_w, portrait_h = 0, 0
    if portrait_img:
        portrait_w, portrait_h = portrait_img.size

    # --- Decorative line under title ---
    line_y = margin_top + title_size + 18

    # --- Quote text wrapping ---
    # Reduce available width if portrait is present on the left
    quote_x = margin_x
    quote_max_width = content_width
    # For the title, also leave room for portrait
    title_max_width = content_width

    quote_lines = _wrap_text(body, font_quote, quote_max_width, draw)

    # Calculate total text block height
    line_height = int(quote_size * 1.65)
    total_quote_height = len(quote_lines) * line_height

    # --- Vertical centering of text block ---
    text_block_height = title_size + 18 + total_quote_height
    available_height = height - margin_top - margin_bottom - portrait_h - 40
    text_y = margin_top + max(0, (available_height - text_block_height) // 2)

    # --- Draw title ---
    draw_text_with_shadow(draw, (margin_x, text_y), title.upper(), font_title)
    title_bbox = draw.textbbox((margin_x, text_y), title.upper(), font=font_title)
    title_bottom = text_y + (title_bbox[3] - title_bbox[1])

    # --- Decorative separator line ---
    sep_y = title_bottom + 12
    sep_x1 = margin_x + int(content_width * 0.05)
    sep_x2 = margin_x + int(content_width * 0.95)
    draw.line([(sep_x1, sep_y), (sep_x2, sep_y)], fill=TEXT_DARK, width=2)
    # Small diamond ornament in center
    diamond_cx = (sep_x1 + sep_x2) // 2
    diamond_size = 5
    draw.polygon(
        [
            (diamond_cx, sep_y - diamond_size),
            (diamond_cx + diamond_size, sep_y),
            (diamond_cx, sep_y + diamond_size),
            (diamond_cx - diamond_size, sep_y),
        ],
        fill=TEXT_DARK,
    )

    # --- Draw quote text (italic) ---
    quote_y = sep_y + 20
    for i, line in enumerate(quote_lines):
        ly = quote_y + i * line_height
        draw_text_with_shadow(
            draw, (margin_x, ly), line, font_quote, shadow=True
        )

    # --- Attribution (bottom-right) ---
    attr_y = height - margin_bottom - attr_size - 10
    attr_bbox = draw.textbbox((0, 0), attribution, font=font_attr)
    attr_width = attr_bbox[2] - attr_bbox[0]
    attr_x = width - margin_x - attr_width

    # Separator above attribution
    attr_line_y = attr_y - 10
    line_len = int(attr_width * 0.3)
    draw.line(
        [(attr_x + attr_width // 2 - line_len, attr_line_y),
         (attr_x + attr_width // 2 + line_len, attr_line_y)],
        fill=TEXT_DARK,
        width=1,
    )
    draw_text_with_shadow(
        draw, (attr_x, attr_y), attribution, font_attr, shadow=False
    )

    # --- Composite portrait (bottom-left) ---
    if portrait_img:
        px = margin_x
        py = height - margin_bottom - portrait_h - 10
        bg.paste(portrait_img, (px, py))

    # --- Save ---
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    bg.save(output_path, "PNG", quality=95)
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Neville Goddard parchment-style quote card."
    )
    parser.add_argument(
        "--title", type=str, required=True, help="Title text (bold, top of card)"
    )
    parser.add_argument(
        "--body", type=str, required=True, help="Quote text (italic body)"
    )
    parser.add_argument(
        "--portrait", type=str, default=None, help="Path to portrait image"
    )
    parser.add_argument(
        "--output", type=str, default="parchment_post.png", help="Output file path"
    )
    parser.add_argument(
        "--ratio",
        type=str,
        default="1:1",
        choices=["1:1", "4:5", "9:16"],
        help="Aspect ratio preset (default: 1:1)",
    )
    parser.add_argument(
        "--attribution",
        type=str,
        default="NEVILLE GODDARD",
        help="Attribution text at bottom-right",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for texture generation"
    )
    args = parser.parse_args()

    random.seed(args.seed)

    out = create_post(
        title=args.title,
        body=args.body,
        portrait_path=args.portrait,
        output_path=args.output,
        ratio=args.ratio,
        attribution=args.attribution,
    )
    print(f"✓ Saved: {out}")


if __name__ == "__main__":
    main()
