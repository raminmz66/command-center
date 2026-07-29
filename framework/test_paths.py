#!/usr/bin/env python3

import os
import tempfile
import unittest
from unittest import mock

import paths


class PathsTest(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.data = os.path.join(self._tmpdir.name, "share")
        self.patcher = mock.patch.dict(os.environ, {"XDG_DATA_HOME": self.data})
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self._tmpdir.cleanup()

    def test_data_dir_under_xdg(self):
        self.assertEqual(
            paths.data_dir(),
            os.path.join(self.data, "command-center"),
        )

    def test_scripts_dir(self):
        self.assertEqual(
            paths.scripts_dir(),
            os.path.join(self.data, "command-center", "scripts"),
        )

    def test_ensure_scripts_dir_creates(self):
        target = paths.ensure_scripts_dir()
        self.assertTrue(os.path.isdir(target))
        self.assertEqual(target, paths.scripts_dir())

    def test_framework_dir_is_this_package(self):
        self.assertTrue(os.path.isfile(os.path.join(paths.framework_dir(), "paths.py")))

    def test_css_path(self):
        self.assertEqual(
            paths.css_path(),
            os.path.join(paths.framework_dir(), "style.css"),
        )


if __name__ == "__main__":
    unittest.main()
