#!/usr/bin/env python3
"""Gtk.Application entry for single-instance Command Center summon."""

import sys

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gio, GLib, Gtk


APPLICATION_ID = "org.commandcenter.App"


class CommandCenterApp(Gtk.Application):
    """One primary window; later activates present + focus search."""

    def __init__(self):
        super().__init__(
            application_id=APPLICATION_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self._window = None

    def do_activate(self):
        if self._window is None:
            # Late import avoids circular load with menu bootstrapping CSS.
            from menu import CommandCenter, load_css

            load_css()
            self._window = CommandCenter(application=self)
            self.add_window(self._window)
            self._window.connect("destroy", self._on_window_destroy)
            self._window.show_all()
            self._window.render_commands()
        self._window.present_and_focus_search()

    def _on_window_destroy(self, *_args):
        self._window = None


def main(argv=None):
    GLib.set_prgname("command-center")
    app = CommandCenterApp()
    return app.run(argv if argv is not None else sys.argv)


if __name__ == "__main__":
    sys.exit(main())
