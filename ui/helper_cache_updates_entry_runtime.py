# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_cache_updates_session import (
    _izom_propui_free_value_label_update_callbacks_suspended,
)
from .helper_selection_collections import (
    _izom_propui_free_bump_collection_revision,
)
from .helper_value_labels_source import (
    _izom_propui_free_find_value_label_owner,
)
from .helper_value_labels_thresholds import (
    _izom_propui_free_clear_dependent_threshold_owner_cache,
)
from .helper_cache_updates_invalidation import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_invalidate_runtime_display_cache,
    _izom_propui_free_schedule_runtime_entry_cache_invalidate,
    izom_propui_free_log_recovered,
)
from ..core.text import izom_propui_free_text_display_name
from ..core.value_labels_common import _izom_propui_free_is_numeric_type
from .helper_cache_updates_entry_params import (
    _izom_propui_free_context_bulk_entry_updates_suspended,
    _izom_propui_free_entry_runtime_update_callbacks_suspended,
    _izom_propui_free_find_params_for_entry,
)
from ..core.cache_common import _izom_propui_free_patch_cached_entry_display_fields
from .helper_value_labels_thresholds import _izom_propui_free_normalize_threshold_collection




def _izom_propui_free_params_state_updated(params, _context):
    _izom_propui_free_invalidate_runtime_display_cache(params)


def _izom_propui_free_sync_entry_list_name(entry):
    if entry is None:
        return
    try:
        editor_label = str(getattr(entry, 'editor_label', '') or '').strip()
    except (AttributeError, TypeError, ValueError):
        editor_label = ''
    try:
        label = str(getattr(entry, 'label', '') or '').strip()
    except (AttributeError, TypeError, ValueError):
        label = ''
    try:
        prop_id = str(getattr(entry, 'prop_id', '') or '').strip()
    except (AttributeError, TypeError, ValueError):
        prop_id = ''
    try:
        ui_order = int(getattr(entry, 'ui_order', 0) or 0)
    except (AttributeError, TypeError, ValueError):
        ui_order = 0
    if str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() == 'TEXT':
        display_name = izom_propui_free_text_display_name(entry)
    else:
        display_name = editor_label or label or prop_id or f"Entry {ui_order if ui_order > 0 else 1}"
    try:
        current_name = str(getattr(entry, 'name', '') or '')
    except (AttributeError, TypeError, ValueError):
        current_name = ''
    if current_name == display_name:
        return
    try:
        entry.name = display_name
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )


def _izom_propui_free_entry_runtime_display_updated(entry, context):
    if _izom_propui_free_entry_runtime_update_callbacks_suspended():
        return
    if _izom_propui_free_context_bulk_entry_updates_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_sync_entry_list_name(entry)
    _izom_propui_free_patch_cached_entry_display_fields(params, entry)
    _izom_propui_free_invalidate_runtime_display_cache(params)


def _izom_propui_free_entry_runtime_state_updated(entry, context):
    from .helper_cache_updates_arrays import _izom_propui_free_normalize_entry_value_label_component_settings
    from .helper_field_clamp import (
        _izom_propui_free_clamp_visibility_match_float,
        _izom_propui_free_clamp_visibility_match_int,
        _izom_propui_free_clamp_visibility_range_max_float,
        _izom_propui_free_clamp_visibility_range_max_int,
        _izom_propui_free_normalize_child_compare_component_dependents,
        _izom_propui_free_normalize_entry_child_compare_component_settings,
        _izom_propui_free_visibility_compare_info,
    )

    if _izom_propui_free_entry_runtime_update_callbacks_suspended():
        return
    if _izom_propui_free_context_bulk_entry_updates_suspended(context):
        return
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_sync_entry_list_name(entry)
    _izom_propui_free_normalize_entry_value_label_component_settings(entry, params=params)
    _izom_propui_free_normalize_entry_child_compare_component_settings(
        entry,
        params=params,
        use_component_attr='visibility_use_component',
        component_attr='visibility_component_index',
    )
    visibility_info = _izom_propui_free_visibility_compare_info(params, entry)
    _izom_propui_free_clamp_visibility_match_float(entry, params=params, info=visibility_info)
    _izom_propui_free_clamp_visibility_match_int(entry, params=params, info=visibility_info)
    _izom_propui_free_clamp_visibility_range_max_float(entry, params=params, info=visibility_info)
    _izom_propui_free_clamp_visibility_range_max_int(entry, params=params, info=visibility_info)
    _izom_propui_free_normalize_child_compare_component_dependents(params, entry)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)


def _izom_propui_free_value_label_rule_state_updated(item, context):
    if _izom_propui_free_value_label_update_callbacks_suspended():
        return
    if _izom_propui_free_context_bulk_entry_updates_suspended(context):
        return
    from .helper_value_labels import (
        _izom_propui_free_entry_component_rule_info,
        _izom_propui_free_self_value_label_companion_key,
    )

    params, entry, collection_owner, collection_name, _index = _izom_propui_free_find_value_label_owner(item, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clear_dependent_threshold_owner_cache(params)
    collection_parent = collection_owner if collection_owner is not None else entry
    if collection_parent is not None and collection_name == 'value_labels':
        component_info = _izom_propui_free_entry_component_rule_info(entry, item)
        if component_info.get('use_component'):
            source_type = str(component_info.get('component_meta', {}).get('component_kind', '') or '').strip().upper()
            if _izom_propui_free_is_numeric_type(source_type):
                component_items = [
                    candidate for candidate in (getattr(collection_parent, collection_name, None) or [])
                    if _izom_propui_free_entry_component_rule_info(entry, candidate).get('use_component')
                ]
                _izom_propui_free_normalize_threshold_collection(
                    component_items,
                    'target_value_int' if source_type == 'INT' else 'target_value_float',
                    source_type,
                    companion_key=lambda candidate, _entry=entry: _izom_propui_free_self_value_label_companion_key(_entry, candidate),
                    params=params,
                )
    if collection_parent is not None and collection_name == 'value_labels':
        _izom_propui_free_bump_collection_revision(collection_parent, collection_name)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)


def _izom_propui_free_value_label_rule_display_updated(item, context):
    if _izom_propui_free_value_label_update_callbacks_suspended():
        return
    if _izom_propui_free_context_bulk_entry_updates_suspended(context):
        return

    params, _entry, collection_owner, collection_name, _index = _izom_propui_free_find_value_label_owner(item, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_clear_dependent_threshold_owner_cache(params)
    if collection_owner is not None and collection_name == 'value_labels':
        _izom_propui_free_bump_collection_revision(collection_owner, collection_name)
    _izom_propui_free_invalidate_runtime_display_cache(params)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
