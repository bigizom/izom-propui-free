# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import izom_propui_free_log_recovered
import math

from .constants import (
    IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
    IZOM_PROPUI_FREE_ARRAY_SIZE_MIN,
    IZOM_PROPUI_FREE_ARRAY_SUBTYPE_ITEMS,
)

_IZOM_PROPUI_FREE_FLOAT_ARRAY_STORAGE_DEFAULT = (1.0,) * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)
_IZOM_PROPUI_FREE_INT_ARRAY_STORAGE_DEFAULT = (0,) * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)
_IZOM_PROPUI_FREE_BOOL_ARRAY_STORAGE_DEFAULT = (False,) * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)
_IZOM_PROPUI_FREE_ARRAY_ELEMENT_TYPES = {'FLOAT', 'INT', 'BOOL'}
_IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE = int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)

_IZOM_PROPUI_FREE_ARRAY_SUBTYPE_META = {
    'COLOR': {'default_size': 4, 'ui_subtype': 'COLOR'},
    'COLOR_GAMMA': {'default_size': 4, 'ui_subtype': 'COLOR_GAMMA'},
    'TRANSLATION': {'default_size': 3, 'ui_subtype': 'TRANSLATION'},
    'DIRECTION': {'default_size': 3, 'ui_subtype': 'DIRECTION'},
    'VELOCITY': {'default_size': 3, 'ui_subtype': 'VELOCITY'},
    'ACCELERATION': {'default_size': 3, 'ui_subtype': 'ACCELERATION'},
    'EULER': {'default_size': 3, 'ui_subtype': 'EULER'},
    'QUATERNION': {'default_size': 4, 'ui_subtype': 'QUATERNION'},
    'XYZ': {'default_size': 3, 'ui_subtype': 'XYZ'},
    'AXISANGLE': {'default_size': 4, 'ui_subtype': 'AXISANGLE'},
    'NONE': {'default_size': 4, 'ui_subtype': 'NONE'},
}

_IZOM_PROPUI_FREE_ARRAY_VALID_SUBTYPES = {
    str(identifier or '').strip().upper() or 'NONE'
    for identifier, _label, _description in IZOM_PROPUI_FREE_ARRAY_SUBTYPE_ITEMS
}

def _izom_propui_free_safe_float(value, default=1.0):
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        result = float(default)
    if not math.isfinite(result):
        result = float(default)
    return result

def _izom_propui_free_safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        return int(default)

def _izom_propui_free_safe_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return bool(default)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {'true', '1', 'yes', 'on'}:
            return True
        if normalized in {'false', '0', 'no', 'off', ''}:
            return False
        return bool(default)
    try:
        return bool(value)
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        return bool(default)

def izom_propui_free_normalize_array_element_type(element_type, default='FLOAT'):
    normalized_default = str(default or 'FLOAT').strip().upper() or 'FLOAT'
    if normalized_default not in _IZOM_PROPUI_FREE_ARRAY_ELEMENT_TYPES:
        normalized_default = 'FLOAT'
    normalized = str(element_type or normalized_default).strip().upper() or normalized_default
    if normalized in _IZOM_PROPUI_FREE_ARRAY_ELEMENT_TYPES:
        return normalized
    return normalized_default

def izom_propui_free_array_storage_default(element_type='FLOAT'):
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type)
    if normalized_element_type == 'INT':
        return _IZOM_PROPUI_FREE_INT_ARRAY_STORAGE_DEFAULT
    if normalized_element_type == 'BOOL':
        return _IZOM_PROPUI_FREE_BOOL_ARRAY_STORAGE_DEFAULT
    return _IZOM_PROPUI_FREE_FLOAT_ARRAY_STORAGE_DEFAULT

def izom_propui_free_normalize_float_array_subtype(subtype, default='NONE'):
    normalized_default = str(default or 'NONE').strip().upper() or 'NONE'
    normalized = str(subtype or normalized_default).strip().upper() or normalized_default
    if normalized in _IZOM_PROPUI_FREE_ARRAY_VALID_SUBTYPES:
        return normalized
    return normalized_default

def izom_propui_free_normalize_array_subtype(subtype, element_type='FLOAT', default='NONE'):
    if izom_propui_free_normalize_array_element_type(element_type, 'FLOAT') != 'FLOAT':
        return 'NONE'
    return izom_propui_free_normalize_float_array_subtype(subtype, default)

def izom_propui_free_array_subtype_meta(subtype='NONE'):
    normalized = izom_propui_free_normalize_float_array_subtype(subtype)
    return _IZOM_PROPUI_FREE_ARRAY_SUBTYPE_META.get(normalized, _IZOM_PROPUI_FREE_ARRAY_SUBTYPE_META['NONE'])

def izom_propui_free_array_default_size(subtype='NONE', element_type='FLOAT'):
    normalized_subtype = izom_propui_free_normalize_array_subtype(subtype, element_type, 'NONE')
    return int(izom_propui_free_array_subtype_meta(normalized_subtype).get('default_size', 4) or 4)

def izom_propui_free_normalize_array_size(size, subtype='NONE', element_type='FLOAT', default=None):
    fallback = default
    if fallback is None:
        fallback = izom_propui_free_array_default_size(subtype, element_type)
    try:
        resolved = int(size)
    except (TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        resolved = int(fallback)
    return max(int(IZOM_PROPUI_FREE_ARRAY_SIZE_MIN), min(int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX), resolved))

def _izom_propui_free_array_label_seed(subtype='NONE'):
    normalized_subtype = izom_propui_free_normalize_float_array_subtype(subtype)
    if normalized_subtype == 'NONE':
        return ('1', '2', '3', '4')
    if normalized_subtype in {'COLOR', 'COLOR_GAMMA'}:
        return ('R', 'G', 'B', 'A')
    if normalized_subtype == 'QUATERNION':
        return ('W', 'X', 'Y', 'Z')
    if normalized_subtype == 'AXISANGLE':
        return ('ANGLE', 'X', 'Y', 'Z')
    return ('X', 'Y', 'Z', 'W')

def izom_propui_free_array_labels(subtype='NONE', *, size=None, element_type='FLOAT'):
    resolved_size = izom_propui_free_normalize_array_size(size, subtype, element_type)
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type, 'FLOAT')
    if normalized_element_type != 'FLOAT':
        return tuple(str(index + 1) for index in range(resolved_size))
    normalized_subtype = izom_propui_free_normalize_array_subtype(subtype, element_type, 'NONE')
    labels: list[str] = list(_izom_propui_free_array_label_seed(normalized_subtype))
    while len(labels) < resolved_size:
        labels.append(str(len(labels) + 1))
    return tuple(labels[:resolved_size])

def izom_propui_free_array_ui_subtype(subtype='NONE'):
    return str(izom_propui_free_array_subtype_meta(subtype).get('ui_subtype', 'NONE') or 'NONE')

def izom_propui_free_array_value_kind(element_type='FLOAT', subtype='NONE'):
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type)
    if normalized_element_type == 'INT':
        return 'INT_ARRAY'
    if normalized_element_type == 'BOOL':
        return 'BOOL_ARRAY'
    normalized_subtype = izom_propui_free_normalize_array_subtype(subtype, normalized_element_type, 'NONE')
    return 'COLOR' if normalized_subtype in {'COLOR', 'COLOR_GAMMA'} else 'VECTOR'

def _izom_propui_free_array_component(value, element_type, default):
    normalized_element_type = (
        element_type
        if isinstance(element_type, str) and element_type in _IZOM_PROPUI_FREE_ARRAY_ELEMENT_TYPES
        else izom_propui_free_normalize_array_element_type(element_type)
    )
    if normalized_element_type == 'INT':
        return _izom_propui_free_safe_int(value, default)
    if normalized_element_type == 'BOOL':
        return _izom_propui_free_safe_bool(value, default)
    return _izom_propui_free_safe_float(value, default)

def izom_propui_free_normalize_array_storage(value, element_type='FLOAT', default=None):
    if isinstance(value, tuple) and len(value) == _IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE:
        return value
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type)
    default_storage = tuple(default or izom_propui_free_array_storage_default(normalized_element_type))
    normalized_default = []
    for index in range(_IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE):
        fallback_value = default_storage[index] if index < len(default_storage) else izom_propui_free_array_storage_default(normalized_element_type)[index]
        normalized_default.append(_izom_propui_free_array_component(fallback_value, normalized_element_type, fallback_value))

    try:
        items = list(value)
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        items = []

    normalized = []
    for index in range(_IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE):
        fallback = normalized_default[index]
        if index < len(items):
            normalized.append(_izom_propui_free_array_component(items[index], normalized_element_type, fallback))
        else:
            normalized.append(fallback)
    return tuple(normalized[:_IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE])

def izom_propui_free_array_visible_value(value, element_type='FLOAT', subtype='NONE', *, size=None, default=None):
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type)
    resolved_size = izom_propui_free_normalize_array_size(size, subtype, normalized_element_type)
    if isinstance(value, tuple) and len(value) == _IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE:
        return tuple(value[:resolved_size])

    if isinstance(default, tuple) and len(default) == _IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE:
        default_storage = default
    else:
        default_storage = tuple(
            default or izom_propui_free_array_storage_default(normalized_element_type)
        )

    try:
        items = list(value)
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        items = []

    normalized = []
    for index in range(resolved_size):
        fallback = (
            default_storage[index]
            if index < len(default_storage)
            else izom_propui_free_array_storage_default(normalized_element_type)[index]
        )
        normalized.append(
            _izom_propui_free_array_component(
                items[index] if index < len(items) else fallback,
                normalized_element_type,
                fallback,
            )
        )
    return tuple(normalized)

def izom_propui_free_array_storage_from_visible(value, element_type='FLOAT', subtype='NONE', *, size=None, previous=None, default=None):
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type)
    resolved_size = izom_propui_free_normalize_array_size(size, subtype, normalized_element_type)
    previous_storage = izom_propui_free_normalize_array_storage(previous, normalized_element_type, default=default)
    default_storage = izom_propui_free_normalize_array_storage(default, normalized_element_type, default=previous_storage)
    visible_default = izom_propui_free_array_visible_value(
        default_storage,
        normalized_element_type,
        subtype,
        size=resolved_size,
        default=default_storage,
    )
    try:
        visible_items = list(value)
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        visible_items = []

    result = list(previous_storage)
    for index in range(resolved_size):
        fallback = visible_default[index] if index < len(visible_default) else default_storage[index]
        if index < len(visible_items):
            result[index] = _izom_propui_free_array_component(visible_items[index], normalized_element_type, fallback)
        else:
            result[index] = fallback
    return tuple(result[:_IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE])

def izom_propui_free_remap_array_storage(value, element_type, old_subtype, new_subtype, *, size=None, default=None):
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type)
    old_normalized = izom_propui_free_normalize_float_array_subtype(old_subtype)
    new_normalized = izom_propui_free_normalize_float_array_subtype(new_subtype)
    resolved_size = izom_propui_free_normalize_array_size(size, new_normalized, normalized_element_type)
    if old_normalized == new_normalized:
        return izom_propui_free_normalize_array_storage(value, normalized_element_type, default=default)

    old_storage = izom_propui_free_normalize_array_storage(value, normalized_element_type, default=default)
    old_labels = izom_propui_free_array_labels(old_normalized, size=resolved_size, element_type=normalized_element_type)
    new_labels = izom_propui_free_array_labels(new_normalized, size=resolved_size, element_type=normalized_element_type)
    old_visible = izom_propui_free_array_visible_value(
        old_storage,
        normalized_element_type,
        old_normalized,
        size=resolved_size,
        default=default,
    )

    default_storage = izom_propui_free_normalize_array_storage(default, normalized_element_type, default=old_storage)
    default_visible = izom_propui_free_array_visible_value(
        default_storage,
        normalized_element_type,
        new_normalized,
        size=resolved_size,
        default=default_storage,
    )

    old_map = {
        label: old_visible[index]
        for index, label in enumerate(old_labels)
        if index < len(old_visible)
    }
    result = list(default_storage)
    for index, label in enumerate(new_labels):
        if label in old_map:
            result[index] = old_map[label]
        elif index < len(default_visible):
            result[index] = default_visible[index]
    return tuple(result[:_IZOM_PROPUI_FREE_ARRAY_STORAGE_SIZE])

def izom_propui_free_float_array_subtype_meta(subtype='NONE'):
    normalized = izom_propui_free_normalize_float_array_subtype(subtype)
    return {
        'visible_size': izom_propui_free_array_default_size(normalized, 'FLOAT'),
        'ui_subtype': izom_propui_free_array_ui_subtype(normalized),
        'value_kind': izom_propui_free_array_value_kind('FLOAT', normalized),
        'labels': izom_propui_free_array_labels(normalized, size=izom_propui_free_array_default_size(normalized, 'FLOAT')),
    }

def izom_propui_free_float_array_visible_size(subtype='NONE'):
    return int(izom_propui_free_float_array_subtype_meta(subtype)['visible_size'])

def izom_propui_free_float_array_ui_subtype(subtype='NONE'):
    return str(izom_propui_free_float_array_subtype_meta(subtype)['ui_subtype'])
