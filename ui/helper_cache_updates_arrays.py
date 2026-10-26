# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .helper_cache_updates_entry_runtime import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_context_bulk_entry_updates_suspended,
    _izom_propui_free_find_params_for_entry,
    _izom_propui_free_schedule_runtime_entry_cache_invalidate,
    _izom_propui_free_sync_entry_list_name,
    izom_propui_free_log_recovered,
)
from ..core.value_access_common import izom_propui_free_clamp_component_slot
from ..core.value_access_entries import (
    izom_propui_free_clear_value_access_memo,
    izom_propui_free_entry_component_meta,
)
from ..core.cache_state import izom_propui_free_cached_runtime_parent_lookup
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_ARRAY_SHAPE_UPDATE_GUARD
from .helper_cache_updates_entry_params import (
    _izom_propui_free_resume_entry_updates,
    _izom_propui_free_suspend_entry_updates,
)
from .helper_cache_updates_invalidation import (
    _izom_propui_free_invalidate_runtime_entry_cache,
    _izom_propui_free_pointer_guard_key,
)
from .helper_value_labels_dependencies import _izom_propui_free_normalize_dependent_thresholds
from .helper_value_labels_thresholds import _izom_propui_free_clear_dependent_threshold_owner_cache




def _izom_propui_free_sync_known_color_array_proxies(owner, field_names):
    if owner is None:
        return

    try:
        from .model_proxies import _izom_propui_free_sync_float_array_color_proxy
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return

    for field_name in field_names:
        normalized_field_name = str(field_name or '').strip()
        if not normalized_field_name:
            continue
        try:
            _izom_propui_free_sync_float_array_color_proxy(
                owner,
                normalized_field_name,
                size=4,
                proxy_name=f"{normalized_field_name}_color",
            )
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            continue


def _izom_propui_free_entry_array_value_updated(entry, context):
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_sync_known_color_array_proxies(
        entry,
        ('default_float_array', 'visibility_match_float_array'),
    )
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)


def _izom_propui_free_entry_array_shape_updated(entry, context):
    from .helper_field_clamp import (
        _izom_propui_free_normalize_child_compare_component_dependents,
        _izom_propui_free_normalize_entry_child_compare_component_settings,
    )

    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return

    guard_key = (_izom_propui_free_pointer_guard_key(entry), 'array_shape')
    if guard_key in _IZOM_PROPUI_FREE_ARRAY_SHAPE_UPDATE_GUARD:
        return

    _IZOM_PROPUI_FREE_ARRAY_SHAPE_UPDATE_GUARD.add(guard_key)
    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        izom_propui_free_clear_value_access_memo()
        _izom_propui_free_clear_dependent_threshold_owner_cache(params)
        _izom_propui_free_sync_entry_list_name(entry)
        _izom_propui_free_normalize_entry_value_label_component_settings(entry, params=params)
        _izom_propui_free_normalize_entry_child_compare_component_settings(
            entry,
            params=params,
            use_component_attr='visibility_use_component',
            component_attr='visibility_component_index',
        )
        _izom_propui_free_normalize_child_compare_component_dependents(params, entry)
        _izom_propui_free_normalize_dependent_thresholds(
            entry,
            params,
            prune_unresolvable_exact_arrays=True,
        )
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)
        _IZOM_PROPUI_FREE_ARRAY_SHAPE_UPDATE_GUARD.discard(guard_key)

    _izom_propui_free_invalidate_runtime_entry_cache(params)


def _izom_propui_free_value_label_array_value_updated(item, context):
    if _izom_propui_free_context_bulk_entry_updates_suspended(context):
        return
    from .helper_selection_collections import _izom_propui_free_bump_collection_revision
    from .helper_value_labels_source import _izom_propui_free_find_value_label_owner

    params, entry, collection_owner, collection_name, _index = _izom_propui_free_find_value_label_owner(item, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return
    _izom_propui_free_sync_known_color_array_proxies(
        item,
        ('value_float_array', 'target_value_float_array'),
    )
    if collection_owner is not None and collection_name == 'value_labels':
        _izom_propui_free_bump_collection_revision(collection_owner, collection_name)
    _izom_propui_free_schedule_runtime_entry_cache_invalidate(params)


def _izom_propui_free_entry_value_label_component_reference(entry, params=None):
    if entry is None:
        return None
    return entry


def _izom_propui_free_normalize_entry_value_label_component_settings(entry, params=None):
    if entry is None:
        return

    reference_entry = _izom_propui_free_entry_value_label_component_reference(entry, params=params)
    if reference_entry is None:
        return

    reference_prop_type = (
        str(reference_entry.get('prop_type', 'FLOAT') or 'FLOAT')
        if isinstance(reference_entry, dict)
        else str(getattr(reference_entry, 'prop_type', 'FLOAT') or 'FLOAT')
    )
    component_meta = izom_propui_free_entry_component_meta(reference_entry, reference_prop_type)
    supports_component = bool(component_meta.get('supported', False))
    try:
        use_component = bool(getattr(entry, 'value_labels_use_component', False))
    except (AttributeError, TypeError, ValueError):
        use_component = False

    if not supports_component:
        if use_component:
            try:
                setattr(entry, 'value_labels_use_component', False)
            except (AttributeError, TypeError, ValueError) as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
        try:
            if int(getattr(entry, 'value_labels_component_index', 1) or 1) != 1:
                setattr(entry, 'value_labels_component_index', 1)
        except (AttributeError, TypeError, ValueError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
        return

    component_slot = izom_propui_free_clamp_component_slot(
        getattr(entry, 'value_labels_component_index', 1),
        component_meta.get('size', 1),
        default=1,
    )
    try:
        current_slot = int(getattr(entry, 'value_labels_component_index', component_slot) or component_slot)
    except (AttributeError, TypeError, ValueError):
        current_slot = component_slot
    if current_slot != component_slot:
        try:
            setattr(entry, 'value_labels_component_index', component_slot)
        except (AttributeError, TypeError, ValueError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
    if use_component:
        for item in getattr(entry, 'value_labels', None) or []:
            try:
                if not bool(getattr(item, 'use_source_component', False)):
                    setattr(item, 'use_source_component', True)
            except (AttributeError, TypeError, ValueError) as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
            try:
                if int(getattr(item, 'source_component_index', 1) or 1) != component_slot:
                    setattr(item, 'source_component_index', component_slot)
            except (AttributeError, TypeError, ValueError) as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
