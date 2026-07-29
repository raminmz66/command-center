#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk


ICON_CATALOG = [
    "🖥", "💾", "🔒", "🌐", "⚙", "🗂",
    "🛡", "📡", "🧹", "⏱", "📦", "🔧",
    "🗒", "🚀", "🔑", "☁", "🔊", "🔋",
    "🏠", "⭐", "🔥", "💡", "🗑", "📁",
    "🔄", "🛠", "📊", "🖧", "🧩", "🎮",
    "📝", "🛰", "🔐", "💻", "🧭", "⚡",
]

_DEFAULT_ICON = "🔧"

class AuthoringForm(Gtk.Box):
    """Sectioned Soft GNOME create/edit form with icon popover."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("cc-authoring-page")

        self._path = None
        self._baseline = None
        self.on_save = None
        self.on_cancel = None
        self._icon_popover = None

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("cc-authoring-header")
        header.set_margin_bottom(12)

        self.back_btn = Gtk.Button(label="← Back")
        self.back_btn.get_style_context().add_class("cc-authoring-back")
        self.back_btn.connect("clicked", self._emit_cancel)

        self.title_label = Gtk.Label(label="New command")
        self.title_label.set_hexpand(True)
        self.title_label.get_style_context().add_class("cc-authoring-title")

        self.save_btn = Gtk.Button(label="Save")
        self.save_btn.get_style_context().add_class("cc-authoring-save")
        self.save_btn.connect("clicked", self._emit_save)

        header.pack_start(self.back_btn, False, False, 0)
        header.pack_start(self.title_label, True, True, 0)
        header.pack_end(self.save_btn, False, False, 0)

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        body.set_hexpand(True)
        body.set_vexpand(True)
        body.set_margin_start(12)
        body.set_margin_end(12)
        body.set_margin_bottom(12)

        # —— Identity ——
        identity = self._section("Identity")
        id_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.name_entry = self._labeled_entry(id_row, "Name", expand=True)
        self.category_entry = self._labeled_entry(id_row, "Category", expand=True)
        identity.pack_start(id_row, False, False, 0)
        self.desc_entry = self._labeled_entry(identity, "Description")
        body.pack_start(identity, False, False, 0)

        # —— Appearance ——
        appearance = self._section("Appearance")
        icon_field = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        icon_lbl = Gtk.Label(label="ICON", xalign=0)
        icon_lbl.get_style_context().add_class("cc-authoring-label")
        icon_field.pack_start(icon_lbl, False, False, 0)

        chip_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        chip_row.set_valign(Gtk.Align.CENTER)

        self.icon_chip = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.icon_chip.get_style_context().add_class("cc-authoring-chip")
        self.chip_emoji = Gtk.Label(label=_DEFAULT_ICON)
        self.chip_emoji.get_style_context().add_class("cc-authoring-chip-emoji")
        chip_text = Gtk.Label(label="Selected")
        chip_text.get_style_context().add_class("cc-authoring-chip-text")
        self.icon_chip.pack_start(self.chip_emoji, False, False, 0)
        self.icon_chip.pack_start(chip_text, False, False, 0)
        chip_row.pack_start(self.icon_chip, False, False, 0)

        self.change_btn = Gtk.Button(label="Change\u2026")
        self.change_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.change_btn.get_style_context().add_class("cc-authoring-change")
        self.change_btn.connect("clicked", self._on_change_icon)
        chip_row.pack_start(self.change_btn, False, False, 0)

        icon_field.pack_start(chip_row, False, False, 0)
        appearance.pack_start(icon_field, False, False, 0)

        self._icon_buttons = {}
        pop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        pop_box.get_style_context().add_class("cc-authoring-icon-popover")
        grid = Gtk.Grid()
        grid.set_column_spacing(4)
        grid.set_row_spacing(4)
        grid.set_margin_start(8)
        grid.set_margin_end(8)
        grid.set_margin_top(8)
        grid.set_margin_bottom(8)
        for idx, glyph in enumerate(ICON_CATALOG):
            cell = Gtk.EventBox()
            cell.set_visible_window(True)
            cell.set_can_focus(False)
            cell.set_halign(Gtk.Align.CENTER)
            cell.set_size_request(34, 34)
            cell.get_style_context().add_class("cc-authoring-icon-cell")
            label = Gtk.Label(label=glyph)
            label.set_halign(Gtk.Align.CENTER)
            label.set_valign(Gtk.Align.CENTER)
            label.get_style_context().add_class("cc-authoring-icon-glyph")
            cell.add(label)
            cell.connect("button-press-event", self._on_icon_cell_pressed, glyph)
            self._icon_buttons[glyph] = cell
            grid.attach(cell, idx % 6, idx // 6, 1, 1)
        pop_box.pack_start(grid, False, False, 0)
        pop_box.show_all()

        self._icon_popover = Gtk.Popover.new(self.change_btn)
        self._icon_popover.set_position(Gtk.PositionType.BOTTOM)
        self._icon_popover.set_modal(True)
        self._icon_popover.add(pop_box)

        body.pack_start(appearance, False, False, 0)

        # —— Behavior ——
        behavior = self._section("Behavior")
        switches = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        self.terminal_switch = Gtk.Switch()
        self.confirm_switch = Gtk.Switch()
        switches.pack_start(self._switch_row("Terminal", self.terminal_switch), False, False, 0)
        switches.pack_start(
            self._switch_row("Confirm before run", self.confirm_switch),
            False,
            False,
            0,
        )
        behavior.pack_start(switches, False, False, 0)
        body.pack_start(behavior, False, False, 0)

        # —— Script ——
        script_sec = self._section("Script")
        script_sec.set_vexpand(True)
        self.script_view = Gtk.TextView()
        self.script_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.script_view.set_monospace(True)
        self.script_view.get_style_context().add_class("cc-authoring-script")
        script_frame = Gtk.ScrolledWindow()
        script_frame.set_min_content_height(140)
        script_frame.set_vexpand(True)
        script_frame.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        script_frame.add(self.script_view)
        script_frame.get_style_context().add_class("cc-authoring-script-frame")
        script_sec.pack_start(script_frame, True, True, 0)
        body.pack_start(script_sec, True, True, 0)

        self.error_label = Gtk.Label(xalign=0)
        self.error_label.get_style_context().add_class("cc-authoring-error")
        self.error_label.set_no_show_all(True)
        self.error_label.hide()
        body.pack_start(self.error_label, False, False, 0)

        self.pack_start(header, False, False, 0)
        self.pack_start(body, True, True, 0)

        self.connect("key-press-event", self._on_key_press)

        self._icon_name = _DEFAULT_ICON
        self._select_icon(self._icon_name)
    def _section(self, title):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.get_style_context().add_class("cc-authoring-section")
        # Uppercase in text — GTK CSS has no text-transform.
        lbl = Gtk.Label(label=title.upper(), xalign=0)
        lbl.get_style_context().add_class("cc-authoring-section-title")
        box.pack_start(lbl, False, False, 0)
        return box

    def _labeled_entry(self, parent, label, expand=False):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        if expand:
            box.set_hexpand(True)
        lbl = Gtk.Label(label=label.upper(), xalign=0)
        lbl.get_style_context().add_class("cc-authoring-label")
        entry = Gtk.Entry()
        entry.get_style_context().add_class("cc-authoring-entry")
        box.pack_start(lbl, False, False, 0)
        box.pack_start(entry, False, False, 0)
        parent.pack_start(box, True if expand else False, True if expand else False, 0)
        return entry

    def _switch_row(self, label, switch):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.pack_start(switch, False, False, 0)
        box.pack_start(Gtk.Label(label=label, xalign=0), False, False, 0)
        return box

    def _on_change_icon(self, *_args):
        if self._icon_popover is None:
            return
        self._icon_popover.set_relative_to(self.change_btn)
        self._icon_popover.popup()

    def _on_icon_cell_pressed(self, _widget, event, glyph):
        if event.button != 1:
            return False
        self._select_icon(glyph)
        if self._icon_popover is not None:
            self._icon_popover.popdown()
        return True

    def _select_icon(self, glyph):
        if glyph not in self._icon_buttons:
            glyph = _DEFAULT_ICON
        self._icon_name = glyph
        self.chip_emoji.set_text(glyph)
        for key, cell in self._icon_buttons.items():
            ctx = cell.get_style_context()
            if key == glyph:
                ctx.add_class("selected")
            else:
                ctx.remove_class("selected")

    def _on_key_press(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape and self._icon_popover is not None:
            if self._icon_popover.get_visible():
                self._icon_popover.popdown()
                return True
        return False

    def popover_visible(self):
        return (
            self._icon_popover is not None
            and self._icon_popover.get_visible()
        )

    def _script_text(self):
        buf = self.script_view.get_buffer()
        start, end = buf.get_start_iter(), buf.get_end_iter()
        return buf.get_text(start, end, True)

    def _set_script_text(self, text):
        self.script_view.get_buffer().set_text(text or "")

    def load(self, path=None, meta=None, body=""):
        self._path = path
        meta = meta or {}
        create = path is None
        self.title_label.set_text("New command" if create else "Edit command")
        self.name_entry.set_text(meta.get("name") or "")
        self.desc_entry.set_text(meta.get("desc") or "")
        self.category_entry.set_text(meta.get("category") or "General")
        self._select_icon(meta.get("icon") or _DEFAULT_ICON)
        self.terminal_switch.set_active(bool(meta.get("terminal")))
        self.confirm_switch.set_active(bool(meta.get("confirm")))
        self._set_script_text(body)
        self.clear_error()
        if self._icon_popover is not None:
            self._icon_popover.popdown()
        self._baseline = self.get_values()

    def get_path(self):
        return self._path

    def get_values(self):
        meta = {
            "name": self.name_entry.get_text().strip(),
            "desc": self.desc_entry.get_text().strip(),
            "category": self.category_entry.get_text().strip() or "General",
            "icon": self._icon_name,
            "terminal": self.terminal_switch.get_active(),
            "confirm": self.confirm_switch.get_active(),
        }
        return meta, self._script_text()

    def is_dirty(self):
        if self._baseline is None:
            return False
        return self.get_values() != self._baseline

    def validate(self):
        meta, body = self.get_values()
        if not meta["name"]:
            return "Name is required."
        if not body.strip():
            return "Script body is required."
        return None

    def show_error(self, message):
        self.error_label.set_text(message or "")
        if message:
            self.error_label.show()
        else:
            self.error_label.hide()

    def clear_error(self):
        self.show_error("")

    def _emit_save(self, *_args):
        if self.on_save:
            self.on_save(self)

    def _emit_cancel(self, *_args):
        if self._icon_popover is not None:
            self._icon_popover.popdown()
        if self.on_cancel:
            self.on_cancel(self)
