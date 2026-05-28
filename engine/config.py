"""
Centralised layout constants for all Python rendering engines.

Keeping these in one place means changing a margin or font size only
requires one edit instead of hunting through five files.
"""

# ── Canvas / Image dimensions per aspect ratio ──────────────────────────
RATIO_SIZES = {
    "1:1":  (1080, 1080),
    "4:5":  (1080, 1350),
    "9:16": (1080, 1920),
}

# ── Card / safe-zone geometry ───────────────────────────────────────────
CARD_MARGIN = 80               # px – outer margin on each side
CARD_RADIUS = 24               # px – corner roundness for glass card
CARD_BORDER_WIDTH = 2          # px
CARD_BORDER_RGBA = (255, 255, 255, 80)

# Vertical safe-zone offsets for 9:16 (Stories / Reels)
STORY_TOP_SAFE = 220
STORY_BOTTOM_SAFE = 250

# Glassmorphism blur radius
CARD_BLUR_RADIUS = 15

# ── Font size ratios (relative to canvas width) ─────────────────────────
TITLE_SIZE_RATIO = 0.044       # 4.4 % of width
QUOTE_SIZE_RATIO = 0.036
ATTR_SIZE_RATIO = 0.028
MIN_TITLE_SIZE = 28
MIN_QUOTE_SIZE = 22
MIN_ATTR_SIZE = 18

# ── Font file names ─────────────────────────────────────────────────────
FONT_TITLE_REGULAR = "PlayfairDisplay-Regular.ttf"
FONT_TITLE_ITALIC  = "PlayfairDisplay-Italic.ttf"
FONT_BODY_REGULAR  = "Inter-Regular.ttf"
FONT_BODY_BOLD     = "Montserrat-Bold.ttf"
FONT_CODE          = "Inter-Regular.ttf"

# ── Font fallbacks (system fonts keyed by prefix) ───────────────────────
FONT_FALLBACK = {
    "Inter":      "/System/Library/Fonts/Helvetica.ttc",
    "Montserrat": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "Playfair":   "/System/Library/Fonts/Supplemental/Georgia.ttf",
}

# ── Layout ratios ───────────────────────────────────────────────────────
LINE_HEIGHT_MULT = 1.25          # line_height = glyph_height × this
CONTENT_INSET = 40               # extra inner padding inside card
META_BOTTOM_GAP = 60             # space between card bottom and watermark

# ── Video defaults ──────────────────────────────────────────────────────
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_SLIDE_DURATION = 3         # seconds per slide
VIDEO_SCALE_FILTER = (
    "scale=1080:1920:force_original_aspect_ratio=decrease,"
    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
)
