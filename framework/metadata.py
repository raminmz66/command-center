#!/usr/bin/env python3

import os


def read_metadata(path):

    meta = {
        "name": None,
        "icon": "application-x-executable",
        "desc": "",
        "category": "General",
        "terminal": False,
        "confirm": False
    }


    try:

        with open(path, "r") as file:

            for line in file:

                if line.startswith("# NAME="):
                    meta["name"] = (
                        line.split("=", 1)[1]
                        .strip()
                    )

                elif line.startswith("# ICON="):
                    meta["icon"] = (
                        line.split("=", 1)[1]
                        .strip()
                    )

                elif line.startswith("# DESC="):
                    meta["desc"] = (
                        line.split("=", 1)[1]
                        .strip()
                    )

                elif line.startswith("# CATEGORY="):
                    meta["category"] = (
                        line.split("=", 1)[1]
                        .strip()
                    )

                elif line.startswith("# TERMINAL="):
                    meta["terminal"] = (
                        line.split("=", 1)[1]
                        .strip()
                        .lower()
                        == "true"
                    )

                elif line.startswith("# CONFIRM="):
                    meta["confirm"] = (
                        line.split("=", 1)[1]
                        .strip()
                        .lower()
                        == "true"
                    )


    except Exception:

        pass


    if not meta["name"]:

        meta["name"] = (
            os.path.basename(path)
            .replace(".sh", "")
            .replace("-", " ")
            .title()
        )


    return meta
