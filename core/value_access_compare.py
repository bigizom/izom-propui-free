# SPDX-License-Identifier: GPL-3.0-or-later

import ast
import json

from .diagnostics import izom_propui_free_log_recovered
from .float_arrays import _izom_propui_free_safe_float
from .value_access_common import (
    _IZOM_PROPUI_FREE_FLOAT_TOLERANCE,
    izom_propui_free_normalize_value_kind,
)

def _izom_propui_free_sequence_value(value):
    if isinstance(value, (str, bytes, bytearray, dict)):
        return None
    if callable(getattr(value, 'to_dict', None)):
        return None
    try:
        items = list(value)
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        return None
    return items


def _izom_propui_free_kind_from_idprop(value, ui_data=None):
    if isinstance(value, bool):
        return 'BOOL'
    if isinstance(value, int):
        return 'INT'
    if isinstance(value, float):
        return 'FLOAT'
    sequence = _izom_propui_free_sequence_value(value)
    if sequence is not None:
        typecode = str(getattr(value, 'typecode', '') or '').strip().lower()
        if typecode == 'b':
            return 'BOOL_ARRAY'
        if typecode == 'i':
            return 'INT_ARRAY'
        if all(isinstance(item, bool) for item in sequence):
            return 'BOOL_ARRAY'
        if all(isinstance(item, int) and not isinstance(item, bool) for item in sequence):
            return 'INT_ARRAY'
        if not all(isinstance(item, (int, float, bool)) for item in sequence):
            return 'NONE'
        subtype = str((ui_data or {}).get('subtype', '') or '').strip().upper()
        return 'COLOR' if subtype.startswith('COLOR') else 'VECTOR'
    return 'NONE'


def _izom_propui_free_normalize_sequence(value):
    items = _izom_propui_free_sequence_value(value)
    if items is None:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                izom_propui_free_log_recovered(
                    category='Core',
                    exception=exc,
                )
                try:
                    parsed = ast.literal_eval(value)
                except (TypeError, ValueError, SyntaxError) as exc:
                    izom_propui_free_log_recovered(
                        category='Core',
                        exception=exc,
                    )
                    return ()
            items = _izom_propui_free_sequence_value(parsed)
    if items is None:
        return ()
    normalized = []
    for item in items:
        if isinstance(item, bool):
            normalized.append(1.0 if item else 0.0)
        elif isinstance(item, (int, float)):
            normalized.append(_izom_propui_free_safe_float(item, 0.0))
        else:
            return ()
    return tuple(normalized)

def _izom_propui_free_normalize_int_sequence(value):
    items = _izom_propui_free_sequence_value(value)
    if items is None:
        return ()
    normalized = []
    for item in items:
        if isinstance(item, bool):
            normalized.append(1 if item else 0)
        elif isinstance(item, (int, float)):
            normalized.append(int(item))
        else:
            return ()
    return tuple(normalized)

def _izom_propui_free_normalize_bool_sequence(value):
    items = _izom_propui_free_sequence_value(value)
    if items is None:
        return ()
    return tuple(bool(item) for item in items)

def _izom_propui_free_normalize_color(value, default=(1.0, 1.0, 1.0, 1.0)):
    normalized_default = _izom_propui_free_normalize_sequence(default)
    if len(normalized_default) < 4:
        normalized_default = tuple(list(normalized_default[:3]) + [1.0])
    else:
        normalized_default = tuple(normalized_default[:4])

    sequence = _izom_propui_free_normalize_sequence(value)
    if len(sequence) == 3:
        return tuple(list(sequence) + [1.0])
    if len(sequence) >= 4:
        return tuple(sequence[:4])
    return normalized_default

def izom_propui_free_normalize_comparable_value(value, value_kind):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind)
    if normalized_kind == 'BOOL':
        return bool(value)
    if normalized_kind == 'INT':
        try:
            return int(value)
        except (TypeError, ValueError, OverflowError) as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
            )
            return 0
    if normalized_kind == 'FLOAT':
        return _izom_propui_free_safe_float(value, 0.0)
    if normalized_kind == 'VECTOR':
        return _izom_propui_free_normalize_sequence(value)
    if normalized_kind == 'COLOR':
        return _izom_propui_free_normalize_color(value, (1.0, 1.0, 1.0, 1.0))
    if normalized_kind == 'INT_ARRAY':
        return _izom_propui_free_normalize_int_sequence(value)
    if normalized_kind == 'BOOL_ARRAY':
        return _izom_propui_free_normalize_bool_sequence(value)
    return value

def izom_propui_free_values_match(current_value, expected_value, value_kind):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind)
    current = izom_propui_free_normalize_comparable_value(current_value, normalized_kind)
    expected = izom_propui_free_normalize_comparable_value(expected_value, normalized_kind)
    if normalized_kind == 'FLOAT':
        return abs(float(current) - float(expected)) <= _IZOM_PROPUI_FREE_FLOAT_TOLERANCE
    if normalized_kind in {'VECTOR', 'COLOR'}:
        if len(current) != len(expected):
            return False
        return all(abs(float(a) - float(b)) <= _IZOM_PROPUI_FREE_FLOAT_TOLERANCE for a, b in zip(current, expected))
    return current == expected

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
