"""Tests for the create_post.py rendering engine."""

import os
import sys
import tempfile
import unittest

# Ensure engine/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import create_post
from engine import config as C


class _Args:
    """Minimal argparse.Namespace stand-in for testing."""

    def __init__(self, **kw):
        self.template = kw.get("template", "quote")
        self.title = kw.get("title", "Author")
        self.body = kw.get("body", "A sample body text.")
        self.ratio = kw.get("ratio", "1:1")
        self.watermark = kw.get("watermark", "@test")
        self.bg_image = kw.get("bg_image", "")
        self.bg_start = kw.get("bg_start", "#1a1c29")
        self.bg_end = kw.get("bg_end", "#0c0d14")
        self.bg_overlay = kw.get("bg_overlay", 30)
        self.no_card = kw.get("no_card", False)
        self.card_color = kw.get("card_color", "#ffffff")
        self.card_opacity = kw.get("card_opacity", 15)
        self.offset_x = kw.get("offset_x", 0)
        self.offset_y = kw.get("offset_y", 0)
        self.output = kw.get("output", "")


class TestDimensionRatios(unittest.TestCase):
    """Canvas dimensions must match config.RATIO_SIZES."""

    def _run(self, ratio):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        args = _Args(ratio=ratio, output=out)
        create_post.create_post(args)
        from PIL import Image
        img = Image.open(out)
        self.assertEqual(img.size, C.RATIO_SIZES[ratio])
        os.unlink(out)

    def test_1x1(self):
        self._run("1:1")

    def test_4x5(self):
        self._run("4:5")

    def test_9x16(self):
        self._run("9:16")


class TestTemplates(unittest.TestCase):
    """All four templates should render without raising."""

    def _run(self, template, title="Title", body="Body text here."):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        args = _Args(template=template, title=title, body=body, output=out)
        create_post.create_post(args)
        self.assertTrue(os.path.isfile(out))
        self.assertGreater(os.path.getsize(out), 0)
        os.unlink(out)

    def test_quote_template(self):
        self._run("quote", title="Steve Jobs", body="Design is how it works.")

    def test_tip_template(self):
        self._run("tip", title="CLEAN CODE", body="• Use names.\n• Keep functions small.")

    def test_code_template(self):
        self._run("code", title="main.py", body="print('hello')")

    def test_default_template(self):
        self._run("default", title="Hello", body="Some body text.")


class TestGlassCard(unittest.TestCase):
    """Card can be toggled on/off."""

    def test_with_card(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        args = _Args(output=out, no_card=False)
        create_post.create_post(args)
        self.assertTrue(os.path.isfile(out))
        os.unlink(out)

    def test_without_card(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        args = _Args(output=out, no_card=True)
        create_post.create_post(args)
        self.assertTrue(os.path.isfile(out))
        os.unlink(out)


class TestOffsets(unittest.TestCase):
    """Non-zero offsets should not crash rendering."""

    def test_offset(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        args = _Args(output=out, offset_x=30, offset_y=-20)
        create_post.create_post(args)
        self.assertTrue(os.path.isfile(out))
        os.unlink(out)


class TestFontFallback(unittest.TestCase):
    """get_font should always return a usable font object."""

    def test_returns_font(self):
        font = create_post.get_font("NonExistent.ttf", 40)
        self.assertIsNotNone(font)

    def test_returns_font_for_known_names(self):
        font = create_post.get_font("Inter-Regular.ttf", 32)
        self.assertIsNotNone(font)


class TestHexToRgb(unittest.TestCase):
    """Hex-to-RGB conversion correctness."""

    def test_6_digit(self):
        r, g, b, a = create_post.hex_to_rgb("#ff0000")
        self.assertEqual((r, g, b), (255, 0, 0))
        self.assertEqual(a, 255)

    def test_3_digit(self):
        r, g, b, a = create_post.hex_to_rgb("#f00")
        self.assertEqual((r, g, b), (255, 0, 0))

    def test_with_alpha(self):
        _, _, _, a = create_post.hex_to_rgb("#00ff00", alpha=128)
        self.assertEqual(a, 128)


if __name__ == "__main__":
    unittest.main()
