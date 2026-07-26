#!/usr/bin/env python3

import unittest

from textutil import (
    truncate_description,
    normalize_icon_color,
    matches_query,
    ordered_categories,
    matches_filters,
    normalize_category,
)


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


class NormalizeIconColorTests(unittest.TestCase):

    def test_aliases(self):
        self.assertEqual(normalize_icon_color("r"), "r")
        self.assertEqual(normalize_icon_color("RED"), "r")
        self.assertEqual(normalize_icon_color("green"), "g")
        self.assertEqual(normalize_icon_color("b"), "b")

    def test_invalid(self):
        self.assertIsNone(normalize_icon_color(""))
        self.assertIsNone(normalize_icon_color(None))
        self.assertIsNone(normalize_icon_color("pink"))


class MatchesQueryTests(unittest.TestCase):

    def setUp(self):
        self.meta = {
            "name": "Conky",
            "desc": "Start desktop widgets",
        }

    def test_empty_query_matches(self):
        self.assertTrue(matches_query(self.meta, ""))
        self.assertTrue(matches_query(self.meta, "   "))

    def test_name_hit(self):
        self.assertTrue(matches_query(self.meta, "con"))

    def test_desc_hit(self):
        self.assertTrue(matches_query(self.meta, "widgets"))

    def test_miss(self):
        self.assertFalse(matches_query(self.meta, "vpn"))

    def test_case_insensitive(self):
        self.assertTrue(matches_query(self.meta, "CONKY"))

    def test_missing_desc(self):
        self.assertTrue(matches_query({"name": "Backup"}, "back"))
        self.assertFalse(matches_query({"name": "Backup"}, "widgets"))


class NormalizeCategoryTests(unittest.TestCase):

    def test_empty_becomes_general(self):
        self.assertEqual(normalize_category(""), "General")
        self.assertEqual(normalize_category(None), "General")
        self.assertEqual(normalize_category("  "), "General")

    def test_strip(self):
        self.assertEqual(normalize_category("  System  "), "System")


class OrderedCategoriesTests(unittest.TestCase):

    def test_preferred_order(self):
        self.assertEqual(
            ordered_categories(["General", "Desktop", "Security"]),
            ["Desktop", "Security", "General"],
        )

    def test_extras_sorted(self):
        self.assertEqual(
            ordered_categories(["Zoo", "Desktop", "Alpha"]),
            ["Desktop", "Alpha", "Zoo"],
        )

    def test_unique_casefold(self):
        self.assertEqual(
            ordered_categories(["desktop", "Desktop", "System"]),
            ["Desktop", "System"],
        )

    def test_skips_empty(self):
        self.assertEqual(
            ordered_categories(["", None, "Network"]),
            ["Network"],
        )


class MatchesFiltersTests(unittest.TestCase):

    def setUp(self):
        self.meta = {
            "name": "Conky",
            "desc": "Start desktop widgets",
            "category": "Desktop",
        }

    def test_all_with_query(self):
        self.assertTrue(matches_filters(self.meta, "con", "All"))
        self.assertFalse(matches_filters(self.meta, "vpn", "All"))

    def test_category_only(self):
        self.assertTrue(matches_filters(self.meta, "", "Desktop"))
        self.assertFalse(matches_filters(self.meta, "", "System"))

    def test_and_miss(self):
        self.assertFalse(matches_filters(self.meta, "con", "System"))

    def test_category_case_insensitive(self):
        self.assertTrue(matches_filters(self.meta, "", "desktop"))

    def test_missing_category_is_general(self):
        meta = {"name": "X", "desc": ""}
        self.assertTrue(matches_filters(meta, "", "General"))
        self.assertFalse(matches_filters(meta, "", "Desktop"))


if __name__ == "__main__":
    unittest.main()
