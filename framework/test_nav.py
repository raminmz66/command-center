#!/usr/bin/env python3

import unittest

from nav import next_highlight_index


class NavTest(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(next_highlight_index(None, "Down", 0))

    def test_first_down_right(self):
        self.assertEqual(next_highlight_index(None, "Down", 5), 0)
        self.assertEqual(next_highlight_index(None, "Right", 5), 0)

    def test_first_up_left(self):
        self.assertEqual(next_highlight_index(None, "Up", 5), 4)
        self.assertEqual(next_highlight_index(None, "Left", 5), 4)

    def test_horizontal(self):
        self.assertEqual(next_highlight_index(1, "Right", 5), 2)
        self.assertEqual(next_highlight_index(0, "Left", 5), 0)

    def test_vertical(self):
        self.assertEqual(next_highlight_index(0, "Down", 6, columns=3), 3)
        self.assertEqual(next_highlight_index(4, "Up", 6, columns=3), 1)
        self.assertEqual(next_highlight_index(5, "Down", 6, columns=3), 5)


if __name__ == "__main__":
    unittest.main()
