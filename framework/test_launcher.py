#!/usr/bin/env python3
import unittest
from unittest import mock

import launcher


class LauncherTests(unittest.TestCase):
    def test_terminal_argv_shape(self):
        argv = launcher.terminal_argv("/tmp/hello.sh")
        self.assertEqual(argv[:3], ["gnome-terminal", "--", "bash"])
        self.assertEqual(argv[3], "-c")
        self.assertIn("/tmp/hello.sh", argv[4])
        self.assertIn("Press Enter to close", argv[4])

    def test_terminal_argv_quotes_spaces(self):
        argv = launcher.terminal_argv("/tmp/my script.sh")
        self.assertIn("'/tmp/my script.sh'", argv[4])

    def test_run_command_terminal_uses_argv(self):
        with mock.patch("launcher.subprocess.Popen") as popen:
            launcher.run_command(None, "/tmp/x.sh", terminal=True)
            popen.assert_called_once()
            self.assertEqual(
                popen.call_args[0][0],
                launcher.terminal_argv("/tmp/x.sh"),
            )

    def test_run_command_non_terminal(self):
        with mock.patch("launcher.subprocess.Popen") as popen:
            launcher.run_command(None, "/tmp/x.sh", terminal=False)
            popen.assert_called_once_with(["/tmp/x.sh"])


if __name__ == "__main__":
    unittest.main()
