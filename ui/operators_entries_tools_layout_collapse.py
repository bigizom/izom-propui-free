# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from .helper_layout_rows import (
    _izom_propui_free_toggle_layout_row_group_collapsed,
)
from .helper_selection_common import (
    _izom_propui_free_set_last_editor_context,
    _izom_propui_free_uid_list_from_json,
)
from .helper_selection_context import _izom_propui_free_set_last_clicked_list_context
from .helper_layout_view import (
    _izom_propui_free_active_layout_view_item,
    _izom_propui_free_layout_view_item_by_uid,
)
from .operators_entries_shared_common import _izom_propui_free_active_layout_row_header_item
from .operators_layout_base import _izom_propui_free_entry_params
from .operators_layout_view import _izom_propui_free_rebuild_layout_view_items



class IZOM_PROPUI_FREE_OT_toggle_layout_row_group_collapse(Operator):
    bl_idname = "wm.izom_propui_free_toggle_layout_row_group_collapse"
    bl_label = "Toggle Row Group Collapse"
    bl_description = "Collapse or expand the selected Row Group without changing the generated result"
    bl_options = {'INTERNAL'}

    target_view_uid: StringProperty(name="Target View UID", default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        return bool(params and getattr(params, 'izom_propui_free_layout_view_items', None))

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        target_view_uid = str(getattr(self, 'target_view_uid', '') or '').strip()
        target_view_item = _izom_propui_free_layout_view_item_by_uid(params, target_view_uid)
        if target_view_item is None or str(getattr(target_view_item, 'kind', '') or '').strip() != 'ROW_HEADER':
            return {'CANCELLED'}
        member_uids = _izom_propui_free_uid_list_from_json(getattr(target_view_item, 'row_member_uids_json', '[]'))
        became_collapsed = _izom_propui_free_toggle_layout_row_group_collapsed(params, target_view_uid)
        preferred_active_uid = str(getattr(params, 'izom_propui_free_layout_view_active_uid', '') or '').strip()
        active_view_item = _izom_propui_free_active_layout_view_item(params)
        if became_collapsed and active_view_item is not None:
            active_uid = str(getattr(active_view_item, 'uid', '') or '').strip()
            active_layout_uid = str(getattr(active_view_item, 'layout_uid', '') or '').strip()
            if active_uid == target_view_uid or (active_layout_uid and active_layout_uid in member_uids):
                preferred_active_uid = target_view_uid
        _izom_propui_free_rebuild_layout_view_items(params, preferred_active_uid=preferred_active_uid or target_view_uid)
        _izom_propui_free_set_last_editor_context(params, 'LAYOUT')
        _izom_propui_free_set_last_clicked_list_context(params, 'GL_LIST')
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_toggle_active_layout_row_group_collapse(Operator):
    bl_idname = "wm.izom_propui_free_toggle_active_layout_row_group_collapse"
    bl_label = "Toggle Active Row Group Collapse"
    bl_description = "Collapse or expand the active Generated Layout row group"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = _izom_propui_free_entry_params(context)
        return bool(params and _izom_propui_free_active_layout_row_header_item(params) is not None)

    def execute(self, context):
        params = _izom_propui_free_entry_params(context)
        if params is None:
            return {'CANCELLED'}
        header_item = _izom_propui_free_active_layout_row_header_item(params)
        target_view_uid = str(getattr(header_item, 'uid', '') or '').strip() if header_item is not None else ''
        if not target_view_uid:
            return {'CANCELLED'}
        return bpy.ops.wm.izom_propui_free_toggle_layout_row_group_collapse(target_view_uid=target_view_uid)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
