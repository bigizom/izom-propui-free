# SPDX-License-Identifier: GPL-3.0-or-later

from .snapshot_entries_labels import (
    _izom_propui_free_ensure_item_uid,
    _izom_propui_free_snapshot_typed_array_value,
    _izom_propui_free_snapshot_value_label,
)
from .entry_ids import _izom_propui_free_limit_entry_snapshot_strings
from .snapshot_entries_common import (
    _IZOM_PROPUI_FREE_ENTRY_CONDITION_ARRAY_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_DEFAULT_ARRAY_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_ARRAY_PRESENTATION_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_BOOL_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_COMMON_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_FLOAT_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_INT_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_TEXT_STYLE_FIELDS,
    _IZOM_PROPUI_FREE_ENTRY_SERIALIZED_SCALAR_FIELDS,
    _izom_propui_free_fresh_entry_default_values,
)



def _izom_propui_free_entry_runtime_needs_default_arrays(data):
    prop_type = str(data.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    return prop_type == 'ARRAY'


def _izom_propui_free_entry_runtime_needs_condition_arrays(data, scope):
    if scope != 'visibility':
        return False
    mode_attr = 'number_child_visibility'
    mode = str(data.get(mode_attr, 'ALWAYS') or 'ALWAYS').strip().upper()
    return mode == 'EQUAL' and not bool(data.get(f'{scope}_use_component', False))


def _izom_propui_free_entry_runtime_needs_component_label_overrides(data):
    return False


def _izom_propui_free_entry_runtime_value_labels_need_arrays(data):
    prop_type = str(data.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    if bool(data.get('value_labels_use_component', False)):
        return False
    if prop_type == 'ARRAY':
        return True
    return False


def _izom_propui_free_copy_runtime_fields(data, entry, field_names):
    defaults = _izom_propui_free_fresh_entry_default_values()
    for field_name in field_names:
        data[field_name] = getattr(entry, field_name, defaults.get(field_name))


def _izom_propui_free_snapshot_runtime_entry_fields(entry):
    defaults = _izom_propui_free_fresh_entry_default_values()
    data = {name: getattr(entry, name, defaults.get(name)) for name in _IZOM_PROPUI_FREE_ENTRY_RUNTIME_COMMON_FIELDS}
    prop_type = str(data.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
    if prop_type == 'TEXT':
        _izom_propui_free_copy_runtime_fields(data, entry, _IZOM_PROPUI_FREE_ENTRY_RUNTIME_TEXT_STYLE_FIELDS)
    if prop_type in {'FLOAT'}:
        _izom_propui_free_copy_runtime_fields(data, entry, _IZOM_PROPUI_FREE_ENTRY_RUNTIME_FLOAT_FIELDS)
    elif prop_type == 'INT':
        _izom_propui_free_copy_runtime_fields(data, entry, _IZOM_PROPUI_FREE_ENTRY_RUNTIME_INT_FIELDS)
    elif prop_type == 'BOOL':
        _izom_propui_free_copy_runtime_fields(data, entry, _IZOM_PROPUI_FREE_ENTRY_RUNTIME_BOOL_FIELDS)
    elif prop_type == 'ARRAY':
        _izom_propui_free_copy_runtime_fields(data, entry, _IZOM_PROPUI_FREE_ENTRY_RUNTIME_ARRAY_PRESENTATION_FIELDS)
        element_type = str(data.get('array_element_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
        if element_type == 'INT':
            _izom_propui_free_copy_runtime_fields(data, entry, _IZOM_PROPUI_FREE_ENTRY_RUNTIME_INT_FIELDS)
        elif element_type == 'BOOL':
            data['default_bool'] = getattr(entry, 'default_bool')
        else:
            _izom_propui_free_copy_runtime_fields(data, entry, _IZOM_PROPUI_FREE_ENTRY_RUNTIME_FLOAT_FIELDS)
    return data


def _izom_propui_free_snapshot_entry(entry, *, limit_strings=True, runtime=False):
    data = (
        _izom_propui_free_snapshot_runtime_entry_fields(entry)
        if runtime else
        {name: getattr(entry, name) for name in _IZOM_PROPUI_FREE_ENTRY_SERIALIZED_SCALAR_FIELDS}
    )
    data['uid'] = _izom_propui_free_ensure_item_uid(entry)
    if not runtime or _izom_propui_free_entry_runtime_needs_default_arrays(data):
        for attr_name, (element_type, default_value) in _IZOM_PROPUI_FREE_ENTRY_DEFAULT_ARRAY_FIELDS.items():
            data[attr_name] = _izom_propui_free_snapshot_typed_array_value(
                getattr(entry, attr_name),
                element_type,
                default_value,
            )
    for scope in ('visibility',):
        if not runtime or _izom_propui_free_entry_runtime_needs_condition_arrays(data, scope):
            prefix = f'{scope}_match_'
            for attr_name, (element_type, default_value) in _IZOM_PROPUI_FREE_ENTRY_CONDITION_ARRAY_FIELDS.items():
                if attr_name.startswith(prefix):
                    data[attr_name] = _izom_propui_free_snapshot_typed_array_value(
                        getattr(entry, attr_name),
                        element_type,
                        default_value,
                    )

    use_value_labels = bool(data.get('use_value_labels', False))
    data['value_labels'] = [
        _izom_propui_free_snapshot_value_label(
            item,
            runtime=runtime,
            force_arrays=runtime and _izom_propui_free_entry_runtime_value_labels_need_arrays(data),
        )
        for item in entry.value_labels
    ] if (not runtime or use_value_labels) else []
    if limit_strings:
        _izom_propui_free_limit_entry_snapshot_strings(data)
    return data


def izom_propui_free_snapshot_entries(params, *, limit_strings=True, runtime=False):
    return [
        _izom_propui_free_snapshot_entry(item, limit_strings=limit_strings, runtime=runtime)
        for item in params.izom_propui_free_entries
    ]


def izom_propui_free_snapshot_runtime_entries(params):
    return izom_propui_free_snapshot_entries(params, limit_strings=False, runtime=True)

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
