# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import bpy

from .helper_value_labels_base import izom_propui_free_log_recovered
from ..core.cache_common import _izom_propui_free_pointer_guard_key
from ..core.cache_state import izom_propui_free_cached_runtime_parent_lookup
from ..core.cache_value_labels import izom_propui_free_cached_value_label_owner_map
from ..core.context import izom_propui_free_context_params
from ..core.text import _izom_propui_free_limit_label_input_text
from ..core.value_access_common import (
    izom_propui_free_clamp_component_slot,
    izom_propui_free_is_exact_match_value_kind,
    izom_propui_free_is_numeric_value_kind,
)
from ..core.value_access_entries import (
    izom_propui_free_entry_component_meta,
    izom_propui_free_entry_value_kind,
)
from ..core.value_labels_compare import (
    _izom_propui_free_numeric_entry_high,
    _izom_propui_free_numeric_entry_low,
)
from .helper_cache_updates_entry_params import (
    _izom_propui_free_context_bulk_entry_updates_suspended,
    _izom_propui_free_find_params_for_entry,
)
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_value_label_runtime_display_cache
from .helper_cache_updates_session import _izom_propui_free_value_label_update_callbacks_suspended
from .helper_selection_collections import _izom_propui_free_active_collection_item
from .helper_selection_common import (
    _izom_propui_free_data_value,
    _izom_propui_free_entry_by_uid,
)


def _izom_propui_free_value_label_source_info(owner, active_propname, context=None):
    collection_name = 'value_labels'
    params = None
    entry = owner if hasattr(owner, 'prop_type') else None
    collection_owner = owner
    if entry is not None:
        params = _izom_propui_free_find_params_for_entry(entry, context)
    if entry is None or params is None:
        found_params, found_entry, found_collection_owner, found_collection_name, _found_index = _izom_propui_free_find_value_label_owner(owner, context)
        if found_entry is not None:
            if found_collection_name == 'value_labels':
                params = found_params
                entry = found_entry
                collection_owner = found_collection_owner if found_collection_owner is not None else owner

    source_entry_for_value = _izom_propui_free_value_label_reference_entry(params, entry) if entry is not None else owner
    entry_prop_type = str(_izom_propui_free_data_value(source_entry_for_value, 'prop_type', 'FLOAT') or 'FLOAT')
    entry_value_kind = izom_propui_free_entry_value_kind(source_entry_for_value, entry_prop_type)
    current = _izom_propui_free_active_collection_item(collection_owner, collection_name) if collection_owner is not None else None
    source = source_entry_for_value
    source_type = entry_value_kind
    target_mode = 'SELF'

    return {
        'params': params,
        'source': source,
        'source_type': source_type,
        'collection_name': collection_name,
        'target_mode': target_mode,
        'entry': entry,
        'collection_owner': collection_owner,
        'current': current,
    }

def _izom_propui_free_value_label_updated(item, context):
    if _izom_propui_free_value_label_update_callbacks_suspended():
        return
    if _izom_propui_free_context_bulk_entry_updates_suspended(context):
        return
    try:
        limited = _izom_propui_free_limit_label_input_text(getattr(item, 'label', ''))
        if getattr(item, 'label', '') != limited:
            item.label = limited
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    _izom_propui_free_invalidate_value_label_runtime_display_cache(item, context)

def _izom_propui_free_find_value_label_owner(item, context=None):
    item_key = _izom_propui_free_pointer_guard_key(item)
    item_ptr = item_key if isinstance(item_key, int) else None

    def _matches(candidate):
        if candidate is item:
            return True
        if item_ptr is not None:
            try:
                return int(candidate.as_pointer()) == item_ptr
            except (AttributeError, TypeError, ValueError, ReferenceError):
                return False
        return False

    def candidate_params_iter():
        seen = set()
        for candidate_context in (context, bpy.context):
            params = izom_propui_free_context_params(candidate_context)
            if params is None:
                continue
            marker = _izom_propui_free_pointer_guard_key(params)
            if marker in seen:
                continue
            seen.add(marker)
            yield params
        try:
            scenes = list(bpy.data.scenes)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(category='UI', exception=exc)
            scenes = []
        for scene in scenes:
            try:
                params = getattr(scene, 'izom_propui_free', None)
            except (AttributeError, TypeError, ValueError, ReferenceError):
                continue
            if params is None:
                continue
            marker = _izom_propui_free_pointer_guard_key(params)
            if marker in seen:
                continue
            seen.add(marker)
            yield params

    seen = set()
    for params in candidate_params_iter():
        marker = _izom_propui_free_pointer_guard_key(params)
        if marker in seen:
            continue
        seen.add(marker)
        owner_map = None
        try:
            owner_map = izom_propui_free_cached_value_label_owner_map(params)
            cached_owner = owner_map.get(item_key)
        except (AttributeError, TypeError, ValueError, ReferenceError, RecursionError):
            cached_owner = None
        if cached_owner is not None:
            try:
                _cached_params, _cached_entry, cached_collection_owner, cached_collection_name, cached_index = cached_owner
                cached_collection = getattr(cached_collection_owner, str(cached_collection_name or ''), None)
                cached_index = int(cached_index)
                if cached_collection is not None and 0 <= cached_index < len(cached_collection):
                    if _matches(cached_collection[cached_index]):
                        return cached_owner
            except (AttributeError, TypeError, ValueError, ReferenceError, RecursionError):
                pass
            try:
                owner_map.pop(item_key, None)
            except (AttributeError, TypeError, ValueError, ReferenceError):
                pass
        try:
            entries = getattr(params, 'izom_propui_free_entries', None)
        except (AttributeError, TypeError, ValueError, ReferenceError):
            entries = None
        if not entries:
            continue

        def remember(result):
            if owner_map is not None:
                try:
                    owner_map[item_key] = result
                except (AttributeError, TypeError, ValueError, ReferenceError) as exc:
                    izom_propui_free_log_recovered(category='UI', exception=exc)
            return result

        for entry in entries:
            try:
                for index, candidate in enumerate(getattr(entry, 'value_labels', None) or []):
                    if _matches(candidate):
                        return remember((params, entry, entry, 'value_labels', index))
            except (AttributeError, TypeError, ValueError, ReferenceError, RecursionError):
                continue
    return None, None, None, None, -1

def _izom_propui_free_entry_numeric_bounds(entry, prop_type):
    if not izom_propui_free_is_numeric_value_kind(prop_type):
        return None, None
    return (
        _izom_propui_free_numeric_entry_low(entry, prop_type),
        _izom_propui_free_numeric_entry_high(entry, prop_type),
    )

def _izom_propui_free_component_slot_value(owner, attr_name, size):
    slot = izom_propui_free_clamp_component_slot(getattr(owner, attr_name, 1), size, default=1)
    return slot

def _izom_propui_free_value_label_reference_entry(params, entry):
    return entry


def _izom_propui_free_entry_effective_value_label_kind(params, entry):
    reference_entry = _izom_propui_free_value_label_reference_entry(params, entry) or entry
    if reference_entry is None:
        return ''
    return str(izom_propui_free_entry_value_kind(
        reference_entry,
        str(_izom_propui_free_data_value(reference_entry, 'prop_type', '') or ''),
    ) or '').strip().upper()


def _izom_propui_free_entry_uses_bool_value_bucket_scope(params, entry):
    return _izom_propui_free_entry_effective_value_label_kind(params, entry) == 'BOOL'


def _izom_propui_free_entry_component_rule_info(entry, item=None, *, reference_entry=None):
    component_entry = reference_entry if reference_entry is not None else entry
    value_kind = izom_propui_free_entry_value_kind(
        component_entry,
        str(_izom_propui_free_data_value(component_entry, 'prop_type', 'FLOAT') or 'FLOAT'),
    )
    component_meta = izom_propui_free_entry_component_meta(component_entry, value_kind)
    supports_component = bool(component_meta.get('supported', False))
    entry_use_component = bool(getattr(entry, 'value_labels_use_component', False))
    entry_component_slot = _izom_propui_free_component_slot_value(entry, 'value_labels_component_index', component_meta.get('size', 1))
    if item is not None:
        row_use_component = bool(getattr(item, 'use_source_component', False))
        use_component = supports_component and (row_use_component or entry_use_component)
        component_slot = _izom_propui_free_component_slot_value(
            item,
            'source_component_index',
            component_meta.get('size', 1),
        ) if row_use_component else entry_component_slot
    else:
        use_component = supports_component and entry_use_component
        component_slot = entry_component_slot
    return {
        'value_kind': value_kind,
        'component_meta': component_meta,
        'use_component': use_component,
        'component_slot': component_slot,
    }

def _izom_propui_free_self_value_label_companion_key(entry, item, *, reference_entry=None):
    component_info = _izom_propui_free_entry_component_rule_info(entry, item, reference_entry=reference_entry)
    if component_info.get('use_component'):
        return ('component', int(component_info.get('component_slot', 1) or 1))
    return ('full',)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
