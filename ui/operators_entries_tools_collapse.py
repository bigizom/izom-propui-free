# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import StringProperty
from bpy.types import Operator
from .helper_layout_entry_collapse import (
    _izom_propui_free_toggle_entry_collapsed_and_focus,
)
from .helper_selection_entries import _izom_propui_free_active_entry_uid
from .operators_layout_base import _izom_propui_free_entry_params



class IZOM_PROPUI_FREE_OT_toggle_active_entry_collapse(Operator):
    bl_idname = "wm.izom_propui_free_toggle_active_entry_collapse"
    bl_label = "Toggle Active Entry Collapse"
    bl_description = "Collapse or expand the active parent entry in the Entry List"
    bl_options = {'INTERNAL'}

    target_uid: StringProperty(name="Target Entry UID", default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        return bool(params and getattr(params, 'izom_propui_free_entries', None))

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        target_uid = str(getattr(self, 'target_uid', '') or '').strip()
        if not target_uid:
            target_uid = _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY')
        if not target_uid:
            return {'CANCELLED'}
        if not _izom_propui_free_toggle_entry_collapsed_and_focus(params, target_uid):
            return {'CANCELLED'}
        return {'FINISHED'}

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
