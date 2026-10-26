# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "izom PropUI Free",
    "author": "bigizom",
    "version": (1, 1, 6),
    "blender": (5, 0, 0),
    "description": (
        "Free UI-generation tool for creating Blender custom-property "
        "controls and exposing them in a generated 3D View sidebar panel."
    ),
    "doc_url": "https://propui.bigizom.com/",
    "category": "3D View",
}


def register():
    from .registration import register as _register

    _register()


def unregister():
    from .registration import unregister as _unregister

    _unregister()
