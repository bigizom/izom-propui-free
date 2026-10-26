# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_value_labels_common import (
    IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
    _izom_propui_free_active_value_label_index_direct,
    _izom_propui_free_finish_value_label_collection_mutation,
    _izom_propui_free_focus_value_label_editor,
    _izom_propui_free_new_uid,
    _izom_propui_free_report_operator,
    _izom_propui_free_selected_value_label_uids,
    _izom_propui_free_threshold_field_name,
    _izom_propui_free_threshold_storage_value,
    _izom_propui_free_value_label_collection_name,
    _izom_propui_free_value_label_companion_key_for_collection,
    _izom_propui_free_value_label_operator_entry,
    _izom_propui_free_value_label_target_info,
    _izom_propui_free_value_label_target_mode_label,
    _izom_propui_free_value_label_threshold_bounds,
    izom_propui_free_context_params,
    izom_propui_free_log_recovered,
)
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator
from ..core.value_access_common import izom_propui_free_is_numeric_value_kind



IZOM_PROPUI_FREE_VALUE_LABEL_SORT_MODE_ITEMS = (
    ('AT_LEAST_DESC', 'At Least: High to Low', "Sort At Least numeric rows so higher values have priority"),
    ('AT_MOST_ASC', 'At Most: Low to High', "Sort At Most numeric rows so lower values have priority"),
    ('EQUAL_ASC', 'Equals: Low to High', "Sort Equals numeric rows by value"),
    ('RANGE_NARROW', 'Range: Narrow First', "Sort In Range numeric rows so narrower ranges have priority"),
)


def _izom_propui_free_value_label_sort_match_mode(sort_mode):
    mode = str(sort_mode or 'AT_LEAST_DESC').strip().upper()
    if mode == 'AT_MOST_ASC':
        return 'LESS'
    if mode == 'EQUAL_ASC':
        return 'EQUAL'
    if mode == 'RANGE_NARROW':
        return 'RANGE'
    return 'GREATER'


def _izom_propui_free_numeric_sort_values(item, field_root, prop_type):
    primary_field = _izom_propui_free_threshold_field_name(prop_type, field_root=field_root)
    range_field = f"{field_root}_range_{'int' if str(prop_type or '').strip().upper() == 'INT' else 'float'}"
    primary_value = _izom_propui_free_threshold_storage_value(item, primary_field, prop_type)
    range_value = _izom_propui_free_threshold_storage_value(item, range_field, prop_type)
    return primary_value, range_value


def _izom_propui_free_value_label_sort_key(item, sort_mode, field_root, prop_type):
    primary_value, range_value = _izom_propui_free_numeric_sort_values(item, field_root, prop_type)
    mode = str(sort_mode or 'AT_LEAST_DESC').strip().upper()
    if mode == 'AT_LEAST_DESC':
        return (-float(primary_value),)
    if mode == 'AT_MOST_ASC':
        return (float(primary_value),)
    if mode == 'RANGE_NARROW':
        low_value = min(float(primary_value), float(range_value))
        high_value = max(float(primary_value), float(range_value))
        return (high_value - low_value, low_value, high_value)
    return (float(primary_value),)


def _izom_propui_free_value_label_sort_row_info(info, entry, active_owner, collection_name, item, sort_mode):
    wanted_match_mode = _izom_propui_free_value_label_sort_match_mode(sort_mode)
    row_match_mode = str(getattr(item, 'match_mode', 'GREATER') or 'GREATER').strip().upper() or 'GREATER'
    if row_match_mode != wanted_match_mode:
        return None

    params = info.get('params')
    source_type, _min_value, _max_value = _izom_propui_free_value_label_threshold_bounds(
        params,
        entry,
        active_owner,
        collection_name,
        'target_value_float',
        item,
    )
    source_type = str(source_type or '').strip().upper()
    if not izom_propui_free_is_numeric_value_kind(source_type):
        return None
    field_root = 'target_value'
    field_name = _izom_propui_free_threshold_field_name(source_type, field_root=field_root)
    companion_key = _izom_propui_free_value_label_companion_key_for_collection(
        collection_name,
        entry,
        active_owner,
        field_name,
        reference_entry=info.get('source_entry') or entry,
    )
    group_key = companion_key(item) if companion_key is not None else ('all',)
    return {
        'group_key': ('self', source_type, group_key),
        'sort_key': _izom_propui_free_value_label_sort_key(item, sort_mode, field_root, source_type),
    }


def _izom_propui_free_ensure_value_label_uid(item):
    uid = str(getattr(item, 'uid', '') or '').strip()
    if uid:
        return uid
    uid = _izom_propui_free_new_uid()
    try:
        item.uid = uid
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    return uid


class IZOM_PROPUI_FREE_OT_sort_value_labels(Operator):
    bl_idname = "wm.izom_propui_free_sort_value_labels"
    bl_label = "Sort Dynamic Labels"
    bl_description = "Sort matching numeric Dynamic Label rows inside each watched-value group"
    bl_options = {'UNDO', 'INTERNAL'}

    target_mode: EnumProperty(
        name="Target Mode",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
        default='SELF',
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(default="", options={'HIDDEN'})
    sort_mode: EnumProperty(
        name="Sort",
        description="Which numeric Dynamic Label rows to sort",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_SORT_MODE_ITEMS,
        default='AT_LEAST_DESC',
    )

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params is not None and len(getattr(params, 'izom_propui_free_entries', []) or []) > 0)

    @classmethod
    def description(cls, _context, properties):
        label = dict((item[0], item[1]) for item in IZOM_PROPUI_FREE_VALUE_LABEL_SORT_MODE_ITEMS).get(
            str(getattr(properties, 'sort_mode', 'AT_LEAST_DESC') or 'AT_LEAST_DESC'),
            'Numeric Rows',
        )
        return f"Sort {label} in {_izom_propui_free_value_label_target_mode_label(getattr(properties, 'target_mode', 'SELF'))}"

    def execute(self, context):
        entry = _izom_propui_free_value_label_operator_entry(context, getattr(self, 'entry_uid', ''))
        info = _izom_propui_free_value_label_target_info(entry, context, self.target_mode)
        if not info or len(info['collection']) < 2:
            return {'CANCELLED'}
        collection = info['collection']
        active_owner = info.get('active_owner', entry)
        collection_name = _izom_propui_free_value_label_collection_name(self.target_mode)
        _izom_propui_free_focus_value_label_editor(info, self.target_mode)

        current_uids = [_izom_propui_free_ensure_value_label_uid(item) for item in collection]
        groups = {}
        for index, item in enumerate(collection):
            row_info = _izom_propui_free_value_label_sort_row_info(
                info,
                entry,
                active_owner,
                collection_name,
                item,
                self.sort_mode,
            )
            if row_info is None:
                continue
            group_key = row_info['group_key']
            groups.setdefault(group_key, []).append((index, current_uids[index], row_info['sort_key']))

        sortable_groups = {
            key: rows
            for key, rows in groups.items()
            if len(rows) > 1
        }
        if not sortable_groups:
            _izom_propui_free_report_operator(
                self,
                'INFO',
                "No matching numeric Dynamic Label rows needed sorting",
            )
            return {'CANCELLED'}

        final_uids = list(current_uids)
        for rows in sortable_groups.values():
            target_indexes = [row[0] for row in rows]
            sorted_rows = sorted(rows, key=lambda row: (row[2], row[0]))
            for target_index, sorted_row in zip(target_indexes, sorted_rows):
                final_uids[target_index] = sorted_row[1]

        if final_uids == current_uids:
            _izom_propui_free_report_operator(
                self,
                'INFO',
                "Dynamic Label rows were already sorted",
            )
            return {'CANCELLED'}

        for target_index, uid in enumerate(final_uids):
            current_index = -1
            for index, item in enumerate(collection):
                if str(getattr(item, 'uid', '') or '').strip() == uid:
                    current_index = index
                    break
            if current_index < 0 or current_index == target_index:
                continue
            collection.move(current_index, target_index)

        selected_uids = _izom_propui_free_selected_value_label_uids(active_owner, collection_name)
        active_uid = str(getattr(active_owner, f"{collection_name}_active_uid", '') or '').strip()
        if not active_uid and len(collection) > 0:
            try:
                active_index = int(getattr(active_owner, f"{collection_name}_active_index", 0) or 0)
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                active_index = 0
            if 0 <= active_index < len(collection):
                active_uid = str(getattr(collection[active_index], 'uid', '') or '').strip()
        active_index = _izom_propui_free_active_value_label_index_direct(
            active_owner,
            collection_name,
            collection,
            [active_uid] if active_uid else [],
        )
        _izom_propui_free_finish_value_label_collection_mutation(
            active_owner,
            collection_name,
            collection,
            active_uid,
            active_index if active_index >= 0 else 0,
            selected_uids=selected_uids,
            anchor_uid=selected_uids[0] if selected_uids else active_uid,
            params=info.get('params'),
        )
        return {'FINISHED'}



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
