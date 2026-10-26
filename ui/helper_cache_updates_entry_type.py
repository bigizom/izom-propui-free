# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_cache_updates_entry_runtime import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_find_params_for_entry,
    izom_propui_free_log_recovered,
)
from .helper_cache_updates_invalidation import _izom_propui_free_pointer_guard_key
from .helper_selection_context import (
    _izom_propui_free_list_context_updates_suspended,
)
from ..core.float_arrays import izom_propui_free_normalize_array_element_type
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_ENTRY_TYPE_UPDATE_GUARD
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_runtime_entry_cache



def _izom_propui_free_entry_type_guard_key(entry):
    return (_izom_propui_free_pointer_guard_key(entry), 'entry_type')


def _izom_propui_free_normalize_entry_after_type_change(entry, context=None):
    from .helper_field_clamp import (
        _izom_propui_free_clamp_visibility_match_float,
        _izom_propui_free_clamp_visibility_match_int,
        _izom_propui_free_float_range_updated,
        _izom_propui_free_general_float_field_updated,
        _izom_propui_free_int_range_updated,
    )
    from .helper_value_labels import _izom_propui_free_visibility_inheritance_depth_updated

    if entry is None:
        return False

    params = _izom_propui_free_find_params_for_entry(entry, context)
    if params is None or _izom_propui_free_list_context_updates_suspended(params):
        return False

    prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
    guard_key = _izom_propui_free_entry_type_guard_key(entry)
    if guard_key in _IZOM_PROPUI_FREE_ENTRY_TYPE_UPDATE_GUARD:
        return False

    _IZOM_PROPUI_FREE_ENTRY_TYPE_UPDATE_GUARD.add(guard_key)
    try:
        if prop_type == 'ARRAY':
            array_element_type = izom_propui_free_normalize_array_element_type(getattr(entry, 'array_element_type', 'FLOAT'), 'FLOAT')
            if array_element_type == 'FLOAT':
                _izom_propui_free_float_range_updated(entry, context)
                _izom_propui_free_general_float_field_updated(entry, context, field_name='step_float')
            elif array_element_type == 'INT':
                _izom_propui_free_int_range_updated(entry, context)
        elif prop_type == 'FLOAT':
            _izom_propui_free_float_range_updated(entry, context)
            _izom_propui_free_general_float_field_updated(entry, context, field_name='step_float')
        elif prop_type == 'INT':
            _izom_propui_free_int_range_updated(entry, context)
        _izom_propui_free_clamp_visibility_match_float(entry, context, params=params)
        _izom_propui_free_clamp_visibility_match_int(entry, context, params=params)
        _izom_propui_free_visibility_inheritance_depth_updated(entry, context)
    finally:
        _IZOM_PROPUI_FREE_ENTRY_TYPE_UPDATE_GUARD.discard(guard_key)
    return True


def _izom_propui_free_prop_type_updated(entry, context):
    from .helper_field_clamp import _izom_propui_free_normalize_child_compare_component_dependents
    from .helper_selection import _izom_propui_free_list_context_updates_suspended

    guard_key = _izom_propui_free_entry_type_guard_key(entry)
    if guard_key in _IZOM_PROPUI_FREE_ENTRY_TYPE_UPDATE_GUARD:
        return

    params = _izom_propui_free_find_params_for_entry(entry, context)
    if params is not None and (
        _izom_propui_free_list_context_updates_suspended(params)
        or _izom_propui_free_bulk_entry_updates_suspended(params)
    ):
        return

    _izom_propui_free_normalize_entry_after_type_change(entry, context)
    try:
        prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        from ..core.constants import izom_propui_free_is_managed_prop_type

        if not izom_propui_free_is_managed_prop_type(prop_type):
            setattr(entry, 'prop_id', '')
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    _izom_propui_free_normalize_child_compare_component_dependents(params, entry)
    _izom_propui_free_invalidate_runtime_entry_cache(params)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
