#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from textutil import truncate_description


class CommandCard(Gtk.Button):

    def __init__(self, meta):

        super().__init__()

        self.set_size_request(
            180,
            130
        )

        self.get_style_context().add_class(
            "command-card"
        )

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

        icon = Gtk.Image()

        theme = Gtk.IconTheme.get_default()

        if theme.has_icon(meta["icon"]):

            icon.set_from_icon_name(
                meta["icon"],
                Gtk.IconSize.DIALOG
            )

        else:

            icon.set_from_icon_name(
                "application-x-executable",
                Gtk.IconSize.DIALOG
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

        self.add(
            box
        )
