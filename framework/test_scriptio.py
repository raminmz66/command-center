#!/usr/bin/env python3
import os
import stat
import tempfile
import unittest

import scriptio


class ScriptioTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = self.tmp.name

    def test_slug_filename(self):
        self.assertEqual(scriptio.slug_filename("My Backup"), "my-backup.sh")
        self.assertEqual(scriptio.slug_filename("  VPN  "), "vpn.sh")

    def test_unique_path_collision(self):
        open(os.path.join(self.dir, "a.sh"), "w").close()
        p = scriptio.unique_path(self.dir, "a.sh")
        self.assertTrue(p.endswith("a-2.sh"))

    def test_round_trip(self):
        path = os.path.join(self.dir, "demo.sh")
        meta = {
            "name": "Demo",
            "icon": "folder-symbolic",
            "desc": "Hello",
            "category": "System",
            "terminal": True,
            "confirm": False,
            "color": "b",
        }
        scriptio.write_script(path, meta, "echo hi\n")
        data = scriptio.read_script(path)
        self.assertEqual(data["meta"]["name"], "Demo")
        self.assertEqual(data["meta"]["terminal"], True)
        self.assertEqual(data["meta"]["color"], "b")
        self.assertEqual(data["body"].strip(), "echo hi")
        mode = os.stat(path).st_mode
        self.assertTrue(mode & stat.S_IXUSR)

    def test_delete(self):
        path = os.path.join(self.dir, "x.sh")
        scriptio.write_script(path, {"name": "X"}, "true\n")
        scriptio.delete_script(path)
        self.assertFalse(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
