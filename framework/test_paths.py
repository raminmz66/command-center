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

    def test_samples_dir_prefers_usr_share(self):
        usr = paths._USR_SAMPLES

        def fake_isdir(p):
            return p == usr

        with mock.patch("paths.os.path.isdir", side_effect=fake_isdir):
            self.assertEqual(paths.samples_dir(), usr)

    def test_seed_copies_missing_only(self):
        samples = os.path.join(self._tmpdir.name, "samples")
        os.makedirs(samples)
        src = os.path.join(samples, "hello-terminal.sh")
        with open(src, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n")
        os.chmod(src, 0o755)
        with mock.patch.object(paths, "samples_dir", return_value=samples):
            created = paths.seed_sample_scripts()
            self.assertEqual(created, ["hello-terminal.sh"])
            dest = os.path.join(paths.scripts_dir(), "hello-terminal.sh")
            self.assertTrue(os.path.isfile(dest))
            with open(dest, "w", encoding="utf-8") as f:
                f.write("USER\n")
            created2 = paths.seed_sample_scripts()
            self.assertEqual(created2, [])
            with open(dest, encoding="utf-8") as f:
                self.assertEqual(f.read(), "USER\n")

    def test_seed_skips_tombstoned_samples(self):
        samples = os.path.join(self._tmpdir.name, "samples")
        os.makedirs(samples)
        for name in ("hello-terminal.sh", "confirm-demo.sh"):
            path = os.path.join(samples, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write("#!/bin/bash\n")
            os.chmod(path, 0o755)
        cfg = os.path.join(self._tmpdir.name, "config")
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": cfg}):
            with mock.patch.object(paths, "samples_dir", return_value=samples):
                paths.remember_deleted_sample("hello-terminal.sh")
                created = paths.seed_sample_scripts()
                self.assertEqual(created, ["confirm-demo.sh"])
                scripts = paths.scripts_dir()
                self.assertFalse(
                    os.path.exists(os.path.join(scripts, "hello-terminal.sh"))
                )
                self.assertTrue(
                    os.path.isfile(os.path.join(scripts, "confirm-demo.sh"))
                )

    def test_remember_deleted_sample_ignores_non_samples(self):
        samples = os.path.join(self._tmpdir.name, "samples")
        os.makedirs(samples)
        cfg = os.path.join(self._tmpdir.name, "config")
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": cfg}):
            with mock.patch.object(paths, "samples_dir", return_value=samples):
                paths.remember_deleted_sample("my-custom.sh")
                self.assertEqual(paths.load_deleted_samples(), [])


if __name__ == "__main__":
    unittest.main()
