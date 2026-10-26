# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_value_labels_common import (
    IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
    _izom_propui_free_finish_value_label_collection_mutation,
    _izom_propui_free_focus_value_label_editor,
    _izom_propui_free_selected_value_label_indexes_direct,
    _izom_propui_free_selected_value_label_uids,
    _izom_propui_free_value_label_collection_name,
    _izom_propui_free_value_label_operator_entry,
    _izom_propui_free_value_label_target_info,
    _izom_propui_free_value_label_target_mode_label,
    izom_propui_free_context_params,
    izom_propui_free_log_recovered,
)
from .confirmations import izom_propui_free_confirm_or_execute
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator



class IZOM_PROPUI_FREE_OT_remove_value_label(Operator):
    bl_idname = "wm.izom_propui_free_remove_value_label"
    bl_label = "Remove Dynamic Label"
    bl_description = "Remove the selected dynamic-label row"
    bl_options = {'UNDO', 'INTERNAL'}

    target_mode: EnumProperty(
        name="Target Mode",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
        default='SELF',
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params is not None and len(getattr(params, 'izom_propui_free_entries', []) or []) > 0)

    @classmethod
    def description(cls, _context, properties):
        return f"Remove the selected row from {_izom_propui_free_value_label_target_mode_label(getattr(properties, 'target_mode', 'SELF'))}"

    def execute(self, context):
        entry = _izom_propui_free_value_label_operator_entry(context, getattr(self, 'entry_uid', ''))
        info = _izom_propui_free_value_label_target_info(entry, context, self.target_mode)
        if not info or len(info['collection']) == 0:
            return {'CANCELLED'}
        collection = info['collection']
        active_owner = info.get('active_owner', entry)
        collection_name = _izom_propui_free_value_label_collection_name(self.target_mode)
        _izom_propui_free_focus_value_label_editor(info, self.target_mode)
        selected_uids = _izom_propui_free_selected_value_label_uids(active_owner, collection_name)
        indexes = _izom_propui_free_selected_value_label_indexes_direct(active_owner, collection_name, collection, selected_uids)
        if not indexes:
            return {'CANCELLED'}
        next_index = min(indexes[0], len(collection) - len(indexes) - 1)
        for index in reversed(indexes):
            collection.remove(index)
        next_uid = ''
        if len(collection) > 0:
            next_index = max(0, min(next_index, len(collection) - 1))
            next_uid = str(getattr(collection[next_index], 'uid', '') or '').strip()
        _izom_propui_free_finish_value_label_collection_mutation(
            active_owner,
            collection_name,
            collection,
            next_uid,
            next_index if next_uid else 0,
            params=info.get('params'),
        )
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_clear_value_labels(Operator):
    bl_idname = "wm.izom_propui_free_clear_value_labels"
    bl_label = "Clear Dynamic Labels"
    bl_description = "Clear every row from the selected Dynamic Labels list"
    bl_options = {'UNDO', 'INTERNAL'}

    target_mode: EnumProperty(
        name="Target Mode",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
        default='SELF',
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params is not None and len(getattr(params, 'izom_propui_free_entries', []) or []) > 0)

    @classmethod
    def description(cls, _context, properties):
        return f"Clear every row from {_izom_propui_free_value_label_target_mode_label(getattr(properties, 'target_mode', 'SELF'))}"

    def invoke(self, context, event):
        return izom_propui_free_confirm_or_execute(
            self, context, event, prop_name='izom_propui_free_confirmation_clear_dynamic_labels'
        )

    def execute(self, context):
        entry = _izom_propui_free_value_label_operator_entry(context, getattr(self, 'entry_uid', ''))
        info = _izom_propui_free_value_label_target_info(entry, context, self.target_mode)
        if not info or len(info['collection']) == 0:
            return {'CANCELLED'}
        collection = info['collection']
        active_owner = info.get('active_owner', entry)
        collection_name = _izom_propui_free_value_label_collection_name(self.target_mode)
        _izom_propui_free_focus_value_label_editor(info, self.target_mode)
        try:
            collection.clear()
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            while len(collection) > 0:
                collection.remove(len(collection) - 1)
        _izom_propui_free_finish_value_label_collection_mutation(
            active_owner,
            collection_name,
            collection,
            '',
            0,
            selected_uids=[],
            anchor_uid='',
            params=info.get('params'),
        )
        return {'FINISHED'}

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
