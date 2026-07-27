#!/usr/bin/env python3
import json
import os
import tempfile
import unittest
from unittest import mock

import favorites


class FavoritesTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.cfg = os.path.join(self._tmpdir.name, "command-center", "favorites.json")
        self.patcher = mock.patch.object(favorites, "favorites_path", return_value=self.cfg)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_missing_file_is_empty(self):
        self.assertEqual(favorites.load_favorites(), [])

    def test_corrupt_json_is_empty(self):
        os.makedirs(os.path.dirname(self.cfg), exist_ok=True)
        with open(self.cfg, "w", encoding="utf-8") as fh:
            fh.write("{not-json")
        self.assertEqual(favorites.load_favorites(), [])

    def test_round_trip(self):
        favorites.save_favorites(["a.sh", "b.sh"])
        self.assertEqual(favorites.load_favorites(), ["a.sh", "b.sh"])

    def test_toggle_add_append(self):
        favorites.save_favorites(["a.sh"])
        self.assertTrue(favorites.toggle_favorite("b.sh"))
        self.assertEqual(favorites.load_favorites(), ["a.sh", "b.sh"])

    def test_toggle_remove(self):
        favorites.save_favorites(["a.sh", "b.sh"])
        self.assertFalse(favorites.toggle_favorite("a.sh"))
        self.assertEqual(favorites.load_favorites(), ["b.sh"])

    def test_is_favorite(self):
        favorites.save_favorites(["x.sh"])
        self.assertTrue(favorites.is_favorite("x.sh"))
        self.assertFalse(favorites.is_favorite("y.sh"))

    def test_toggle_prunes_unknown_when_known_given(self):
        favorites.save_favorites(["gone.sh", "keep.sh"])
        self.assertTrue(favorites.toggle_favorite("new.sh", known={"keep.sh", "new.sh"}))
        self.assertEqual(favorites.load_favorites(), ["keep.sh", "new.sh"])

    def test_non_list_json_is_empty(self):
        os.makedirs(os.path.dirname(self.cfg), exist_ok=True)
        with open(self.cfg, "w", encoding="utf-8") as fh:
            json.dump({"a": 1}, fh)
        self.assertEqual(favorites.load_favorites(), [])


if __name__ == "__main__":
    unittest.main()
