# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.constants_icons import (
    izom_propui_free_blender_icon_default_number,
    izom_propui_free_blender_icon_items,
)
from ..core.text import (
    izom_propui_free_display_icon,
    izom_propui_free_display_icon_pair,
)
from .operators_entries_shared_common import (
    _izom_propui_free_icon_property_group,
    _izom_propui_free_target_icon_owner,
)
from .operators_layout_base import _izom_propui_free_entry_params



class IZOM_PROPUI_FREE_OT_pick_icon(Operator):
    bl_idname = "wm.izom_propui_free_pick_icon"
    bl_label = "Pick Blender Icon"
    bl_description = "Search all Blender icons and assign the selected icon"
    bl_options = {'UNDO', 'INTERNAL'}
    bl_property = "icon_value"

    target_scope: EnumProperty(
        name="Target Scope",
        items=[
            ('ENTRY', 'Entry', ''),
            ('PARAMS', 'PropUI Settings', ''),
    ('VALUE_LABEL', 'Dynamic Label Row', ''),
        ],
        default='ENTRY',
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(name="Entry UID", default="", options={'HIDDEN'})
    value_label_uid: StringProperty(name="Dynamic Label UID", default="", options={'HIDDEN'})
    target_mode: StringProperty(name="Target Mode", default="SELF", options={'HIDDEN'})
    prop_name: StringProperty(name="Property Name", default="", options={'HIDDEN'})
    initial_icon_value: StringProperty(name="Initial Icon", default="NONE", options={'HIDDEN'})
    icon_value: EnumProperty(
        name="Icon",
        description="Search and choose a Blender icon",
        items=izom_propui_free_blender_icon_items,
        default=izom_propui_free_blender_icon_default_number('NONE'),
    )

    @classmethod
    def poll(cls, context):
        return _izom_propui_free_entry_params(context) is not None

    def invoke(self, context, _event):
        try:
            self.icon_value = izom_propui_free_display_icon(getattr(self, 'initial_icon_value', 'NONE'), 'NONE')
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        prop_name = str(getattr(self, 'prop_name', '') or '').strip()
        if not prop_name:
            return {'CANCELLED'}
        owner = _izom_propui_free_target_icon_owner(
            params,
            context,
            getattr(self, 'target_scope', 'ENTRY'),
            getattr(self, 'entry_uid', ''),
            getattr(self, 'value_label_uid', ''),
            getattr(self, 'target_mode', 'SELF'),
        )
        if owner is None or not hasattr(owner, prop_name):
            return {'CANCELLED'}
        selected_icon = izom_propui_free_display_icon(getattr(self, 'icon_value', 'NONE'), 'NONE')
        icon_group = _izom_propui_free_icon_property_group(prop_name)
        if icon_group and all(hasattr(owner, attr_name) for attr_name in icon_group):
            before_prop, after_prop = icon_group
            current_before, current_after = izom_propui_free_display_icon_pair(
                getattr(owner, before_prop, 'NONE'),
                getattr(owner, after_prop, 'NONE'),
            )
            if prop_name == before_prop:
                current_before = selected_icon
            else:
                current_after = selected_icon
            setattr(owner, before_prop, current_before)
            setattr(owner, after_prop, current_after)
        else:
            setattr(owner, prop_name, selected_icon)
        if getattr(context, 'area', None) is not None and hasattr(context.area, 'tag_redraw'):
            context.area.tag_redraw()
        return {'FINISHED'}


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
