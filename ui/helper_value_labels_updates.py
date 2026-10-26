# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_value_labels_dependencies import (
    _izom_propui_free_clamp_visibility_match_float,
    _izom_propui_free_clamp_visibility_match_int,
    _izom_propui_free_clamp_visibility_range_max_float,
    _izom_propui_free_clamp_visibility_range_max_int,
    _izom_propui_free_entry_component_rule_info,
    _izom_propui_free_entry_numeric_bounds,
    _izom_propui_free_pointer_guard_key,
    izom_propui_free_entry_value_kind,
    izom_propui_free_is_numeric_value_kind,
)
from ..core.constants_display import IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH
from ..core.context import izom_propui_free_context_params
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.snapshot_tree import _izom_propui_free_clamp_visibility_inheritance_depth
from ..core.value_access_common import izom_propui_free_is_exact_match_value_kind
from ..core.value_labels_common import _izom_propui_free_is_numeric_type
from .helper_cache_updates_common import (
    _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD,
    _IZOM_PROPUI_FREE_VISIBILITY_DEPTH_UPDATE_GUARD,
)
from .helper_cache_updates_entry_params import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_context_bulk_entry_updates_suspended,
    _izom_propui_free_entry_runtime_update_callbacks_suspended,
    _izom_propui_free_find_params_for_entry,
)
from .helper_cache_updates_invalidation import _izom_propui_free_schedule_runtime_entry_cache_invalidate
from .helper_field_clamp_common import _izom_propui_free_snap_editor_float_value_for_params
from .helper_field_clamp_numeric import (
    _izom_propui_free_clamp_entry_default_float,
    _izom_propui_free_clamp_entry_default_int,
    _izom_propui_free_general_float_field_updated,
)
from .helper_selection_collections import _izom_propui_free_bump_collection_revision
from .helper_selection_common import _izom_propui_free_data_value
from .helper_validation import (
    _izom_propui_free_entry_visibility_inheritance_info,
)
from .helper_value_labels_base import (
    _izom_propui_free_inheritance_tree_state,
    _izom_propui_free_value_label_guard_key,
)
from .helper_value_labels_source import (
    _izom_propui_free_entry_effective_value_label_kind,
    _izom_propui_free_find_value_label_owner,
    _izom_propui_free_value_label_reference_entry,
)
from .helper_value_labels_thresholds import (
    _izom_propui_free_canonical_threshold_field_name,
    _izom_propui_free_set_threshold_value,
    _izom_propui_free_threshold_storage_value,
    _izom_propui_free_value_label_snapshot_previous_threshold,
    _izom_propui_free_value_label_threshold_bounds,
)



def _izom_propui_free_entry_value_update_suspended(context):
    return (
        _izom_propui_free_entry_runtime_update_callbacks_suspended()
        or _izom_propui_free_context_bulk_entry_updates_suspended(context)
    )


def _izom_propui_free_value_label_threshold_updated(item, context, *, field_name):
    guard_key = _izom_propui_free_value_label_guard_key(item, field_name)
    if guard_key in _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD:
        return
    if _izom_propui_free_context_bulk_entry_updates_suspended(context):
        return
    context_params = izom_propui_free_context_params(context)
    if _izom_propui_free_bulk_entry_updates_suspended(context_params):
        return

    notify_params = None
    notify_owner = None
    notify_collection_name = ''
    should_notify = False
    _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD.add(guard_key)
    try:
        params, entry, collection_owner, collection_name, index = _izom_propui_free_find_value_label_owner(item, context)
        notify_params = params
        if _izom_propui_free_bulk_entry_updates_suspended(params):
            return
        if entry is None or collection_name != 'value_labels':
            return

        notify_owner = collection_owner if collection_owner is not None else entry
        notify_collection_name = collection_name
        target_reference_entry = _izom_propui_free_value_label_reference_entry(params, entry) or entry
        target_prop_type = izom_propui_free_entry_value_kind(
            target_reference_entry,
            str(getattr(target_reference_entry, 'prop_type', '') or ''),
        )
        target_is_numeric = _izom_propui_free_is_numeric_type(target_prop_type)
        field_prop_type, min_value, max_value = _izom_propui_free_value_label_threshold_bounds(
            params,
            entry,
            collection_owner,
            collection_name,
            field_name,
            item,
        )
        if not _izom_propui_free_is_numeric_type(field_prop_type):
            return
        target_component_info = (
            _izom_propui_free_entry_component_rule_info(entry, item, reference_entry=target_reference_entry)
            if field_name.startswith('target_value_')
            else {}
        )
        target_uses_numeric_component = bool(target_component_info.get('use_component', False)) and _izom_propui_free_is_numeric_type(field_prop_type)
        if field_name.startswith('target_value_') and not (target_is_numeric or target_uses_numeric_component):
            return

        canonical_field_name = _izom_propui_free_canonical_threshold_field_name(field_name, field_prop_type)
        if canonical_field_name != field_name:
            canonical_value = _izom_propui_free_threshold_storage_value(item, canonical_field_name, field_prop_type)
            _izom_propui_free_set_threshold_value(item, canonical_field_name, field_prop_type, canonical_value)
            should_notify = True
            return

        default_value = 0 if field_prop_type == 'INT' else 0.0
        current_value = _izom_propui_free_threshold_storage_value(item, canonical_field_name, field_prop_type)
        try:
            if field_prop_type == 'INT':
                normalized_value = int(current_value)
            else:
                snap_base = min_value if min_value is not None else 0.0
                normalized_value = _izom_propui_free_snap_editor_float_value_for_params(params, current_value, base=snap_base)
        except (TypeError, ValueError):
            normalized_value = default_value
        previous_value = _izom_propui_free_value_label_snapshot_previous_threshold(
            params,
            entry,
            collection_owner,
            collection_name,
            index,
            canonical_field_name,
            normalized_value,
        )
        _izom_propui_free_set_threshold_value(item, canonical_field_name, field_prop_type, normalized_value)
        normalized_value = _izom_propui_free_threshold_storage_value(item, canonical_field_name, field_prop_type)
        should_notify = True

    finally:
        _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD.discard(guard_key)
        if should_notify:
            if notify_owner is not None and notify_collection_name == 'value_labels':
                _izom_propui_free_bump_collection_revision(notify_owner, notify_collection_name)
            _izom_propui_free_schedule_runtime_entry_cache_invalidate(notify_params)

def _izom_propui_free_value_float_threshold_updated(item, context):
    _izom_propui_free_value_label_threshold_updated(item, context, field_name='value_float')


def _izom_propui_free_value_int_threshold_updated(item, context):
    _izom_propui_free_value_label_threshold_updated(item, context, field_name='value_int')


_izom_propui_free_value_float_updated = _izom_propui_free_value_float_threshold_updated
_izom_propui_free_conditional_value_float_updated = _izom_propui_free_value_float_threshold_updated
_izom_propui_free_value_int_updated = _izom_propui_free_value_int_threshold_updated
_izom_propui_free_conditional_value_int_updated = _izom_propui_free_value_int_threshold_updated

def _izom_propui_free_target_value_float_updated(item, context):
    _izom_propui_free_value_label_threshold_updated(item, context, field_name='target_value_float')

def _izom_propui_free_target_value_int_updated(item, context):
    _izom_propui_free_value_label_threshold_updated(item, context, field_name='target_value_int')

def _izom_propui_free_default_float_updated(entry, context):
    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clamp_entry_default_float(entry, params)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_default_int_updated(entry, context):
    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clamp_entry_default_int(entry)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_step_float_updated(entry, context):
    _izom_propui_free_general_float_field_updated(entry, context, field_name='step_float')

def _izom_propui_free_number_child_visibility_updated(entry, context):
    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clamp_visibility_match_float(entry, context)
    _izom_propui_free_clamp_visibility_match_int(entry, context)
    _izom_propui_free_clamp_visibility_range_max_float(entry, context)
    _izom_propui_free_clamp_visibility_range_max_int(entry, context)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_visibility_match_float_updated(entry, context):
    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clamp_visibility_match_float(entry, context)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_visibility_match_int_updated(entry, context):
    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clamp_visibility_match_int(entry, context)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_visibility_range_max_float_updated(entry, context):
    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clamp_visibility_range_max_float(entry, context)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_visibility_range_max_int_updated(entry, context):
    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clamp_visibility_range_max_int(entry, context)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_visibility_inheritance_depth_updated(entry, context):
    guard_key = (_izom_propui_free_pointer_guard_key(entry), 'visibility_inheritance_depth')
    if guard_key in _IZOM_PROPUI_FREE_VISIBILITY_DEPTH_UPDATE_GUARD:
        return

    if _izom_propui_free_entry_value_update_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    current_depth = _izom_propui_free_data_value(entry, 'visibility_inheritance_depth', 1)
    if params is not None:
        state = _izom_propui_free_inheritance_tree_state(params)
        clamped_depth = _izom_propui_free_entry_visibility_inheritance_info(params, entry, state=state).get('selected_depth', 1)
    else:
        parent_uid = str(_izom_propui_free_data_value(entry, 'parent_uid', '') or '').strip()
        max_depth = IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH if parent_uid else 1
        clamped_depth = _izom_propui_free_clamp_visibility_inheritance_depth(current_depth, max_depth)

    try:
        stored_depth = int(_izom_propui_free_data_value(entry, 'visibility_inheritance_depth', 1) or 1)
    except (TypeError, ValueError):
        stored_depth = 1
    if stored_depth == clamped_depth:
        _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)
        return

    _IZOM_PROPUI_FREE_VISIBILITY_DEPTH_UPDATE_GUARD.add(guard_key)
    try:
        entry.visibility_inheritance_depth = clamped_depth
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    finally:
        _IZOM_PROPUI_FREE_VISIBILITY_DEPTH_UPDATE_GUARD.discard(guard_key)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)

def _izom_propui_free_value_label_target_info(entry, context, target_mode='SELF'):
    if not entry:
        return None

    mode = str(target_mode or 'SELF')
    if mode != 'SELF':
        return None

    params = _izom_propui_free_find_params_for_entry(entry, context)
    reference_entry = _izom_propui_free_value_label_reference_entry(params, entry)
    if reference_entry is None:
        return None
    component_info = _izom_propui_free_entry_component_rule_info(entry, reference_entry=reference_entry)
    value_kind = component_info.get('value_kind', izom_propui_free_entry_value_kind(entry, getattr(entry, 'prop_type', 'FLOAT')))
    effective_value_kind = value_kind
    if not (
        izom_propui_free_is_numeric_value_kind(effective_value_kind)
        or izom_propui_free_is_exact_match_value_kind(effective_value_kind)
    ):
        return None
    min_value, max_value = _izom_propui_free_entry_numeric_bounds(reference_entry, effective_value_kind)
    return {
        'collection': entry.value_labels,
        'active_attr': 'value_labels_active_index',
        'active_owner': entry,
        'params': params,
        'source_type': effective_value_kind,
        'source_value_kind': value_kind,
        'source_entry': reference_entry,
        'min_value': min_value,
        'max_value': max_value,
        'target_mode': 'SELF',
    }


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
