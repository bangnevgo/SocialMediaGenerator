import os
import sys
import argparse
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

try:
    import config as C          # when run from project root
except ImportError:
    from . import config as C   # when run as package

logger = logging.getLogger(__name__)

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# Map of custom fonts → readable system fallbacks
_FONT_FALLBACK = {
    "Inter":        "/System/Library/Fonts/Helvetica.ttc",
    "Montserrat":   "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "Playfair":     "/System/Library/Fonts/Supplemental/Georgia.ttf",
}


def get_font(font_name, size):
    """Retrieve font with fallback to system fonts if not found.

    Logs a warning so the designer knows the layout may differ from the
    intended look.  Falls back gracefully through:
      1. Custom font in engine/fonts/
      2. System fallback (mapped above)
      3. Pillow default bitmap font (last resort)
    """
    custom = os.path.join(FONT_DIR, font_name)
    if os.path.exists(custom):
        try:
            return ImageFont.truetype(custom, size)
        except Exception as exc:
            logger.warning("Could not load %s (%s), trying system fallback.", font_name, exc)

    # Try system fallback
    for prefix, sys_path in _FONT_FALLBACK.items():
        if font_name.startswith(prefix) and os.path.exists(sys_path):
            logger.warning(
                "Using system fallback for %s → %s — layout may differ from browser preview.",
                font_name, sys_path,
            )
            return ImageFont.truetype(sys_path, size)

    logger.error(
        "No suitable font found for %s.  Falling back to Pillow default (bitmap). "
        "Run python3 engine/setup_fonts.py to download proper fonts.",
        font_name,
    )
    return ImageFont.load_default()

def draw_gradient(width, height, start_color, end_color):
    """Create a beautiful linear gradient background."""
    base = Image.new("RGBA", (width, height), start_color)
    top = Image.new("RGBA", (width, height), end_color)
    mask = Image.new("L", (width, height))
    for y in range(height):
        # Linear transition from top (0) to bottom (255)
        mask.putpixel((0, y), int(255 * (y / height)))
    # Stretch mask to full width
    mask = mask.resize((width, height))
    return Image.composite(top, base, mask)

def hex_to_rgb(hex_str, alpha=255):
    """Convert hex string to RGBA tuple."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    rgb = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return rgb + (alpha,)

def draw_wrapped_text(draw, font, text, max_width, start_y, line_height_mult=1.2, fill="white", align="center", center_x=540):
    """Helper to wrap and draw text, returning the ending Y coordinate.

    Supports explicit newlines (\n) in text, mirroring the JS canvas version.
    Each paragraph (separated by \n) is word-wrapped independently.
    """
    # Split by explicit newlines first, then word-wrap each paragraph
    paragraphs = text.split("\n")
    lines = []
    for para in paragraphs:
        words = para.split(" ")
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        if current_line:
            lines.append(" ".join(current_line))
        
    # Pre-calculate line height once per font (not per line)
    sample_bbox = draw.textbbox((0, 0), "AygHj", font=font)
    line_h = int((sample_bbox[3] - sample_bbox[1]) * C.LINE_HEIGHT_MULT)

    # Draw each line
    y = start_y
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_w = line_bbox[2] - line_bbox[0]

        if align == "center":
            x = center_x - (line_w / 2)
        elif align == "right":
            x = (center_x + max_width/2) - line_w
        else: # left
            x = center_x - max_width/2

        draw.text((x, y), line, font=font, fill=fill)
        y += line_h

    return y

def simulate_glassmorphism(img, box_coords, blur_radius=20, fill_color=(255, 255, 255, 30), border_color=(255, 255, 255, 80)):
    """Apply premium glassmorphic frosted card effect over the background.
    Returns the modified image (may be a new RGBA image due to alpha compositing)."""
    x0, y0, x1, y1 = box_coords
    
    # 1. Ensure RGBA mode
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 2. Crop card area
    card_area = img.crop((x0, y0, x1, y1))
    
    # 3. Blur it
    blurred = card_area.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # 4. Increase brightness/contrast slightly for frosted look
    enhancer = ImageEnhance.Brightness(blurred)
    blurred = enhancer.enhance(1.10)
    
    # 5. Paste blurred background back (fully opaque)
    img.paste(blurred, (x0, y0))
    
    # 6. Create proper alpha overlay for glass effect
    # NOTE: draw.rectangle with RGBA fill on the SAME image just SETS pixel values,
    # it does NOT alpha-composite. Use a separate overlay layer instead.
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay, 'RGBA')
    odraw.rectangle([x0, y0, x1, y1], fill=fill_color)
    odraw.rectangle([x0, y0, x1, y1], outline=border_color, width=2)
    
    # 7. Alpha-composite overlay onto img
    return Image.alpha_composite(img, overlay)

def create_post(args):
    # Set sizes based on platform/ratio
    width, height = C.RATIO_SIZES.get(args.ratio, C.RATIO_SIZES["1:1"])
        
    # 1. Background Setup
    if args.bg_image and os.path.exists(args.bg_image):
        img = Image.open(args.bg_image).convert("RGBA")
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    else:
        # Use gradient or fallback solid
        start_bg = hex_to_rgb(args.bg_start)
        end_bg = hex_to_rgb(args.bg_end)
        img = draw_gradient(width, height, start_bg, end_bg)
        
    # Apply global background overlay (darken background for readability)
    if args.bg_overlay > 0:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, int(255 * (args.bg_overlay / 100))))
        img = Image.alpha_composite(img, overlay)
        
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 2. Draw Glass Card (if enabled or template matches tip/code)
    card_margin = C.CARD_MARGIN
    card_width = width - (card_margin * 2)
    card_height = height - (card_margin * 2)

    # Adjust card height for stories (leave header/footer safe zones)
    card_y_start = card_margin
    card_y_end = height - card_margin
    if args.ratio == "9:16":
        card_y_start = C.STORY_TOP_SAFE
        card_y_end = height - C.STORY_BOTTOM_SAFE
        
    # Apply offset positioning
    card_y_start += args.offset_y
    card_y_end += args.offset_y
    card_rect = [card_margin + args.offset_x, card_y_start, width - card_margin + args.offset_x, card_y_end]
    
    if not args.no_card:
        img = simulate_glassmorphism(
            img,
            card_rect,
            blur_radius=C.CARD_BLUR_RADIUS,
            fill_color=hex_to_rgb(args.card_color, int(255 * (args.card_opacity / 100))),
            border_color=C.CARD_BORDER_RGBA,
        )
        draw = ImageDraw.Draw(img, "RGBA")
        
    # 3. Draw Brand/Watermark
    if args.watermark:
        watermark_font = get_font("Inter-Regular.ttf", 32)
        # Position at the bottom of the card or canvas
        y_watermark = card_y_end - 60 if not args.no_card else height - 70 + args.offset_y
        bbox = draw.textbbox((0, 0), args.watermark, font=watermark_font)
        w = bbox[2] - bbox[0]
        draw.text((width/2 - w/2 + args.offset_x, y_watermark), args.watermark, font=watermark_font, fill=hex_to_rgb("#FFFFFF", 180))
        
    # 4. Render Layouts based on templates
    content_width = card_width - 80 # Safe text margins within card
    center_x = width / 2 + args.offset_x
    
    if args.template == "quote":
        # Quote Card Layout (Centered, serif typography, decorative quotes)
        title_font = get_font("PlayfairDisplay-Regular.ttf", 46)
        author_font = get_font("PlayfairDisplay-Italic.ttf", 36)
        
        # Draw decorative quotation mark
        quote_mark_font = get_font("PlayfairDisplay-Regular.ttf", 160)
        quote_bbox = draw.textbbox((0, 0), "“", font=quote_mark_font)
        qw = quote_bbox[2] - quote_bbox[0]
        qh = quote_bbox[3] - quote_bbox[1]
        draw.text((center_x - qw/2, card_y_start + 60), "“", font=quote_mark_font, fill=hex_to_rgb("#FFFFFF", 100))
        
        # Draw wrapped quote text
        start_y = card_y_start + 60 + qh + 20
        y_end = draw_wrapped_text(
            draw, 
            title_font, 
            args.body or "Add your quote here...", 
            content_width, 
            start_y, 
            align="center", 
            center_x=center_x
        )
        
        # Draw Author/Subtitle
        if args.title:
            author_text = f"— {args.title}"
            draw_wrapped_text(
                draw, 
                author_font, 
                author_text, 
                content_width, 
                y_end + 30, 
                align="center", 
                center_x=center_x,
                fill=hex_to_rgb("#E0E0E0", 220)
            )
            
    elif args.template == "tip":
        # Tech Tips / Informational Post
        title_font = get_font("Montserrat-Bold.ttf", 52)
        body_font = get_font("Inter-Regular.ttf", 38)
        
        # Title (bold header)
        start_y = card_y_start + 70
        y_end = draw_wrapped_text(
            draw, 
            title_font, 
            args.title or "TIP TITLE", 
            content_width, 
            start_y, 
            align="center", 
            center_x=center_x,
            fill=hex_to_rgb("#64FFDA") # Mint cyan accent
        )
        
        # Horizontal divider line
        line_y = y_end + 30
        draw.line([center_x - 150, line_y, center_x + 150, line_y], fill=hex_to_rgb("#64FFDA", 120), width=3)
        
        # Body list or paragraph
        draw_wrapped_text(
            draw, 
            body_font, 
            args.body or "Add tip details...", 
            content_width, 
            line_y + 40, 
            align="left" if "\n" in (args.body or "") else "center", 
            center_x=center_x
        )
        
    elif args.template == "code":
        # Code Highlight Frame (glass container mimicking VS Code editor)
        title_font = get_font("Montserrat-Bold.ttf", 40)
        code_font = get_font("Inter-Regular.ttf", 34)
        
        # Draw editor window controls (red, yellow, green window buttons)
        btn_y = card_y_start + 40
        card_x_start = card_margin + args.offset_x
        draw.ellipse([card_x_start + 40, btn_y, card_x_start + 58, btn_y + 18], fill=hex_to_rgb("#FF5F56"))
        draw.ellipse([card_x_start + 68, btn_y, card_x_start + 86, btn_y + 18], fill=hex_to_rgb("#FFBD2E"))
        draw.ellipse([card_x_start + 96, btn_y, card_x_start + 114, btn_y + 18], fill=hex_to_rgb("#27C93F"))
        
        # File title header
        header_font = get_font("Inter-Regular.ttf", 28)
        header_bbox = draw.textbbox((0, 0), args.title or "code.py", font=header_font)
        hw = header_bbox[2] - header_bbox[0]
        draw.text((center_x - hw/2, btn_y - 4), args.title or "code.py", font=header_font, fill=hex_to_rgb("#AAAAAA"))
        
        # Draw divider
        draw.line([card_x_start + 20, btn_y + 35, width - card_margin - 20 + args.offset_x, btn_y + 35], fill=hex_to_rgb("#FFFFFF", 30), width=1)
        
        # Draw code blocks
        code_body = args.body or "print('Hello, Social Media!')"
        draw_wrapped_text(
            draw, 
            code_font, 
            code_body, 
            content_width, 
            btn_y + 60, 
            align="left", 
            center_x=center_x,
            fill=hex_to_rgb("#A9B7C6") # standard IDE gray/white text
        )
 
    else:
        # Default simple template
        title_font = get_font("Montserrat-Bold.ttf", 48)
        body_font = get_font("Inter-Regular.ttf", 36)
        
        y_end = draw_wrapped_text(draw, title_font, args.title or "", content_width, card_y_start + 80, align="center", center_x=center_x)
        draw_wrapped_text(draw, body_font, args.body or "", content_width, y_end + 50, align="center", center_x=center_x)
        
    # 5. Flatten alpha & Save Output
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    if img.mode == 'RGBA':
        # Flatten transparency over dark background so Telegram/etc display correctly
        flat = Image.new('RGB', img.size, (15, 10, 20))
        flat.paste(img, (0, 0), img.split()[3])
        img = flat
    img.save(args.output, "PNG")
    print(f"Post successfully generated at: {args.output}")

def main():
    parser = argparse.ArgumentParser(description="Programmatic Social Media Post Layout Generator")
    parser.add_argument("--template", choices=["default", "quote", "tip", "code"], default="default", help="Design layout template")
    parser.add_argument("--title", default="", help="Headline text / Code file name / Quote Author")
    parser.add_argument("--body", default="", help="Subtext / Tips block / Code snippet")
    parser.add_argument("--ratio", choices=["1:1", "4:5", "9:16"], default="1:1", help="Image aspect ratio")
    parser.add_argument("--watermark", default="", help="User handle or brand name (bottom of the card)")
    
    # Background options
    parser.add_argument("--bg_image", default="", help="Path to background image (takes precedence over gradients)")
    parser.add_argument("--bg_start", default="#121214", help="Gradient start background hex color")
    parser.add_argument("--bg_end", default="#1F1F24", help="Gradient end background hex color")
    parser.add_argument("--bg_overlay", type=int, default=30, help="Background overlay opacity percentage (0-100)")
    
    # Card options
    parser.add_argument("--no_card", action="store_true", help="Disable the glassmorphic card container")
    parser.add_argument("--card_color", default="#FFFFFF", help="Hex color of the card")
    parser.add_argument("--card_opacity", type=int, default=15, help="Card opacity percentage (0-100)")
    
    # Offset positioning
    parser.add_argument("--offset_x", type=int, default=0, help="Horizontal layout offset shift in pixels")
    parser.add_argument("--offset_y", type=int, default=0, help="Vertical layout offset shift in pixels")
    
    parser.add_argument("--output", required=True, help="Path to write the final PNG image")
    
    args = parser.parse_args()
    create_post(args)

if __name__ == "__main__":
    main()
