#!/usr/bin/env python3

import gi
import os
import subprocess

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GLib

from authoring import AuthoringForm
from favorites import load_favorites, save_favorites
from metadata import read_metadata
from scriptio import (
    delete_script,
    read_script,
    slug_filename,
    unique_path,
    write_script,
)
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
            780
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

        self.commands = []
        self.favorites = load_favorites()
        self.edit_favorites = False
        self.edit_commands = False
        self.pending_favorites = None
        self.pending_confirm = None
        self.confirm_popover = None
        self._initial_search_focus = False
        self._header = header

        self.edit_fav_button = Gtk.Button()
        self.edit_fav_button.set_tooltip_text("Edit favorites")
        self.edit_fav_button.get_style_context().add_class("cc-header-button")
        self.edit_fav_button.get_style_context().add_class("cc-edit-favorites")
        self._sync_edit_fav_button()
        self.edit_fav_button.connect("clicked", self.on_edit_favorites_clicked)
        header.pack_start(self.edit_fav_button)

        self.edit_cmd_button = Gtk.Button(label="Edit")
        self.edit_cmd_button.set_tooltip_text("Edit commands")
        self.edit_cmd_button.get_style_context().add_class("cc-header-button")
        self.edit_cmd_button.get_style_context().add_class("cc-edit-commands")
        self.edit_cmd_button.connect("clicked", self.on_edit_commands_clicked)
        header.pack_start(self.edit_cmd_button)

        self.add_cmd_button = Gtk.Button(label="+")
        self.add_cmd_button.set_tooltip_text("New command")
        self.add_cmd_button.get_style_context().add_class("cc-header-button")
        self.add_cmd_button.get_style_context().add_class("cc-header-plus")
        self.add_cmd_button.connect("clicked", self.on_add_command_clicked)
        header.pack_end(self.add_cmd_button)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search commands…")
        self.search_entry.get_style_context().add_class("cc-search-entry")
        self.search_entry.set_hexpand(True)
        self.search_entry.set_size_request(220, -1)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_search_key_press)
        header.pack_end(self.search_entry)

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

        self.favorites_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.favorites_box.get_style_context().add_class("cc-favorites-section")
        self.favorites_box.set_no_show_all(True)
        self.favorites_box.hide()
        self.favorites_label = Gtk.Label(label="Favorites", xalign=0)
        self.favorites_label.get_style_context().add_class("cc-favorites-label")
        self.favorites_grid = Gtk.Grid()
        self.favorites_grid.set_row_spacing(12)
        self.favorites_grid.set_column_spacing(12)
        self.favorites_grid.set_halign(Gtk.Align.CENTER)
        self.favorites_box.pack_start(self.favorites_label, False, False, 0)
        self.favorites_box.pack_start(self.favorites_grid, False, False, 0)

        self.edit_banner = Gtk.Label(
            label="Editing commands — tap ✎ to edit or 🗑 to delete. Launch paused."
        )
        self.edit_banner.set_line_wrap(True)
        self.edit_banner.get_style_context().add_class("cc-edit-banner")
        self.edit_banner.set_no_show_all(True)
        self.edit_banner.hide()

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        self.content.pack_start(self.chip_box, False, False, 0)
        self.content.pack_start(self.edit_banner, False, False, 0)
        self.content.pack_start(self.favorites_box, False, False, 0)
        self.content.pack_start(self.grid, True, True, 0)

        self.authoring = AuthoringForm()
        self.authoring.on_save = self.on_authoring_save
        self.authoring.on_cancel = self.on_authoring_cancel

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.stack.add_named(self.content, "launcher")
        self.stack.add_named(self.authoring, "authoring")

        self.root_overlay = Gtk.Overlay()
        self.root_overlay.add(self.stack)
        self.add(self.root_overlay)
        self._delete_overlay = None

        self.load_commands()

        self.connect("key-press-event", self.on_window_key_press)
        # Focus search once on first map only — not after every grid rebuild.
        self.connect("map-event", self.on_map_event)

    def _sync_edit_fav_button(self):
        if self.edit_favorites:
            self.edit_fav_button.set_label("Apply")
            self.edit_fav_button.set_image(Gtk.Image())
            self.edit_fav_button.set_always_show_image(False)
            self.edit_fav_button.set_tooltip_text("Apply favorite changes")
            self.edit_fav_button.get_style_context().add_class("active")
        else:
            theme = Gtk.IconTheme.get_default()
            icon_name = "starred-symbolic"
            if not theme.has_icon(icon_name):
                for fallback in ("emblem-favorite-symbolic", "starred"):
                    if theme.has_icon(fallback):
                        icon_name = fallback
                        break
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            self.edit_fav_button.set_label("")
            self.edit_fav_button.set_image(icon)
            self.edit_fav_button.set_always_show_image(True)
            self.edit_fav_button.set_tooltip_text("Edit favorites")
            self.edit_fav_button.get_style_context().remove_class("active")

    def on_edit_favorites_clicked(self, *_args):
        if self.stack.get_visible_child_name() == "authoring":
            return
        if not self.edit_favorites:
            self._exit_edit_commands(render=False)
            self.edit_favorites = True
            self.pending_favorites = list(self.favorites)
            self._sync_edit_fav_button()
            self.render_commands()
            return
        # Apply pending → disk, exit edit
        known = self._known_basenames()
        names = [n for n in (self.pending_favorites or []) if n in known]
        save_favorites(names)
        self.favorites = load_favorites()
        self.pending_favorites = None
        self.edit_favorites = False
        self._sync_edit_fav_button()
        self.render_commands()

    def _exit_edit_favorites(self, apply=False):
        if not self.edit_favorites:
            return
        if apply:
            known = self._known_basenames()
            names = [n for n in (self.pending_favorites or []) if n in known]
            save_favorites(names)
            self.favorites = load_favorites()
        self.pending_favorites = None
        self.edit_favorites = False
        self._sync_edit_fav_button()

    def _sync_edit_cmd_button(self):
        ctx = self.edit_cmd_button.get_style_context()
        if self.edit_commands:
            ctx.add_class("active")
            self.edit_cmd_button.set_tooltip_text("Done editing commands")
            self.edit_banner.show()
        else:
            ctx.remove_class("active")
            self.edit_cmd_button.set_tooltip_text("Edit commands")
            self.edit_banner.hide()

    def _exit_edit_commands(self, render=True):
        if not self.edit_commands:
            return
        self.edit_commands = False
        self._sync_edit_cmd_button()
        if render:
            self.render_commands()

    def on_edit_commands_clicked(self, *_args):
        if self.stack.get_visible_child_name() == "authoring":
            return
        if self.edit_commands:
            self._exit_edit_commands()
            return
        self._exit_edit_favorites(apply=False)
        self.edit_commands = True
        self._sync_edit_cmd_button()
        self.render_commands()

    def on_add_command_clicked(self, *_args):
        self.show_authoring(None)

    def _set_launcher_chrome_visible(self, visible):
        for widget in (
            self.search_entry,
            self.edit_cmd_button,
            self.edit_fav_button,
            self.add_cmd_button,
        ):
            if visible:
                widget.show()
            else:
                widget.hide()

    def show_authoring(self, path):
        self.hide_confirm()
        self.hide_delete_overlay()
        if path is None:
            self.authoring.load(path=None, meta={
                "name": "",
                "desc": "",
                "category": "General",
                "icon": "🔧",
                "terminal": False,
                "confirm": False,
            }, body="")
        else:
            data = read_script(path)
            self.authoring.load(path=path, meta=data["meta"], body=data["body"])
        # Let Gtk.Stack own child visibility — do not hide() stack children.
        self._set_launcher_chrome_visible(False)
        self.authoring.set_hexpand(True)
        self.authoring.set_vexpand(True)
        self.authoring.show_all()
        self.stack.set_visible_child_name("authoring")

    def show_launcher(self):
        self.hide_delete_overlay()
        # Child must be visible BEFORE set_visible_child_name, or Stack ignores it.
        self.content.set_no_show_all(False)
        self.content.show_all()
        self.stack.set_visible_child_name("launcher")
        self._set_launcher_chrome_visible(True)
        self._sync_edit_cmd_button()
        self.render_commands()

    def on_authoring_save(self, form):
        err = form.validate()
        if err:
            form.show_error(err)
            return
        meta, body = form.get_values()
        path = form.get_path()
        try:
            if path is None:
                filename = slug_filename(meta["name"])
                path = unique_path(SCRIPTS_DIR, filename)
            write_script(path, meta, body)
        except OSError as exc:
            form.show_error(str(exc))
            return
        self.show_launcher()
        self.load_commands()

    def on_authoring_cancel(self, form):
        if form.is_dirty():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text="Discard changes?",
            )
            dialog.format_secondary_text(
                "You have unsaved edits. Discard them and return?"
            )
            dialog.add_button("Keep editing", Gtk.ResponseType.CANCEL)
            dialog.add_button("Discard", Gtk.ResponseType.ACCEPT)
            response = dialog.run()
            dialog.destroy()
            if response != Gtk.ResponseType.ACCEPT:
                return
        self.show_launcher()

    def on_edit_script(self, path):
        self.show_authoring(path)

    def hide_delete_overlay(self):
        if self._delete_overlay is None:
            return
        overlay = self._delete_overlay
        self._delete_overlay = None
        self.root_overlay.remove(overlay)

    def on_delete_script(self, path, meta):
        self.hide_delete_overlay()
        name = meta.get("name") or os.path.basename(path)
        base = os.path.basename(path)

        dim = Gtk.EventBox()
        dim.get_style_context().add_class("cc-delete-overlay")
        dim.set_hexpand(True)
        dim.set_vexpand(True)

        center = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        center.set_halign(Gtk.Align.CENTER)
        center.set_valign(Gtk.Align.CENTER)

        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        panel.get_style_context().add_class("cc-delete-dialog")
        title = Gtk.Label(label="Delete command?", xalign=0)
        title.get_style_context().add_class("cc-delete-dialog-title")
        body = Gtk.Label(
            label=(
                f"Remove {name}? This deletes the script file {base} "
                "and cannot be undone from the app."
            ),
            xalign=0,
        )
        body.set_line_wrap(True)
        body.set_max_width_chars(36)
        body.get_style_context().add_class("cc-delete-dialog-body")
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        actions.set_halign(Gtk.Align.END)
        cancel = Gtk.Button(label="Cancel")
        cancel.get_style_context().add_class("cc-authoring-cancel")
        delete_btn = Gtk.Button(label="Delete")
        delete_btn.get_style_context().add_class("cc-delete-confirm")

        def on_cancel(*_a):
            self.hide_delete_overlay()

        def on_delete(*_a):
            self.hide_delete_overlay()
            try:
                delete_script(path)
            except OSError as exc:
                err = Gtk.MessageDialog(
                    transient_for=self,
                    modal=True,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Could not delete script",
                )
                err.format_secondary_text(str(exc))
                err.run()
                err.destroy()
                return
            names = [n for n in load_favorites() if n != base]
            save_favorites(names)
            self.favorites = names
            self.load_commands()

        cancel.connect("clicked", on_cancel)
        delete_btn.connect("clicked", on_delete)
        actions.pack_start(cancel, False, False, 0)
        actions.pack_start(delete_btn, False, False, 0)
        panel.pack_start(title, False, False, 0)
        panel.pack_start(body, False, False, 0)
        panel.pack_start(actions, False, False, 0)
        center.pack_start(panel, False, False, 0)
        dim.add(center)
        dim.show_all()
        self.root_overlay.add_overlay(dim)
        self._delete_overlay = dim

    def _known_basenames(self):
        return {os.path.basename(path) for path, _meta in self.commands}

    def _clear_container(self, container):
        for child in container.get_children():
            container.remove(child)

    def _attach_cards(self, container, items, columns=3):
        self._clear_container(container)
        row = col = 0
        for path, meta in items:
            basename = os.path.basename(path)
            if self.edit_favorites and self.pending_favorites is not None:
                favorited = basename in self.pending_favorites
            else:
                favorited = basename in self.favorites
            card = CommandCard(
                meta,
                favorited=favorited,
                edit_mode=self.edit_favorites,
                commands_edit=self.edit_commands,
                on_edit=(
                    (lambda p=path: self.on_edit_script(p))
                    if self.edit_commands
                    else None
                ),
                on_delete=(
                    (lambda p=path, m=meta: self.on_delete_script(p, m))
                    if self.edit_commands
                    else None
                ),
            )
            card.set_can_focus(False)
            card._cc_script_path = path
            if self.edit_favorites:
                card.connect("clicked", self.on_favorite_card_clicked, path)
            elif self.edit_commands:
                # Launch paused — ignore card body clicks.
                pass
            else:
                card.connect("clicked", self.on_command_clicked, path, meta)
            container.attach(card, col, row, 1, 1)
            col += 1
            if col == columns:
                col = 0
                row += 1

    def on_favorite_card_clicked(self, _button, path):
        basename = os.path.basename(path)
        pending = list(self.pending_favorites or [])
        if basename in pending:
            pending = [n for n in pending if n != basename]
        else:
            pending.append(basename)
        self.pending_favorites = pending
        self.render_commands()

    def _build_confirm_popover(self, relative_to):
        pop = Gtk.Popover.new(relative_to)
        pop.set_position(Gtk.PositionType.TOP)
        pop.set_modal(True)
        pop.get_style_context().add_class("cc-confirm-popover-shell")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.get_style_context().add_class("cc-confirm-popover")

        label = Gtk.Label(xalign=0)
        label.get_style_context().add_class("cc-confirm-label")
        label.set_line_wrap(True)
        self.confirm_label = label

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel = Gtk.Button(label="Cancel")
        cancel.get_style_context().add_class("cc-confirm-cancel")
        cancel.connect("clicked", self.on_confirm_cancel)
        run = Gtk.Button(label="Run")
        run.get_style_context().add_class("cc-confirm-run")
        run.connect("clicked", self.on_confirm_run)
        btn_row.pack_start(cancel, False, False, 0)
        btn_row.pack_start(run, False, False, 0)

        box.pack_start(label, False, False, 0)
        box.pack_start(btn_row, False, False, 0)
        box.show_all()
        pop.add(box)
        pop.connect("closed", self.on_confirm_popover_closed)
        return pop

    def show_confirm(self, path, meta, relative_to=None):
        self.hide_confirm()
        if relative_to is None:
            return
        self.pending_confirm = (path, meta)
        self.confirm_popover = self._build_confirm_popover(relative_to)
        name = meta.get("name") or "command"
        self.confirm_label.set_text(f"Run {name}?")
        self.confirm_popover.popup()

    def hide_confirm(self):
        self.pending_confirm = None
        pop = self.confirm_popover
        self.confirm_popover = None
        if pop is not None:
            pop.popdown()
            pop.destroy()

    def on_confirm_popover_closed(self, pop):
        if self.confirm_popover is pop:
            self.pending_confirm = None
            self.confirm_popover = None

    def on_confirm_cancel(self, *_args):
        self.hide_confirm()

    def on_confirm_run(self, *_args):
        if not self.pending_confirm:
            return
        path, meta = self.pending_confirm
        self.hide_confirm()
        run_command(None, path, meta.get("terminal", False))

    def on_command_clicked(self, button, path, meta):
        if self.pending_confirm is not None:
            return
        if meta.get("confirm"):
            self.show_confirm(path, meta, relative_to=button)
            return
        run_command(None, path, meta.get("terminal", False))

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
        if self.pending_confirm is not None:
            self.hide_confirm()
        # Preserve caret: rebuilding cards must not steal focus or select-all.
        had_search_focus = (
            self.search_entry is not None
            and self.search_entry.has_focus()
        )
        cursor = None
        if had_search_focus:
            cursor = self.search_entry.get_position()

        query = ""
        if hasattr(self, "search_entry") and self.search_entry is not None:
            query = self.search_entry.get_text()

        by_base = {os.path.basename(p): (p, m) for p, m in self.commands}
        fav_items = []
        for name in self.favorites:
            if name in by_base:
                fav_items.append(by_base[name])

        if not fav_items:
            # no_show_all so startup window.show_all() cannot revive an empty strip
            self.favorites_box.set_no_show_all(True)
            self.favorites_box.hide()
        else:
            self.favorites_box.set_no_show_all(False)
            self._attach_cards(self.favorites_grid, fav_items)
            self.favorites_box.show_all()

        main_items = []
        for path, meta in self.commands:
            if matches_filters(meta, query, self.selected_category):
                main_items.append((path, meta))
        self._attach_cards(self.grid, main_items)
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
        self.favorites = load_favorites()
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
            if os.environ.get("CC_QA_CONFIRM") == "1":
                # After layout/show_all settle so the target card exists.
                GLib.timeout_add(400, self._qa_show_first_confirm)
            qa = os.environ.get("CC_QA_AUTHORING", "").strip().lower()
            if qa in ("edit", "new", "delete", "form", "form-popover"):
                GLib.timeout_add(450, self._qa_authoring, qa)
            shot = os.environ.get("CC_QA_SHOT", "").strip()
            if shot:
                if qa == "delete":
                    delay = 1200
                elif qa == "form-popover":
                    delay = 1100
                else:
                    delay = 900
                GLib.timeout_add(delay, self._qa_shot_and_quit, shot)
        return False

    def _qa_open_icon_popover(self):
        if hasattr(self, "authoring") and self.authoring is not None:
            self.authoring._on_change_icon()
        return False

    def _qa_shot_and_quit(self, path):
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            self.present()
            gdk_win = self.get_window()
            if gdk_win is None:
                return False
            xid = gdk_win.get_xid()
            # External grab — Gdk.pixbuf_get_from_window can abort via cairo.
            subprocess.run(
                ["import", "-window", hex(xid), path],
                check=False,
                timeout=8,
            )
        finally:
            Gtk.main_quit()
        return False

    def _qa_authoring(self, mode):
        if mode == "edit":
            self.edit_commands = True
            self._sync_edit_cmd_button()
            self.render_commands()
        elif mode == "new":
            self.show_authoring(None)
        elif mode == "form":
            if self.commands:
                path, _meta = self.commands[0]
                self.show_authoring(path)
            else:
                self.show_authoring(None)
        elif mode == "form-popover":
            if self.commands:
                path, _meta = self.commands[0]
                self.show_authoring(path)
            else:
                self.show_authoring(None)
            GLib.timeout_add(200, self._qa_open_icon_popover)
        elif mode == "delete":
            self.edit_commands = True
            self._sync_edit_cmd_button()
            self.render_commands()
            if self.commands:
                path, meta = self.commands[0]
                GLib.timeout_add(300, lambda: self.on_delete_script(path, meta) or False)
        return False

    def _qa_show_first_confirm(self):
        for path, meta in self.commands:
            if not meta.get("confirm"):
                continue
            for container in (self.grid, self.favorites_grid):
                for child in container.get_children():
                    if getattr(child, "_cc_script_path", None) == path:
                        self.show_confirm(path, meta, relative_to=child)
                        return False
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
        if self.stack.get_visible_child_name() == "authoring":
            if event.keyval == Gdk.KEY_Escape:
                if self.authoring.popover_visible():
                    self.authoring._icon_popover.popdown()
                    return True
                self.on_authoring_cancel(self.authoring)
                return True
            return False
        if (
            self.pending_confirm is not None
            and event.keyval == Gdk.KEY_Escape
        ):
            self.hide_confirm()
            return True
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
# show_all can fight Favorites visibility — re-apply strip show/hide.
window.render_commands()

Gtk.main()