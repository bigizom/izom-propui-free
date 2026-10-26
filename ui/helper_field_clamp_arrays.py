# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .helper_field_clamp_compare import (
    _izom_propui_free_find_params_for_entry,
    _izom_propui_free_normalize_child_compare_component_dependents,
    _izom_propui_free_pointer_guard_key,
    _izom_propui_free_resume_entry_updates,
    _izom_propui_free_suspend_entry_updates,
    izom_propui_free_log_recovered,
)
from ..core.collection_sync import _izom_propui_free_values_differ
from ..core.float_arrays import (
    izom_propui_free_normalize_array_element_type,
    izom_propui_free_normalize_float_array_subtype,
    izom_propui_free_remap_array_storage,
)
from ..core.value_access_entries import izom_propui_free_clear_value_access_memo
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD
from .helper_cache_updates_entry_params import _izom_propui_free_bulk_entry_updates_suspended
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_runtime_entry_cache
from .helper_field_clamp_common import _izom_propui_free_entry_field_update_suspended
from .helper_value_labels_dependencies import _izom_propui_free_normalize_dependent_thresholds
from .helper_value_labels_thresholds import _izom_propui_free_clear_dependent_threshold_owner_cache




def _izom_propui_free_remap_typed_array_field(owner, field_name, element_type, old_subtype, new_subtype, *, size=4):
    if owner is None:
        return
    try:
        current_value = getattr(owner, field_name)
    except AttributeError:
        return
    remapped_value = izom_propui_free_remap_array_storage(
        current_value,
        element_type,
        old_subtype,
        new_subtype,
        size=size,
        default=current_value,
    )
    if not _izom_propui_free_values_differ(current_value, remapped_value):
        return
    try:
        setattr(owner, field_name, remapped_value)
    except (AttributeError, TypeError, ValueError):
        return


def _izom_propui_free_remap_array_rule_sources(collection, source_uid, element_type, old_subtype, new_subtype, *, size=4):
    normalized_source_uid = str(source_uid or '').strip()
    if not normalized_source_uid:
        return
    field_name = 'value_float_array'
    if element_type == 'INT':
        field_name = 'value_int_array'
    elif element_type == 'BOOL':
        field_name = 'value_bool_array'
    for item in collection or []:
        _izom_propui_free_remap_typed_array_field(item, field_name, element_type, old_subtype, new_subtype, size=size)


def _izom_propui_free_remap_float_array_dependents(params, entry, old_subtype, new_subtype):
    if params is None or entry is None:
        return
    entry_uid = str(getattr(entry, 'uid', '') or '').strip()
    if not entry_uid:
        return

    entry_element_type = izom_propui_free_normalize_array_element_type(getattr(entry, 'array_element_type', 'FLOAT'), 'FLOAT')
    try:
        entry_array_size = int(getattr(entry, 'array_size', 4) or 4)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        entry_array_size = 4

    if entry_element_type == 'FLOAT':
        _izom_propui_free_remap_typed_array_field(entry, 'default_float_array', 'FLOAT', old_subtype, new_subtype, size=entry_array_size)
    elif entry_element_type == 'INT':
        _izom_propui_free_remap_typed_array_field(entry, 'default_int_array', 'INT', old_subtype, new_subtype, size=entry_array_size)
    elif entry_element_type == 'BOOL':
        _izom_propui_free_remap_typed_array_field(entry, 'default_bool_array', 'BOOL', old_subtype, new_subtype, size=entry_array_size)
    for bucket in getattr(entry, 'value_labels', []) or []:
        if entry_element_type == 'FLOAT':
            _izom_propui_free_remap_typed_array_field(bucket, 'target_value_float_array', 'FLOAT', old_subtype, new_subtype, size=entry_array_size)
        elif entry_element_type == 'INT':
            _izom_propui_free_remap_typed_array_field(bucket, 'target_value_int_array', 'INT', old_subtype, new_subtype, size=entry_array_size)
        elif entry_element_type == 'BOOL':
            _izom_propui_free_remap_typed_array_field(bucket, 'target_value_bool_array', 'BOOL', old_subtype, new_subtype, size=entry_array_size)

    for candidate in getattr(params, 'izom_propui_free_entries', []) or []:
        if str(getattr(candidate, 'parent_uid', '') or '').strip() == entry_uid:
            if entry_element_type == 'FLOAT':
                _izom_propui_free_remap_typed_array_field(candidate, 'visibility_match_float_array', 'FLOAT', old_subtype, new_subtype, size=entry_array_size)
            elif entry_element_type == 'INT':
                _izom_propui_free_remap_typed_array_field(candidate, 'visibility_match_int_array', 'INT', old_subtype, new_subtype, size=entry_array_size)
            elif entry_element_type == 'BOOL':
                _izom_propui_free_remap_typed_array_field(candidate, 'visibility_match_bool_array', 'BOOL', old_subtype, new_subtype, size=entry_array_size)

        _izom_propui_free_remap_array_rule_sources(
            getattr(candidate, 'value_labels', None),
            entry_uid,
            entry_element_type,
            old_subtype,
            new_subtype,
            size=entry_array_size,
        )


def _izom_propui_free_float_array_subtype_updated(entry, context):

    if _izom_propui_free_entry_field_update_suspended(context):
        try:
            entry.float_array_subtype_cached = izom_propui_free_normalize_float_array_subtype(
                getattr(entry, 'float_array_subtype', 'NONE'),
                'NONE',
            )
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
        return

    params = _izom_propui_free_find_params_for_entry(entry, context)
    new_subtype = izom_propui_free_normalize_float_array_subtype(
        getattr(entry, 'float_array_subtype', 'NONE'),
        'NONE',
    )
    old_subtype = izom_propui_free_normalize_float_array_subtype(
        getattr(entry, 'float_array_subtype_cached', new_subtype),
        new_subtype,
    )

    if _izom_propui_free_bulk_entry_updates_suspended(params):
        try:
            entry.float_array_subtype_cached = new_subtype
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
        return

    guard_key = (_izom_propui_free_pointer_guard_key(entry), 'float_array_subtype')
    if guard_key in _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD:
        return

    _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.add(guard_key)
    entry_update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        izom_propui_free_clear_value_access_memo()
        _izom_propui_free_clear_dependent_threshold_owner_cache(params)
        if old_subtype != new_subtype:
            _izom_propui_free_remap_float_array_dependents(params, entry, old_subtype, new_subtype)
        _izom_propui_free_normalize_child_compare_component_dependents(params, entry)
        _izom_propui_free_normalize_dependent_thresholds(
            entry,
            params,
            prune_unresolvable_exact_arrays=True,
        )
        try:
            entry.float_array_subtype_cached = new_subtype
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    finally:
        if entry_update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)
        _IZOM_PROPUI_FREE_EDITOR_FLOAT_UPDATE_GUARD.discard(guard_key)

    _izom_propui_free_invalidate_runtime_entry_cache(params)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
