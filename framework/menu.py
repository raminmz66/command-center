#!/usr/bin/env python3

import gi
import os
import subprocess

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GLib

from metadata import read_metadata
from textutil import matches_query
from widgets import CommandCard
from launcher import run_command


SCRIPTS_DIR = os.path.expanduser(
    "~/CommandCenter/scripts"
)

CSS_FILE = os.path.expanduser(
    "~/CommandCenter/framework/style.css"
)


def load_css():

    provider = Gtk.CssProvider()

    if os.path.exists(CSS_FILE):

        provider.load_from_path(
            CSS_FILE
        )

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


class CommandCenter(Gtk.Window):

    def __init__(self):

        super().__init__()

        self.get_style_context().add_class(
            "command-center-window"
        )

        self.set_title(
            "Command Center"
        )

        self.set_default_size(
            640,
            540
        )

        self.set_resizable(
            False
        )

        self.set_border_width(
            18
        )


        header = Gtk.HeaderBar()

        header.set_title(
            "Command Center"
        )

        header.set_subtitle(
            "Personal command launcher"
        )

        header.set_show_close_button(
            True
        )

        self.set_titlebar(
            header
        )


        folder_button = Gtk.Button()

        folder_icon = Gtk.Image.new_from_icon_name(
            "folder-symbolic",
            Gtk.IconSize.BUTTON
        )

        folder_button.set_image(
            folder_icon
        )

        folder_button.set_tooltip_text(
            "Open scripts folder"
        )

        folder_button.get_style_context().add_class(
            "cc-header-button"
        )

        folder_button.connect(
            "clicked",
            self.open_folder
        )


        header.pack_start(
            folder_button
        )


        refresh_button = Gtk.Button()

        refresh_icon = Gtk.Image.new_from_icon_name(
            "view-refresh-symbolic",
            Gtk.IconSize.BUTTON
        )

        refresh_button.set_image(
            refresh_icon
        )

        refresh_button.set_tooltip_text(
            "Reload commands"
        )

        refresh_button.get_style_context().add_class(
            "cc-header-button"
        )

        refresh_button.connect(
            "clicked",
            self.refresh
        )


        header.pack_start(
            refresh_button
        )

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search commands…")
        self.search_entry.get_style_context().add_class("cc-search-entry")
        self.search_entry.set_hexpand(True)
        self.search_entry.set_size_request(220, -1)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_search_key_press)
        header.pack_end(self.search_entry)

        self.commands = []

        self.grid = Gtk.Grid()

        self.grid.get_style_context().add_class(
            "command-grid"
        )

        self.grid.set_row_spacing(
            12
        )

        self.grid.set_column_spacing(
            12
        )

        self.grid.set_halign(
            Gtk.Align.CENTER
        )


        self.add(
            self.grid
        )


        self.load_commands()

        self.connect("key-press-event", self.on_window_key_press)
        self.connect(
            "map-event",
            lambda *a: GLib.idle_add(self.focus_search) or False,
        )

    def clear_grid(self):

        for child in self.grid.get_children():

            self.grid.remove(
                child
            )


    def discover_commands(self):
        self.commands = []
        if not os.path.exists(SCRIPTS_DIR):
            return
        for file in sorted(os.listdir(SCRIPTS_DIR)):
            if not file.endswith(".sh"):
                continue
            path = os.path.join(SCRIPTS_DIR, file)
            meta = read_metadata(path)
            self.commands.append((path, meta))

    def render_commands(self):
        self.clear_grid()
        query = ""
        if hasattr(self, "search_entry") and self.search_entry is not None:
            query = self.search_entry.get_text()
        row = 0
        col = 0
        for path, meta in self.commands:
            if not matches_query(meta, query):
                continue
            card = CommandCard(meta)
            card.connect("clicked", run_command, path, meta["terminal"])
            self.grid.attach(card, col, row, 1, 1)
            col += 1
            if col == 3:
                col = 0
                row += 1
        self.show_all()

    def load_commands(self):
        self.discover_commands()
        self.render_commands()

    def on_search_changed(self, entry):
        self.render_commands()

    def on_search_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.search_entry.set_text("")
            return True
        return False

    def focus_search(self, *args):
        self.search_entry.grab_focus()
        return True

    def on_window_key_press(self, widget, event):
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval in (Gdk.KEY_f, Gdk.KEY_F):
            return self.focus_search()
        # Slash focuses search when not already typing in the entry
        if event.keyval == Gdk.KEY_slash and not self.search_entry.is_focus():
            return self.focus_search()
        return False

    def refresh(
        self,
        widget
    ):

        self.load_commands()


    def open_folder(
        self,
        widget
    ):

        subprocess.Popen(
            [
                "xdg-open",
                SCRIPTS_DIR
            ]
        )


load_css()


window = CommandCenter()

window.connect(
    "destroy",
    Gtk.main_quit
)


window.show_all()

Gtk.main()