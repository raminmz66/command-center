#!/usr/bin/env python3
import unittest

import empty_state


class EmptyStateTests(unittest.TestCase):
    def test_empty_when_no_commands(self):
        self.assertTrue(empty_state.is_library_empty([]))

    def test_not_empty_with_commands(self):
        self.assertFalse(empty_state.is_library_empty([("/x.sh", {})]))

    def test_copy_constants(self):
        self.assertEqual(empty_state.TITLE, "No commands yet")
        self.assertEqual(
            empty_state.BODY,
            "Create your first command to fill this launcher.",
        )
        self.assertEqual(empty_state.CTA, "Create command")


if __name__ == "__main__":
    unittest.main()
