# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_value_labels_source import (
    izom_propui_free_entry_component_meta,
    izom_propui_free_log_recovered,
)
from ..core.float_arrays import (
    izom_propui_free_array_storage_from_visible,
)
from .helper_field_clamp_common import _izom_propui_free_snap_editor_float_value_for_params
from .lists_common_value_labels import _izom_propui_free_entry_value


def _izom_propui_free_exact_array_field_name(field_root, value_kind):
    root = str(field_root or 'value').strip() or 'value'
    normalized_kind = str(value_kind or '').strip().upper()
    if normalized_kind == 'INT_ARRAY':
        return f"{root}_int_array"
    if normalized_kind == 'BOOL_ARRAY':
        return f"{root}_bool_array"
    return f"{root}_float_array"

def _izom_propui_free_exact_array_component_bounds(reference_entry, component_meta, params=None):
    element_type = str(component_meta.get('element_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
    subtype = str(component_meta.get('subtype', 'NONE') or 'NONE').strip().upper() or 'NONE'
    value_kind = str(component_meta.get('value_kind', '') or '').strip().upper()
    if element_type == 'BOOL':
        return False, True
    if element_type == 'INT':
        try:
            low = int(_izom_propui_free_entry_value(reference_entry, 'min_int', 0))
        except (TypeError, ValueError):
            low = 0
        try:
            high = int(_izom_propui_free_entry_value(reference_entry, 'max_int', low))
        except (TypeError, ValueError):
            high = low
        if high < low:
            high = low
        return low, high

    if value_kind == 'COLOR' or subtype.startswith('COLOR'):
        low, high = 0.0, 1.0
    else:
        try:
            low = float(_izom_propui_free_entry_value(reference_entry, 'min_float', 0.0))
        except (TypeError, ValueError):
            low = 0.0
        try:
            high = float(_izom_propui_free_entry_value(reference_entry, 'max_float', low))
        except (TypeError, ValueError):
            high = low
        low = _izom_propui_free_snap_editor_float_value_for_params(params, low, base=0.0)
        high = _izom_propui_free_snap_editor_float_value_for_params(params, high, base=0.0)
    if high < low:
        high = low
    return low, high

def _izom_propui_free_exact_array_low_key(component_meta, reference_entry=None, params=None):
    try:
        size = int(component_meta.get('size', 4) or 4)
    except (TypeError, ValueError):
        size = 4
    low, _high = _izom_propui_free_exact_array_component_bounds(reference_entry, component_meta, params=params)
    return tuple(low for _index in range(max(1, size)))

def _izom_propui_free_store_exact_array_key(item, field_name, component_meta, value_key):
    element_type = str(component_meta.get('element_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
    subtype = str(component_meta.get('subtype', 'NONE') or 'NONE').strip().upper() or 'NONE'
    try:
        size = int(component_meta.get('size', len(value_key)) or len(value_key))
    except (TypeError, ValueError):
        size = len(value_key)
    try:
        previous = getattr(item, field_name, ())
    except AttributeError:
        previous = ()
    storage = izom_propui_free_array_storage_from_visible(
        tuple(value_key),
        element_type,
        subtype,
        size=size,
        previous=previous,
        default=previous,
    )
    try:
        setattr(item, field_name, storage)
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )

def _izom_propui_free_set_low_exact_array_value(item, field_root, value_kind, reference_entry=None, params=None):
    component_meta = izom_propui_free_entry_component_meta(reference_entry, value_kind)
    field_name = _izom_propui_free_exact_array_field_name(field_root, value_kind)
    low_key = _izom_propui_free_exact_array_low_key(component_meta, reference_entry=reference_entry, params=params)
    _izom_propui_free_store_exact_array_key(item, field_name, component_meta, low_key)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
