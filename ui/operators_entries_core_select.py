# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator
from .helper_selection_entries import _izom_propui_free_select_entry_uid
from .operators_layout_base import _izom_propui_free_entry_params




class IZOM_PROPUI_FREE_OT_select_entry(Operator):
    bl_idname = "wm.izom_propui_free_select_entry"
    bl_label = "Select izom PropUI Entry"
    bl_description = "Select an izom PropUI entry. Shift-click selects a range, Ctrl-click toggles selection"
    bl_options = {'INTERNAL'}

    target_uid: StringProperty(name="Target UID", options={'HIDDEN'})
    editor_context: EnumProperty(
        name="Editor Context",
        items=[
            ('HIERARCHY', 'Hierarchy', ''),
            ('LAYOUT', 'Layout', ''),
        ],
        default='HIERARCHY',
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        return bool(
            params
            and getattr(params, 'izom_propui_free_entries', None)
        )

    def invoke(self, context, event):
        params = _izom_propui_free_entry_params(context)
        if not params:
            return {'CANCELLED'}
        _izom_propui_free_select_entry_uid(
            params,
            self.target_uid,
            editor_context=self.editor_context,
            extend=bool(getattr(event, 'shift', False)),
            toggle=bool(getattr(event, 'ctrl', False)),
        )
        if getattr(context, 'area', None) is not None and hasattr(context.area, 'tag_redraw'):
            context.area.tag_redraw()
        return {'FINISHED'}

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if not params:
            return {'CANCELLED'}
        _izom_propui_free_select_entry_uid(params, self.target_uid, editor_context=self.editor_context)
        if getattr(context, 'area', None) is not None and hasattr(context.area, 'tag_redraw'):
            context.area.tag_redraw()
        return {'FINISHED'}

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
