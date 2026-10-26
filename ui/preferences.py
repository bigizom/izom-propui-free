# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import BoolProperty
from bpy.types import AddonPreferences, Operator

from .common import izom_propui_free_addon_preferences_id


_IZOM_PROPUI_FREE_LICENSE_NOTICE = (
    "izom PropUI Free - A Blender UI-generation extension.",
    "Copyright (C) 2026  bigizom",
    "",
    "This program is free software: you can redistribute it and/or modify",
    "it under the terms of the GNU General Public License as published by",
    "the Free Software Foundation, either version 3 of the License, or",
    "(at your option) any later version.",
    "",
    "The full license text is in the LICENSE.txt file shipped with this",
    "extension.",
)

class IZOM_PROPUI_FREE_OT_show_license(Operator):
    bl_idname = "wm.izom_propui_free_show_license"
    bl_label = "izom PropUI Free License"
    bl_description = "Show the izom PropUI Free license notice"
    bl_options = {'INTERNAL'}

    def invoke(self, context, _event):
        return context.window_manager.invoke_props_dialog(self, width=540)

    def draw(self, _context):
        col = self.layout.column(align=True)
        for line in _IZOM_PROPUI_FREE_LICENSE_NOTICE:
            col.label(text=line)

    def execute(self, _context):
        return {'FINISHED'}


class IZOM_PROPUI_FREE_AddonPreferences(AddonPreferences):
    bl_idname = izom_propui_free_addon_preferences_id(__package__)

    show_diagnostics: BoolProperty(
        name="Show Diagnostics",
        description="Expand or collapse the izom PropUI Free diagnostics preferences",
        default=True,
        options={'HIDDEN'},
    )
    izom_propui_free_verbose_console_diagnostics: BoolProperty(
        name="Verbose Console Diagnostics",
        description="Print debug-level izom PropUI diagnostics and tracebacks to Blender's system console",
        default=False,
    )
    def draw(self, _context):
        layout = self.layout
        diagnostics_header = layout.row(align=True)
        diagnostics_expanded = bool(getattr(self, 'show_diagnostics', True))
        diagnostics_header.prop(
            self,
            "show_diagnostics",
            text="izom PropUI Diagnostics",
            icon='TRIA_DOWN' if diagnostics_expanded else 'TRIA_RIGHT',
            emboss=False,
        )
        if diagnostics_expanded:
            layout.column(align=True).prop(self, "izom_propui_free_verbose_console_diagnostics")
        layout.separator()
        layout.operator("wm.izom_propui_free_show_license", text="License Notice", icon='TEXT')


CLASSES = (
    IZOM_PROPUI_FREE_OT_show_license,
    IZOM_PROPUI_FREE_AddonPreferences,
)
