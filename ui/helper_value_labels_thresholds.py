# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_value_labels_exact import (
    _izom_propui_free_snap_editor_float_value_for_params,
    izom_propui_free_log_recovered,
)
from ..core.cache_common import _izom_propui_free_pointer_guard_key
from ..core.cache_state import (
    izom_propui_free_cached_entry_tree_bundle,
)
from ..core.value_access_common import izom_propui_free_is_numeric_value_kind
from ..core.value_access_entries import izom_propui_free_entry_value_kind
from ..core.value_labels_common import _izom_propui_free_is_numeric_type
from ..core.value_labels_thresholds import (
    _izom_propui_free_clamp_threshold_value,
    _izom_propui_free_collection_item_matches,
)
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD
from .helper_cache_updates_entry_params import _izom_propui_free_find_params_for_entry
from .helper_selection_common import (
    _izom_propui_free_data_value,
)
from .helper_value_labels_base import (
    _IZOM_PROPUI_FREE_DEPENDENT_THRESHOLD_OWNER_CACHE,
    _izom_propui_free_value_label_guard_key,
)
from .helper_value_labels_source import (
    _izom_propui_free_entry_component_rule_info,
    _izom_propui_free_entry_numeric_bounds,
    _izom_propui_free_value_label_reference_entry,
)


def _izom_propui_free_threshold_pair_fields(field_name):
    if field_name == 'value_int':
        return 'value_int', 'value_float'
    if field_name == 'value_float':
        return 'value_float', 'value_int'
    if field_name == 'target_value_int':
        return 'target_value_int', 'target_value_float'
    if field_name == 'target_value_float':
        return 'target_value_float', 'target_value_int'
    return field_name, None

def _izom_propui_free_canonical_threshold_field_name(field_name, prop_type):
    if str(field_name or '').startswith('target_value_'):
        return 'target_value_int' if prop_type == 'INT' else 'target_value_float'
    return 'value_int' if prop_type == 'INT' else 'value_float'

def _izom_propui_free_threshold_storage_value(item, field_name, prop_type):
    primary_field, _secondary_field = _izom_propui_free_threshold_pair_fields(field_name)
    default_value = 0 if prop_type == 'INT' else 0.0
    try:
        primary_value = getattr(item, primary_field, default_value)
    except AttributeError:
        primary_value = default_value

    if prop_type == 'INT':
        try:
            return int(primary_value)
        except (TypeError, ValueError):
            return 0

    try:
        return float(primary_value)
    except (TypeError, ValueError):
        return 0.0

def _izom_propui_free_set_threshold_value(item, field_name, prop_type, value):
    primary_field, secondary_field = _izom_propui_free_threshold_pair_fields(field_name)
    default_value = 0 if prop_type == 'INT' else 0.0
    try:
        current_value = getattr(item, primary_field, default_value)
    except AttributeError:
        current_value = default_value

    guarded_fields = [primary_field]
    if secondary_field:
        guarded_fields.append(secondary_field)
    added_guard_keys = []
    for guarded_field in guarded_fields:
        guard_key = _izom_propui_free_value_label_guard_key(item, guarded_field)
        if guard_key in _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD:
            continue
        _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD.add(guard_key)
        added_guard_keys.append(guard_key)

    try:
        if prop_type == 'INT':
            try:
                normalized_value = int(value)
            except (TypeError, ValueError):
                normalized_value = 0
            try:
                if int(current_value) != normalized_value:
                    setattr(item, primary_field, normalized_value)
            except (AttributeError, TypeError, ValueError):
                return
            if secondary_field:
                try:
                    secondary_current = float(getattr(item, secondary_field, 0.0))
                except (AttributeError, TypeError, ValueError):
                    secondary_current = 0.0
                try:
                    if abs(secondary_current - float(normalized_value)) > 1e-6:
                        setattr(item, secondary_field, float(normalized_value))
                except (AttributeError, TypeError, ValueError) as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
            return

        try:
            normalized_value = float(value)
        except (TypeError, ValueError):
            normalized_value = 0.0
        try:
            if abs(float(current_value) - normalized_value) > 1e-6:
                setattr(item, primary_field, normalized_value)
        except (AttributeError, TypeError, ValueError):
            return
        if secondary_field:
            try:
                secondary_current = int(getattr(item, secondary_field, 0) or 0)
            except (AttributeError, TypeError, ValueError):
                secondary_current = 0
            synced_secondary = int(round(normalized_value))
            try:
                if secondary_current != synced_secondary:
                    setattr(item, secondary_field, synced_secondary)
            except (AttributeError, TypeError, ValueError) as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
    finally:
        for guard_key in added_guard_keys:
            _IZOM_PROPUI_FREE_VALUE_LABEL_UPDATE_GUARD.discard(guard_key)

def _izom_propui_free_normalize_threshold_collection(
    collection,
    field_name,
    prop_type,
    *,
    min_value=None,
    max_value=None,
    companion_key=None,
    params=None,
    base_value=None,
):
    if not collection or not _izom_propui_free_is_numeric_type(prop_type):
        return
    if base_value is None:
        base_value = min_value if prop_type == 'FLOAT' and min_value is not None else 0.0
    for item in collection:
        raw_value = _izom_propui_free_threshold_storage_value(item, field_name, prop_type)
        if prop_type == 'FLOAT':
            raw_value = _izom_propui_free_snap_editor_float_value_for_params(params, raw_value, base=base_value)
        normalized_value = _izom_propui_free_clamp_threshold_value(
            raw_value,
            prop_type,
            min_value=min_value,
            max_value=max_value,
        )
        _izom_propui_free_set_threshold_value(item, field_name, prop_type, normalized_value)

def _izom_propui_free_value_label_threshold_bounds(params, entry, collection_owner, collection_name, field_name, item=None):
    fallback_prop_type = 'INT' if field_name.endswith('_int') else 'FLOAT'
    if field_name.startswith('target_value_'):
        reference_entry = _izom_propui_free_value_label_reference_entry(params, entry) or entry
        component_info = _izom_propui_free_entry_component_rule_info(entry, item, reference_entry=reference_entry)
        if component_info.get('use_component'):
            return str(component_info['component_meta'].get('component_kind', fallback_prop_type) or fallback_prop_type), None, None
        target_prop_type = component_info.get(
            'value_kind',
            izom_propui_free_entry_value_kind(reference_entry, str(getattr(reference_entry, 'prop_type', '') or '')),
        )
        if not izom_propui_free_is_numeric_value_kind(target_prop_type):
            return target_prop_type, None, None
        return target_prop_type, *_izom_propui_free_entry_numeric_bounds(reference_entry, target_prop_type)

    reference_entry = _izom_propui_free_value_label_reference_entry(params, entry) or entry
    source_prop_type = izom_propui_free_entry_value_kind(
        reference_entry,
        str(getattr(reference_entry, 'prop_type', '') or ''),
    )
    if not izom_propui_free_is_numeric_value_kind(source_prop_type):
        return source_prop_type, None, None
    return source_prop_type, *_izom_propui_free_entry_numeric_bounds(reference_entry, source_prop_type)

def _izom_propui_free_value_label_snapshot_previous_threshold(params, entry, collection_owner, collection_name, index, field_name, default_value):
    if params is None:
        return default_value

    entry_uid = str(getattr(entry, 'uid', '') or '')
    if not entry_uid:
        return default_value

    bundle = izom_propui_free_cached_entry_tree_bundle(params)
    snapshots = bundle.get('entry_snapshots') or []
    entry_index = (bundle.get('entry_index_by_uid', {}) or {}).get(entry_uid)
    if entry_index is None or not (0 <= int(entry_index) < len(snapshots)):
        return default_value

    entry_snapshot = snapshots[int(entry_index)]

    previous_items = list(entry_snapshot.get('value_labels', []) or []) if collection_name == 'value_labels' else []

    if 0 <= index < len(previous_items):
        return previous_items[index].get(field_name, default_value)
    return default_value

def _izom_propui_free_normalize_value_label_collection(entry, params=None):
    reference_entry = _izom_propui_free_value_label_reference_entry(params, entry) or entry
    prop_type = izom_propui_free_entry_value_kind(
        reference_entry,
        str(_izom_propui_free_data_value(reference_entry, 'prop_type', '') or ''),
    )
    if entry is None or not izom_propui_free_is_numeric_value_kind(prop_type):
        return
    min_value, max_value = _izom_propui_free_entry_numeric_bounds(reference_entry, prop_type)
    _izom_propui_free_normalize_threshold_collection(
        getattr(entry, 'value_labels', None),
        'target_value_int' if prop_type == 'INT' else 'target_value_float',
        prop_type,
        min_value=min_value,
        max_value=max_value,
        params=params,
        base_value=min_value if prop_type == 'FLOAT' else 0,
    )


def _izom_propui_free_clear_dependent_threshold_owner_cache(params=None):
    if params is None:
        _IZOM_PROPUI_FREE_DEPENDENT_THRESHOLD_OWNER_CACHE.clear()
        return
    params_key = _izom_propui_free_pointer_guard_key(params)
    stale_keys = [
        cache_key for cache_key in _IZOM_PROPUI_FREE_DEPENDENT_THRESHOLD_OWNER_CACHE
        if cache_key and cache_key[0] == params_key
    ]
    for cache_key in stale_keys:
        _IZOM_PROPUI_FREE_DEPENDENT_THRESHOLD_OWNER_CACHE.pop(cache_key, None)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
