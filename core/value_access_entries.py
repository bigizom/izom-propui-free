# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .diagnostics import izom_propui_free_log_recovered
from .constants import izom_propui_free_is_managed_prop_type
from .float_arrays import (
    izom_propui_free_array_value_kind,
    izom_propui_free_array_visible_value,
    izom_propui_free_normalize_array_element_type,
    izom_propui_free_normalize_array_size,
    izom_propui_free_normalize_array_storage,
    izom_propui_free_normalize_array_subtype,
)
from .value_access_common import (
    _izom_propui_free_entry_value,
    izom_propui_free_custom_component_value_kind,
    izom_propui_free_entry_array_component_labels,
    izom_propui_free_normalize_value_kind,
)
from .value_access_compare import (
    _izom_propui_free_sequence_value,
    izom_propui_free_normalize_comparable_value,
)


_IZOM_PROPUI_FREE_VALUE_KIND_MEMO = {}
_IZOM_PROPUI_FREE_COMPONENT_META_MEMO = {}
_IZOM_PROPUI_FREE_VALUE_KIND_MEMO_FIELDS = (
    'prop_type',
    'value_kind',
    'array_element_type',
    'float_array_subtype',
    'array_size',
)
_IZOM_PROPUI_FREE_COMPONENT_META_MEMO_FIELDS = _IZOM_PROPUI_FREE_VALUE_KIND_MEMO_FIELDS


def _izom_propui_free_entry_memo_key(entry, default, fields):
    if not isinstance(entry, dict):
        pointer = getattr(entry, 'as_pointer', None)
        if callable(pointer):
            # Collection iteration creates short-lived RNA wrappers. Their
            # Python ids can be reused by the very next, unrelated entry.
            # Keep only the underlying RNA identity; lifecycle invalidation
            # clears these keys when Blender replaces the owning data.
            return ('rna', int(pointer()), default)
    runtime_token = entry.get('_value_access_memo_token') if isinstance(entry, dict) else None
    if runtime_token is not None:
        return ('dict-token', runtime_token, default, id(fields))
    return (
        'dict',
        default,
        tuple((field_name, _izom_propui_free_entry_value(entry, field_name, None)) for field_name in fields),
    )

def izom_propui_free_clear_value_access_memo():
    _IZOM_PROPUI_FREE_VALUE_KIND_MEMO.clear()
    _IZOM_PROPUI_FREE_COMPONENT_META_MEMO.clear()

def izom_propui_free_entry_component_meta(entry, default='FLOAT'):
    memo_key = _izom_propui_free_entry_memo_key(entry, default, _IZOM_PROPUI_FREE_COMPONENT_META_MEMO_FIELDS)
    cached = _IZOM_PROPUI_FREE_COMPONENT_META_MEMO.get(memo_key)
    if cached is not None:
        return cached
    value_kind = izom_propui_free_entry_value_kind(entry, default)
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind, default)
    component_kind = izom_propui_free_custom_component_value_kind(normalized_kind, none_value=None)
    prop_type = str(_izom_propui_free_entry_value(entry, 'prop_type', default) or default).strip().upper() or default
    element_type = 'FLOAT'
    subtype = 'NONE'
    size = 0

    if normalized_kind in {'VECTOR', 'COLOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        if prop_type == 'ARRAY':
            element_type = izom_propui_free_entry_array_element_type(entry, 'FLOAT')
            subtype = izom_propui_free_entry_array_subtype(entry, 'NONE')
            size = izom_propui_free_entry_array_size(entry, 4)
        else:
            if normalized_kind == 'COLOR':
                element_type = 'FLOAT'
                subtype = 'COLOR'
                size = 4
            elif normalized_kind == 'VECTOR':
                element_type = 'FLOAT'
                subtype = 'NONE'
                size = 3
            elif normalized_kind == 'INT_ARRAY':
                element_type = 'INT'
                size = 4
            elif normalized_kind == 'BOOL_ARRAY':
                element_type = 'BOOL'
                size = 4

    if normalized_kind == 'COLOR' and size <= 0:
        size = 4
        subtype = 'COLOR'
    elif normalized_kind == 'VECTOR' and size <= 0:
        size = 3
    elif normalized_kind in {'INT_ARRAY', 'BOOL_ARRAY'} and size <= 0:
        size = 4

    labels = ()
    if size > 0:
        size = izom_propui_free_normalize_array_size(size, subtype, element_type, default=size)
        labels = izom_propui_free_entry_array_component_labels(
            entry,
            subtype,
            size=size,
            element_type=element_type,
        )

    result = {
        'value_kind': normalized_kind,
        'component_kind': component_kind,
        'supported': component_kind is not None,
        'element_type': element_type,
        'subtype': subtype,
        'size': size,
        'labels': labels,
    }
    _IZOM_PROPUI_FREE_COMPONENT_META_MEMO[memo_key] = result
    return result

def izom_propui_free_component_value(value, value_kind, component_index, default=None):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind)
    component_kind = izom_propui_free_custom_component_value_kind(normalized_kind, none_value=None)
    if component_kind is None:
        return default

    normalized_value = izom_propui_free_normalize_comparable_value(value, normalized_kind)
    components = _izom_propui_free_sequence_value(normalized_value) or []
    if not components:
        if component_kind == 'BOOL':
            return False if default is None else bool(default)
        return 0 if component_kind == 'INT' and default is None else (0.0 if default is None else default)

    try:
        resolved_index = int(component_index)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        resolved_index = 0
    resolved_index = max(0, min(len(components) - 1, resolved_index))
    component_value = components[resolved_index]
    if component_kind == 'BOOL':
        return bool(component_value)
    if component_kind == 'INT':
        try:
            return int(component_value)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
            )
            return int(default or 0)
    try:
        return float(component_value)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        return float(default or 0.0)

def izom_propui_free_is_managed_entry(entry):
    prop_type = str(_izom_propui_free_entry_value(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    return izom_propui_free_is_managed_prop_type(prop_type)

def izom_propui_free_entry_slider_control_available(entry, value_kind=None, *, uses_component_draw_mode=True):
    kind = izom_propui_free_normalize_value_kind(
        value_kind if value_kind is not None else izom_propui_free_entry_value_kind(entry, 'NONE'),
        'NONE',
    )
    if not (
        kind in {'FLOAT', 'INT'}
        or (kind in {'VECTOR', 'COLOR', 'INT_ARRAY'} and bool(uses_component_draw_mode))
    ):
        return False

    prop_type = str(_izom_propui_free_entry_value(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    if izom_propui_free_is_managed_prop_type(prop_type):
        return True
    return False

def izom_propui_free_entry_array_element_type(entry, default='FLOAT'):
    return izom_propui_free_normalize_array_element_type(
        _izom_propui_free_entry_value(entry, 'array_element_type', default),
        default,
    )

def izom_propui_free_entry_array_subtype(entry, default='NONE'):
    return izom_propui_free_normalize_array_subtype(
        _izom_propui_free_entry_value(entry, 'float_array_subtype', default),
        izom_propui_free_entry_array_element_type(entry, 'FLOAT'),
        default,
    )

def izom_propui_free_entry_array_size(entry, default=None):
    element_type = izom_propui_free_entry_array_element_type(entry, 'FLOAT')
    subtype = izom_propui_free_entry_array_subtype(entry, 'NONE')
    fallback = _izom_propui_free_entry_value(entry, 'array_size', default)
    return izom_propui_free_normalize_array_size(fallback, subtype, element_type, default=default)

def izom_propui_free_array_field_element_type(field_name, default='FLOAT'):
    text = str(field_name or '').strip()
    if text.endswith('_int_array'):
        return 'INT'
    if text.endswith('_bool_array'):
        return 'BOOL'
    return izom_propui_free_normalize_array_element_type(default, 'FLOAT')

def izom_propui_free_entry_array_field_name(field_root, element_type='FLOAT'):
    text = str(field_root or '').strip()
    if text.endswith('_float_array') or text.endswith('_int_array') or text.endswith('_bool_array'):
        return text
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type, 'FLOAT')
    suffix = 'float_array'
    if normalized_element_type == 'INT':
        suffix = 'int_array'
    elif normalized_element_type == 'BOOL':
        suffix = 'bool_array'
    return f"{text}_{suffix}"

def _izom_propui_free_entry_array_value_kind(entry, default='FLOAT'):
    element_type = izom_propui_free_entry_array_element_type(entry, default)
    subtype = izom_propui_free_entry_array_subtype(entry, 'NONE')
    return izom_propui_free_array_value_kind(element_type, subtype)

def izom_propui_free_entry_float_array_subtype(entry, default='NONE'):
    return izom_propui_free_entry_array_subtype(entry, default)

def izom_propui_free_entry_array_visible_value(entry, field_root='default', *, default=None):
    element_type = izom_propui_free_entry_array_element_type(entry, 'FLOAT')
    field_name = izom_propui_free_entry_array_field_name(field_root, element_type)
    field_element_type = izom_propui_free_array_field_element_type(field_name, element_type)
    subtype = izom_propui_free_entry_array_subtype(entry, 'NONE')
    size = izom_propui_free_entry_array_size(entry)
    storage_default = izom_propui_free_normalize_array_storage(
        default if default is not None else _izom_propui_free_entry_value(entry, field_name, ()),
        field_element_type,
    )
    return izom_propui_free_array_visible_value(
        _izom_propui_free_entry_value(entry, field_name, storage_default),
        field_element_type,
        subtype,
        size=size,
        default=storage_default,
    )

def izom_propui_free_entry_value_kind(entry, default='FLOAT'):
    memo_key = _izom_propui_free_entry_memo_key(entry, default, _IZOM_PROPUI_FREE_VALUE_KIND_MEMO_FIELDS)
    cached = _IZOM_PROPUI_FREE_VALUE_KIND_MEMO.get(memo_key)
    if cached is not None:
        return cached
    prop_type = str(_izom_propui_free_entry_value(entry, 'prop_type', default) or default).strip().upper() or default
    if prop_type in {'FLOAT', 'INT', 'BOOL'}:
        result = prop_type
    elif prop_type == 'ARRAY':
        result = _izom_propui_free_entry_array_value_kind(entry, 'FLOAT')
    elif prop_type == 'TEXT':
        result = 'TEXT'
    else:
        result = izom_propui_free_normalize_value_kind(default, 'FLOAT')
    _IZOM_PROPUI_FREE_VALUE_KIND_MEMO[memo_key] = result
    return result


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
