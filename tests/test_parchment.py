"""Tests for the create_parchment_post.py rendering engine."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import create_parchment_post
from engine import config as C


class TestParchmentRatios(unittest.TestCase):
    """Parchment background must match configured ratio sizes."""

    def _run(self, ratio):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        create_parchment_post.create_post(
            title="TEST",
            body="Test body text.",
            output_path=out,
            ratio=ratio,
        )
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


class TestParchmentContent(unittest.TestCase):
    """Basic rendering and long text wrapping."""

    def test_basic_save(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        path = create_parchment_post.create_post(
            title="ASSUMPTION",
            body="An assumption, though false, if persisted in, will harden into fact.",
            output_path=out,
        )
        self.assertTrue(os.path.isfile(path))
        os.unlink(out)

    def test_long_text(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        long_body = " ".join(["word"] * 100)
        create_parchment_post.create_post(
            title="LONG",
            body=long_body,
            output_path=out,
            ratio="4:5",
        )
        self.assertGreater(os.path.getsize(out), 0)
        os.unlink(out)

    def test_with_portrait(self):
        """If portrait path is invalid, it should gracefully skip it."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            out = f.name
        from PIL import Image
        # Create a tiny placeholder image as fake portrait
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as p:
            portrait = p.name
        Image.new("RGB", (50, 50), "red").save(portrait)

        create_parchment_post.create_post(
            title="PORTRAIT",
            body="Body text.",
            portrait_path=portrait,
            output_path=out,
        )
        self.assertTrue(os.path.isfile(out))
        os.unlink(out)
        os.unlink(portrait)


class TestBackgroundGeneration(unittest.TestCase):
    """create_parchment_background must return correct-sized image."""

    def test_size(self):
        img = create_parchment_post.create_parchment_background(1080, 1080)
        self.assertEqual(img.size, (1080, 1080))

    def test_mode_rgb(self):
        img = create_parchment_post.create_parchment_background(200, 200)
        self.assertEqual(img.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
