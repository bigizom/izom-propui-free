# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_value_labels_common import (
    IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
    _izom_propui_free_active_value_label_index_direct,
    _izom_propui_free_finish_value_label_collection_mutation,
    _izom_propui_free_focus_value_label_editor,
    _izom_propui_free_selected_value_label_indexes_direct,
    _izom_propui_free_selected_value_label_uids,
    _izom_propui_free_value_label_collection_name,
    _izom_propui_free_value_label_operator_entry,
    _izom_propui_free_value_label_target_info,
    _izom_propui_free_value_label_target_mode_label,
    izom_propui_free_context_params,
)
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator



class IZOM_PROPUI_FREE_OT_move_value_label(Operator):
    bl_idname = "wm.izom_propui_free_move_value_label"
    bl_label = "Move Dynamic Label"
    bl_description = "Move the selected dynamic-label row up or down"
    bl_options = {'UNDO', 'INTERNAL'}

    target_mode: EnumProperty(
        name="Target Mode",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
        default='SELF',
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(default="", options={'HIDDEN'})
    direction: EnumProperty(
        name="Direction",
        description="Direction to move the selected dynamic-label row",
        items=[
            ('UP', 'Up', 'Move dynamic label up'),
            ('DOWN', 'Down', 'Move dynamic label down'),
        ],
        default='UP',
    )

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params is not None and len(getattr(params, 'izom_propui_free_entries', []) or []) > 0)

    @classmethod
    def description(cls, _context, properties):
        direction = 'up' if str(getattr(properties, 'direction', 'UP') or 'UP').strip().upper() == 'UP' else 'down'
        return f"Move the selected row {direction} in {_izom_propui_free_value_label_target_mode_label(getattr(properties, 'target_mode', 'SELF'))}"

    def execute(self, context):
        entry = _izom_propui_free_value_label_operator_entry(context, getattr(self, 'entry_uid', ''))
        info = _izom_propui_free_value_label_target_info(entry, context, self.target_mode)
        if not info or len(info['collection']) < 2:
            return {'CANCELLED'}
        collection = info['collection']
        active_owner = info.get('active_owner', entry)
        collection_name = _izom_propui_free_value_label_collection_name(self.target_mode)
        _izom_propui_free_focus_value_label_editor(info, self.target_mode)
        selected_uids = set(_izom_propui_free_selected_value_label_uids(active_owner, collection_name))
        if not selected_uids:
            return {'CANCELLED'}
        indexes = _izom_propui_free_selected_value_label_indexes_direct(active_owner, collection_name, collection, selected_uids)
        if not indexes:
            return {'CANCELLED'}
        moved = False
        if self.direction == 'UP':
            for index in indexes:
                if index <= 0:
                    continue
                previous_uid = str(getattr(collection[index - 1], 'uid', '') or '').strip()
                if previous_uid in selected_uids:
                    continue
                collection.move(index, index - 1)
                moved = True
        else:
            for index in reversed(indexes):
                if index >= len(collection) - 1:
                    continue
                next_uid = str(getattr(collection[index + 1], 'uid', '') or '').strip()
                if next_uid in selected_uids:
                    continue
                collection.move(index, index + 1)
                moved = True
        if not moved:
            return {'CANCELLED'}
        active_uid = getattr(active_owner, f"{collection_name}_active_uid", '')
        active_index = _izom_propui_free_active_value_label_index_direct(active_owner, collection_name, collection, [active_uid])
        _izom_propui_free_finish_value_label_collection_mutation(
            active_owner,
            collection_name,
            collection,
            str(active_uid or '').strip(),
            active_index if active_index >= 0 else 0,
            selected_uids=list(selected_uids),
            anchor_uid=str(active_uid or '').strip(),
            params=info.get('params'),
        )
        return {'FINISHED'}


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
