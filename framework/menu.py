#!/usr/bin/env python3

import gi
import os
import subprocess

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GLib

from metadata import read_metadata
from textutil import matches_filters, ordered_categories, normalize_category
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
        self._initial_search_focus = False

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

        self.selected_category = "All"
        self.chip_buttons = {}

        # Horizontal chip row (not FlowBox — START-aligned FlowBox collapses to one column).
        self.chip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.chip_box.set_halign(Gtk.Align.START)
        self.chip_box.set_valign(Gtk.Align.START)
        self.chip_box.get_style_context().add_class("cc-category-bar")

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        self.content.pack_start(self.chip_box, False, False, 0)
        self.content.pack_start(self.grid, True, True, 0)
        self.add(self.content)

        self.load_commands()

        self.connect("key-press-event", self.on_window_key_press)
        # Focus search once on first map only — not after every grid rebuild.
        self.connect("map-event", self.on_map_event)

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
        # Preserve caret: rebuilding cards must not steal focus or select-all.
        had_search_focus = (
            self.search_entry is not None
            and self.search_entry.has_focus()
        )
        cursor = None
        if had_search_focus:
            cursor = self.search_entry.get_position()

        self.clear_grid()
        query = ""
        if hasattr(self, "search_entry") and self.search_entry is not None:
            query = self.search_entry.get_text()
        row = 0
        col = 0
        for path, meta in self.commands:
            if not matches_filters(meta, query, self.selected_category):
                continue
            card = CommandCard(meta)
            card.set_can_focus(False)
            card.connect("clicked", run_command, path, meta["terminal"])
            self.grid.attach(card, col, row, 1, 1)
            col += 1
            if col == 3:
                col = 0
                row += 1
        # Only show the grid — window show_all() remaps widgets and steals focus.
        self.grid.show_all()

        if had_search_focus:
            self._restore_search_focus(cursor)

    def rebuild_category_chips(self):
        for child in self.chip_box.get_children():
            self.chip_box.remove(child)
        self.chip_buttons = {}

        cats = []
        for _path, meta in self.commands:
            cats.append(normalize_category(meta.get("category")))
        labels = ["All"] + ordered_categories(cats)

        if (
            self.selected_category != "All"
            and self.selected_category.casefold()
            not in {c.casefold() for c in labels[1:]}
        ):
            self.selected_category = "All"

        for label in labels:
            button = Gtk.ToggleButton(label=label)
            button.get_style_context().add_class("cc-category-chip")
            button.set_can_focus(False)
            active = label.casefold() == self.selected_category.casefold()
            button.set_active(active)
            if active:
                button.get_style_context().add_class("active")
            button.connect("toggled", self.on_category_toggled, label)
            self.chip_box.pack_start(button, False, False, 0)
            self.chip_buttons[label] = button

        self.chip_box.show_all()

    def on_category_toggled(self, button, label):
        if not button.get_active():
            # Prevent fully clearing selection — re-assert if user clicks active chip off
            if label.casefold() == self.selected_category.casefold():
                button.handler_block_by_func(self.on_category_toggled)
                button.set_active(True)
                button.handler_unblock_by_func(self.on_category_toggled)
            return
        self.selected_category = label
        for name, other in self.chip_buttons.items():
            is_sel = name.casefold() == label.casefold()
            if other is not button:
                other.handler_block_by_func(self.on_category_toggled)
                other.set_active(False)
                other.handler_unblock_by_func(self.on_category_toggled)
            ctx = other.get_style_context()
            if is_sel:
                ctx.add_class("active")
            else:
                ctx.remove_class("active")
        self.render_commands()

    def load_commands(self):
        self.discover_commands()
        self.rebuild_category_chips()
        self.render_commands()

    def on_search_changed(self, entry):
        self.render_commands()

    def on_search_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.search_entry.set_text("")
            return True
        return False

    def on_map_event(self, *args):
        if not self._initial_search_focus:
            self._initial_search_focus = True
            GLib.idle_add(self.focus_search)
        return False

    def _restore_search_focus(self, cursor=None):
        entry = self.search_entry
        if hasattr(entry, "grab_focus_without_selecting"):
            entry.grab_focus_without_selecting()
        else:
            entry.grab_focus()
        if cursor is not None:
            entry.set_position(cursor)
        return False

    def focus_search(self, *args):
        self._restore_search_focus()
        return False

    def on_window_key_press(self, widget, event):
        # Don't intercept keys while typing in the search field.
        if self.search_entry.has_focus():
            return False
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval in (Gdk.KEY_f, Gdk.KEY_F):
            self.focus_search()
            return True
        if event.keyval == Gdk.KEY_slash:
            self.focus_search()
            return True
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