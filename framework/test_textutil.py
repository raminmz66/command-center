#!/usr/bin/env python3

import unittest

from textutil import truncate_description


class TruncateDescriptionTests(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(truncate_description(""), "")

    def test_short_unchanged(self):
        self.assertEqual(
            truncate_description("Start desktop widgets"),
            "Start desktop widgets",
        )

    def test_exact_max_unchanged(self):
        text = "a" * 48
        self.assertEqual(truncate_description(text, 48), text)

    def test_long_truncated_with_ellipsis(self):
        text = "Show automatic update lockdown status for the whole system"
        result = truncate_description(text, 48)
        self.assertTrue(result.endswith("…"))
        self.assertEqual(len(result), 48)
        self.assertFalse(result[:-1].endswith(" "))

    def test_custom_max_len(self):
        self.assertEqual(
            truncate_description("abcdefghij", 5),
            "abcd…",
        )


if __name__ == "__main__":
    unittest.main()
