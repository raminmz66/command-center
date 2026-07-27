#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from textutil import truncate_description, normalize_icon_color


class CommandCard(Gtk.Button):

    def __init__(
        self,
        meta,
        favorited=False,
        edit_mode=False,
        commands_edit=False,
        on_edit=None,
        on_delete=None,
    ):

        super().__init__()

        self.set_size_request(
            180,
            130
        )

        self.get_style_context().add_class(
            "command-card"
        )

        overlay = Gtk.Overlay()

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        box.set_halign(
            Gtk.Align.CENTER
        )

        box.set_valign(
            Gtk.Align.CENTER
        )

        if edit_mode and not commands_edit:
            star = Gtk.Label(label="★" if favorited else "☆")
            star.get_style_context().add_class("cc-favorite-star")
            if favorited:
                star.get_style_context().add_class("favorited")
            star.set_halign(Gtk.Align.END)
            star.set_valign(Gtk.Align.START)
            box.pack_start(star, False, False, 0)

        icon = Gtk.Image()

        theme = Gtk.IconTheme.get_default()

        icon_name = meta.get("icon") or "application-x-executable"

        if not theme.has_icon(icon_name):
            symbolic = (
                icon_name
                if icon_name.endswith("-symbolic")
                else f"{icon_name}-symbolic"
            )
            if theme.has_icon(symbolic):
                icon_name = symbolic
            else:
                icon_name = "application-x-executable"

        icon.set_from_icon_name(
            icon_name,
            Gtk.IconSize.DIALOG
        )

        icon.get_style_context().add_class(
            "command-icon"
        )

        color_key = normalize_icon_color(
            meta.get("color")
        )

        if color_key:
            icon.get_style_context().add_class(
                f"command-icon-{color_key}"
            )

        title = Gtk.Label(
            label=meta["name"]
        )

        title.set_markup(
            f"<b>{meta['name']}</b>"
        )

        title.get_style_context().add_class(
            "command-title"
        )

        desc_text = truncate_description(
            meta.get("desc", "")
        )

        description = Gtk.Label(
            label=desc_text
        )

        description.set_line_wrap(
            True
        )

        description.set_justify(
            Gtk.Justification.CENTER
        )

        description.set_max_width_chars(
            22
        )

        description.get_style_context().add_class(
            "command-desc"
        )

        box.pack_start(
            icon,
            False,
            False,
            0
        )

        box.pack_start(
            title,
            False,
            False,
            0
        )

        if desc_text:

            box.pack_start(
                description,
                False,
                False,
                0
            )

        overlay.add(box)

        if commands_edit:
            actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            actions.set_halign(Gtk.Align.END)
            actions.set_valign(Gtk.Align.START)
            actions.set_margin_top(4)
            actions.set_margin_end(4)
            actions.get_style_context().add_class("cc-card-actions")

            edit_btn = Gtk.Button()
            edit_btn.set_relief(Gtk.ReliefStyle.NONE)
            edit_btn.set_tooltip_text("Edit")
            edit_btn.get_style_context().add_class("cc-card-edit")
            edit_icon = Gtk.Image.new_from_icon_name(
                "document-edit-symbolic",
                Gtk.IconSize.BUTTON,
            )
            if not Gtk.IconTheme.get_default().has_icon("document-edit-symbolic"):
                edit_icon = Gtk.Image.new_from_icon_name(
                    "gtk-edit",
                    Gtk.IconSize.BUTTON,
                )
            edit_btn.set_image(edit_icon)
            if on_edit:
                edit_btn.connect("clicked", lambda *_: on_edit())

            del_btn = Gtk.Button()
            del_btn.set_relief(Gtk.ReliefStyle.NONE)
            del_btn.set_tooltip_text("Delete")
            del_btn.get_style_context().add_class("cc-card-delete")
            del_icon = Gtk.Image.new_from_icon_name(
                "user-trash-symbolic",
                Gtk.IconSize.BUTTON,
            )
            del_btn.set_image(del_icon)
            if on_delete:
                del_btn.connect("clicked", lambda *_: on_delete())

            actions.pack_start(edit_btn, False, False, 0)
            actions.pack_start(del_btn, False, False, 0)
            overlay.add_overlay(actions)

        self.add(
            overlay
        )
