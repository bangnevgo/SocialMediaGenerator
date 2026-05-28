"""Tests for the ai_generator.py API helpers."""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import ai_generator


class TestTokenValidation(unittest.TestCase):
    """_validate_token should reject empty / short tokens."""

    def test_empty_token(self):
        self.assertFalse(ai_generator._validate_token("", "TEST_KEY"))

    def test_none_token(self):
        self.assertFalse(ai_generator._validate_token(None, "TEST_KEY"))

    def test_short_token(self):
        """Short tokens log a warning but are still accepted (len < 10)."""
        self.assertFalse(ai_generator._validate_token("short", "TEST_KEY"))

    def test_valid_token(self):
        self.assertTrue(ai_generator._validate_token("hf_validtoken12345", "TEST_KEY"))


class TestProviderArgumentValidation(unittest.TestCase):
    """Each provider function should fail gracefully when token is missing."""

    @patch.dict(os.environ, {}, clear=True)
    def test_replicate_no_token(self):
        result = ai_generator.generate_replicate("prompt", "image", "/tmp/out.png")
        self.assertFalse(result)

    @patch.dict(os.environ, {}, clear=True)
    def test_huggingface_no_token(self):
        result = ai_generator.generate_huggingface("prompt", "image", "/tmp/out.png")
        self.assertFalse(result)

    @patch.dict(os.environ, {}, clear=True)
    def test_openai_no_token(self):
        result = ai_generator.generate_openai("prompt", "image", "/tmp/out.png")
        self.assertFalse(result)

    def test_openai_video_unsupported(self):
        """OpenAI provider should reject video type even with a valid key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk_test_validkey12345"}):
            result = ai_generator.generate_openai("prompt", "video", "/tmp/out.mp4")
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
