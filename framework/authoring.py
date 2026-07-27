#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from textutil import normalize_icon_color


CURATED_ICONS = [
    "system-monitor-app-symbolic",
    "document-save-symbolic",
    "security-high-symbolic",
    "network-vpn-symbolic",
    "preferences-system-symbolic",
    "folder-symbolic",
    "channel-secure-symbolic",
    "network-wireless-symbolic",
    "user-trash-symbolic",
    "alarm-symbolic",
    "package-x-generic-symbolic",
    "applications-utilities-symbolic",
]

COLOR_KEYS = [
    (None, "None"),
    ("r", "Red"),
    ("g", "Green"),
    ("b", "Blue"),
    ("o", "Orange"),
    ("p", "Purple"),
    ("y", "Yellow"),
]


class AuthoringForm(Gtk.Box):
    """Full-window Soft GNOME create/edit form."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.get_style_context().add_class("cc-authoring-page")

        self._path = None
        self._baseline = None
        self.on_save = None
        self.on_cancel = None

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("cc-authoring-header")
        header.set_margin_bottom(10)

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

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)

        shell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        shell.get_style_context().add_class("cc-authoring-shell")
        shell.set_margin_start(4)
        shell.set_margin_end(4)
        shell.set_margin_bottom(8)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.name_entry = self._labeled_entry(row, "Name", expand=True)
        self.category_entry = self._labeled_entry(row, "Category", expand=True)
        shell.pack_start(row, False, False, 0)

        self.desc_entry = self._labeled_entry(shell, "Description")

        icon_block = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        icon_lbl = Gtk.Label(label="ICON", xalign=0)
        icon_lbl.get_style_context().add_class("cc-authoring-label")
        icon_block.pack_start(icon_lbl, False, False, 0)

        icon_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.icon_preview = Gtk.Image.new_from_icon_name(
            "application-x-executable",
            Gtk.IconSize.DIALOG,
        )
        self.icon_preview.get_style_context().add_class("cc-authoring-icon-preview")
        preview_frame = Gtk.Frame()
        preview_frame.get_style_context().add_class("cc-authoring-icon-preview-frame")
        preview_frame.add(self.icon_preview)
        icon_row.pack_start(preview_frame, False, False, 0)

        grid_wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.icon_grid = Gtk.FlowBox()
        self.icon_grid.set_min_children_per_line(6)
        self.icon_grid.set_max_children_per_line(6)
        self.icon_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.icon_grid.set_homogeneous(True)
        self.icon_grid.set_column_spacing(4)
        self.icon_grid.set_row_spacing(4)
        self._icon_buttons = {}
        theme = Gtk.IconTheme.get_default()
        for name in CURATED_ICONS:
            use = name if theme.has_icon(name) else "application-x-executable"
            btn = Gtk.Button()
            btn.set_relief(Gtk.ReliefStyle.NONE)
            img = Gtk.Image.new_from_icon_name(use, Gtk.IconSize.BUTTON)
            btn.set_image(img)
            btn.set_tooltip_text(name)
            btn.get_style_context().add_class("cc-authoring-icon-cell")
            btn.connect("clicked", self._on_icon_picked, name)
            self._icon_buttons[name] = btn
            self.icon_grid.add(btn)
        grid_wrap.pack_start(self.icon_grid, False, False, 0)

        self.custom_icon_entry = Gtk.Entry()
        self.custom_icon_entry.set_placeholder_text("Custom icon name…")
        self.custom_icon_entry.get_style_context().add_class("cc-authoring-custom-icon")
        self.custom_icon_entry.connect("changed", self._on_custom_icon)
        grid_wrap.pack_start(self.custom_icon_entry, False, False, 0)

        icon_row.pack_start(grid_wrap, True, True, 0)
        icon_block.pack_start(icon_row, False, False, 0)
        shell.pack_start(icon_block, False, False, 0)

        color_block = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        color_lbl = Gtk.Label(label="COLOR", xalign=0)
        color_lbl.get_style_context().add_class("cc-authoring-label")
        color_block.pack_start(color_lbl, False, False, 0)
        self.color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self._color_buttons = {}
        self._selected_color = None
        for key, tip in COLOR_KEYS:
            btn = Gtk.Button()
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.set_tooltip_text(tip)
            btn.set_size_request(28, 28)
            cls = "cc-color-swatch"
            btn.get_style_context().add_class(cls)
            if key is None:
                btn.get_style_context().add_class("cc-color-none")
                btn.set_label("∅")
            else:
                btn.get_style_context().add_class(f"cc-color-{key}")
            btn.connect("clicked", self._on_color_picked, key)
            self._color_buttons[key] = btn
            self.color_box.pack_start(btn, False, False, 0)
        color_block.pack_start(self.color_box, False, False, 0)
        shell.pack_start(color_block, False, False, 0)

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
        shell.pack_start(switches, False, False, 0)

        script_lbl = Gtk.Label(label="SCRIPT", xalign=0)
        script_lbl.get_style_context().add_class("cc-authoring-label")
        shell.pack_start(script_lbl, False, False, 0)
        self.script_view = Gtk.TextView()
        self.script_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.script_view.set_monospace(True)
        self.script_view.get_style_context().add_class("cc-authoring-script")
        script_frame = Gtk.ScrolledWindow()
        script_frame.set_min_content_height(96)
        script_frame.set_vexpand(True)
        script_frame.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        script_frame.add(self.script_view)
        script_frame.get_style_context().add_class("cc-authoring-script-frame")
        shell.pack_start(script_frame, True, True, 0)

        self.error_label = Gtk.Label(xalign=0)
        self.error_label.get_style_context().add_class("cc-authoring-error")
        self.error_label.set_no_show_all(True)
        self.error_label.hide()
        shell.pack_start(self.error_label, False, False, 0)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.set_halign(Gtk.Align.END)
        cancel = Gtk.Button(label="Cancel")
        cancel.get_style_context().add_class("cc-authoring-cancel")
        cancel.connect("clicked", self._emit_cancel)
        save2 = Gtk.Button(label="Save")
        save2.get_style_context().add_class("cc-authoring-save")
        save2.connect("clicked", self._emit_save)
        footer.pack_start(cancel, False, False, 0)
        footer.pack_start(save2, False, False, 0)
        shell.pack_start(footer, False, False, 0)

        scroll.add(shell)
        self.pack_start(header, False, False, 0)
        self.pack_start(scroll, True, True, 0)

        self._icon_name = CURATED_ICONS[0]
        self._select_icon(self._icon_name)
        self._select_color(None)

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

    def _on_icon_picked(self, _btn, name):
        self.custom_icon_entry.set_text("")
        self._select_icon(name)

    def _on_custom_icon(self, entry):
        text = entry.get_text().strip()
        if text:
            self._select_icon(text, from_custom=True)

    def _select_icon(self, name, from_custom=False):
        self._icon_name = name
        theme = Gtk.IconTheme.get_default()
        use = name if theme.has_icon(name) else "application-x-executable"
        self.icon_preview.set_from_icon_name(use, Gtk.IconSize.DIALOG)
        for key, btn in self._icon_buttons.items():
            ctx = btn.get_style_context()
            if key == name and not from_custom:
                ctx.add_class("selected")
            else:
                ctx.remove_class("selected")

    def _on_color_picked(self, _btn, key):
        self._select_color(key)

    def _select_color(self, key):
        self._selected_color = key
        for k, btn in self._color_buttons.items():
            ctx = btn.get_style_context()
            if k == key:
                ctx.add_class("selected")
            else:
                ctx.remove_class("selected")
        # refresh preview tint via CSS classes on preview
        ctx = self.icon_preview.get_style_context()
        for c in list(ctx.list_classes()):
            if c.startswith("command-icon-"):
                ctx.remove_class(c)
        nk = normalize_icon_color(key)
        if nk:
            ctx.add_class("command-icon")
            ctx.add_class(f"command-icon-{nk}")

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
        icon = meta.get("icon") or CURATED_ICONS[0]
        if icon in self._icon_buttons:
            self.custom_icon_entry.set_text("")
            self._select_icon(icon)
        else:
            self.custom_icon_entry.set_text(icon)
            self._select_icon(icon, from_custom=True)
        color = normalize_icon_color(meta.get("color"))
        self._select_color(color)
        self.terminal_switch.set_active(bool(meta.get("terminal")))
        self.confirm_switch.set_active(bool(meta.get("confirm")))
        self._set_script_text(body)
        self.clear_error()
        self._baseline = self.get_values()

    def get_path(self):
        return self._path

    def get_values(self):
        meta = {
            "name": self.name_entry.get_text().strip(),
            "desc": self.desc_entry.get_text().strip(),
            "category": self.category_entry.get_text().strip() or "General",
            "icon": self._icon_name,
            "color": self._selected_color,
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
        if self.on_cancel:
            self.on_cancel(self)
