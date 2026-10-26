# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_sync_common import (
    izom_propui_free_log_recovered,
)
from ..bpy_support.idprops import (
    _izom_propui_free_get_idprop_ui_data,
    _izom_propui_free_has_custom_prop,
)
from ..core.float_arrays import (
    izom_propui_free_array_visible_value,
    izom_propui_free_normalize_array_size,
    izom_propui_free_normalize_array_storage,
)
from ..core.runtime_idprops import (
    _izom_propui_free_detect_array_element_type,
    _izom_propui_free_detect_supported_prop_type,
)
from ..core.value_access_entries import (
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_size,
    izom_propui_free_entry_array_subtype,
)



def _izom_propui_free_entry_value_for_owner(entry, target_owner, relevant_owners, *, prefer_editor_default=False):
    prop_id = str(entry.get('prop_id', '') or '').strip()
    prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    target_has_prop = _izom_propui_free_has_custom_prop(target_owner, prop_id)
    target_value = None
    target_ui_data = {}
    target_type = None
    if target_has_prop:
        try:
            target_value = target_owner[prop_id]
            target_ui_data = _izom_propui_free_get_idprop_ui_data(target_owner, prop_id)
            target_type = _izom_propui_free_detect_supported_prop_type(target_value, target_ui_data)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            target_value = None
            target_ui_data = {}
            target_type = None
    source_owner = None if prefer_editor_default else (target_owner if target_has_prop else None)
    source_type = target_type if source_owner is target_owner else None
    if source_owner is None:
        for owner in relevant_owners:
            if owner is None or owner == target_owner or not _izom_propui_free_has_custom_prop(owner, prop_id):
                continue
            source_owner = owner
            try:
                source_type = _izom_propui_free_detect_supported_prop_type(
                    owner[prop_id],
                    _izom_propui_free_get_idprop_ui_data(owner, prop_id),
                )
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                source_type = None
            break

    if prop_type == 'FLOAT':
        low = min(float(entry.get('min_float', 0.0)), float(entry.get('max_float', 1.0)))
        high = max(float(entry.get('min_float', 0.0)), float(entry.get('max_float', 1.0)))
        source_value = target_value if source_owner is target_owner else (source_owner[prop_id] if source_owner is not None else None)
        value = float(source_value) if source_owner is not None and source_type in {'FLOAT', 'INT', 'BOOL'} else float(entry.get('default_float', 0.0))
        value = min(max(value, low), high)
    elif prop_type == 'INT':
        low = min(int(entry.get('min_int', 0)), int(entry.get('max_int', 5)))
        high = max(int(entry.get('min_int', 0)), int(entry.get('max_int', 5)))
        source_value = target_value if source_owner is target_owner else (source_owner[prop_id] if source_owner is not None else None)
        value = int(source_value) if source_owner is not None and source_type in {'INT', 'BOOL', 'FLOAT'} else int(entry.get('default_int', 0))
        value = min(max(value, low), high)
    elif prop_type == 'BOOL':
        source_value = target_value if source_owner is target_owner else (source_owner[prop_id] if source_owner is not None else None)
        value = bool(source_value) if source_owner is not None and source_type in {'BOOL', 'INT', 'FLOAT'} else bool(entry.get('default_bool', False))
    elif prop_type == 'ARRAY':
        array_element_type = izom_propui_free_entry_array_element_type(entry, 'FLOAT')
        array_subtype = izom_propui_free_entry_array_subtype(entry, 'NONE')
        array_size = izom_propui_free_entry_array_size(entry, 4)
        source_matches_entry = False
        if source_owner is not None and source_type == 'ARRAY':
            try:
                source_value = target_value if source_owner is target_owner else source_owner[prop_id]
                source_ui_data = target_ui_data if source_owner is target_owner else _izom_propui_free_get_idprop_ui_data(source_owner, prop_id)
                source_matches_entry = _izom_propui_free_detect_array_element_type(
                    source_value,
                    source_ui_data,
                ) == array_element_type
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                source_matches_entry = False
        source_value = (
            izom_propui_free_array_visible_value(
                target_value if source_owner is target_owner else source_owner[prop_id],
                array_element_type,
                array_subtype,
                size=array_size,
            )
            if source_owner is not None and source_matches_entry else
            _izom_propui_free_entry_array_default_visible_value(
                entry,
                array_element_type,
                array_subtype,
                array_size,
            )
        )
        if array_element_type == 'FLOAT':
            low = min(float(entry.get('min_float', 0.0)), float(entry.get('max_float', 1.0)))
            high = max(float(entry.get('min_float', 0.0)), float(entry.get('max_float', 1.0)))
            value = tuple(min(max(float(component), low), high) for component in source_value)
        elif array_element_type == 'INT':
            low = min(int(entry.get('min_int', 0)), int(entry.get('max_int', 5)))
            high = max(int(entry.get('min_int', 0)), int(entry.get('max_int', 5)))
            value = tuple(min(max(int(component), low), high) for component in source_value)
        else:
            value = tuple(bool(component) for component in source_value)
    else:
        return None, source_owner, source_type, target_has_prop, target_value, target_ui_data, target_type
    return value, source_owner, source_type, target_has_prop, target_value, target_ui_data, target_type


def _izom_propui_free_entry_array_default_visible_value(entry, array_element_type, array_subtype, array_size):
    field_name = {
        'INT': 'default_int_array',
        'BOOL': 'default_bool_array',
    }.get(array_element_type, 'default_float_array')
    raw_value = entry.get(field_name, ())
    if isinstance(raw_value, tuple) and len(raw_value) == 32:
        storage = raw_value
    else:
        storage = izom_propui_free_normalize_array_storage(raw_value, array_element_type)
    return tuple(storage[:izom_propui_free_normalize_array_size(array_size, array_subtype, array_element_type)])

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
