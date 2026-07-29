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
            "icon": "💾",
            "desc": "Hello",
            "category": "System",
            "terminal": True,
            "confirm": False,
        }
        scriptio.write_script(path, meta, "echo hi\n")
        data = scriptio.read_script(path)
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        self.assertEqual(data["meta"]["name"], "Demo")
        self.assertEqual(data["meta"]["icon"], "💾")
        self.assertEqual(data["meta"]["terminal"], True)
        self.assertIsNone(data["meta"]["color"])
        self.assertNotIn("# COLOR=", text)
        self.assertEqual(data["body"].strip(), "echo hi")
        mode = os.stat(path).st_mode
        self.assertTrue(mode & stat.S_IXUSR)

    def test_emoji_icon_catalog_size(self):
        from authoring import ICON_CATALOG
        self.assertEqual(len(ICON_CATALOG), 36)

    def test_delete(self):
        path = os.path.join(self.dir, "x.sh")
        scriptio.write_script(path, {"name": "X"}, "true\n")
        scriptio.delete_script(path)
        self.assertFalse(os.path.exists(path))

    def test_read_legacy_color_metadata(self):
        path = os.path.join(self.dir, "legacy.sh")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(
                "#!/bin/bash\n"
                "# NAME=Legacy\n"
                "# ICON=🔒\n"
                "# COLOR=b\n"
                "# TERMINAL=false\n"
                "# CONFIRM=false\n"
                "# CATEGORY=Security\n"
                "\n"
                "echo legacy\n"
            )
        data = scriptio.read_script(path)
        self.assertEqual(data["meta"]["color"], "b")
        self.assertEqual(data["body"].strip(), "echo legacy")


if __name__ == "__main__":
    unittest.main()
