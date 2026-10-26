# SPDX-License-Identifier: GPL-3.0-or-later

from .value_access import (
    _izom_propui_free_entry_value,
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_field_name,
    izom_propui_free_entry_array_visible_value,
    izom_propui_free_normalize_comparable_value,
    izom_propui_free_normalize_value_kind,
)
from .value_labels_common import (
    _izom_propui_free_is_numeric_type,
    _izom_propui_free_value_label_match_mode,
)


def _izom_propui_free_numeric_rule_matches_value(compare_value, threshold, value_kind, *, match_mode='GREATER', range_threshold=None):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind, 'FLOAT')
    mode = _izom_propui_free_value_label_match_mode(match_mode, 'GREATER')
    try:
        if normalized_kind == 'INT':
            current = int(compare_value)
            primary = int(threshold if threshold is not None else 0)
            secondary = int(range_threshold if range_threshold is not None else primary)
        else:
            current = float(compare_value)
            primary = float(threshold if threshold is not None else 0.0)
            secondary = float(range_threshold if range_threshold is not None else primary)
    except (TypeError, ValueError):
        return False

    if mode == 'EQUAL':
        if normalized_kind == 'INT':
            return current == primary
        return abs(current - primary) <= 1e-6
    if mode == 'LESS':
        return current <= primary
    if mode == 'RANGE':
        low = min(primary, secondary)
        high = max(primary, secondary)
        return low <= current <= high
    return current >= primary


def _izom_propui_free_rule_compare_value(getter, field_root, value_kind, *, fallback_name='threshold', default_value=None, reference_entry=None):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind)
    if _izom_propui_free_is_numeric_type(normalized_kind):
        return _izom_propui_free_runtime_threshold_value(
            getter,
            field_root,
            normalized_kind,
            fallback_name=fallback_name,
            default_value=default_value,
        )
    if normalized_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        field_name = f"{field_root}_float_array"
        if normalized_kind == 'INT_ARRAY':
            field_name = f"{field_root}_int_array"
        elif normalized_kind == 'BOOL_ARRAY':
            field_name = f"{field_root}_bool_array"
        if isinstance(reference_entry, dict) and str(reference_entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper() == 'ARRAY':
            reference_element_type = izom_propui_free_entry_array_element_type(reference_entry, 'FLOAT')
            field_name = izom_propui_free_entry_array_field_name(field_root, reference_element_type)
            field_value = getter(
                field_name,
                default_value if default_value is not None else reference_entry.get(izom_propui_free_entry_array_field_name('default', reference_element_type), ()),
            )
            return izom_propui_free_entry_array_visible_value(
                dict(reference_entry, **{field_name: field_value}),
                field_name,
                default=default_value,
            )
        return izom_propui_free_normalize_comparable_value(
            getter(field_name, default_value if default_value is not None else ()),
            normalized_kind,
        )
    return None


def _izom_propui_free_entry_compare_value(entry, value_kind, current_value=None):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind)
    if _izom_propui_free_is_numeric_type(normalized_kind):
        return _izom_propui_free_numeric_compare_value(entry, normalized_kind, current_value=current_value)
    if current_value is None:
        current_value = _izom_propui_free_entry_value(entry, '_current_value', None)
    if current_value is None:
        if normalized_kind == 'BOOL':
            current_value = _izom_propui_free_entry_value(entry, 'default_bool', False)
        elif normalized_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
            if str(_izom_propui_free_entry_value(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() == 'ARRAY':
                current_value = izom_propui_free_entry_array_visible_value(entry, 'default')
            elif normalized_kind == 'INT_ARRAY':
                current_value = _izom_propui_free_entry_value(entry, 'default_int_array', ())
            elif normalized_kind == 'BOOL_ARRAY':
                current_value = _izom_propui_free_entry_value(entry, 'default_bool_array', ())
            else:
                current_value = _izom_propui_free_entry_value(entry, 'default_float_array', (1.0, 1.0, 1.0, 1.0))
        else:
            current_value = _izom_propui_free_entry_value(entry, 'default_text', '')
    elif normalized_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'} and str(_izom_propui_free_entry_value(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() == 'ARRAY':
        current_field = izom_propui_free_entry_array_field_name(
            'default',
            izom_propui_free_entry_array_element_type(entry, 'FLOAT'),
        )
        current_value = izom_propui_free_entry_array_visible_value(
            dict(entry, **{current_field: current_value}) if isinstance(entry, dict) else entry,
            current_field,
            default=current_value,
        )
    return izom_propui_free_normalize_comparable_value(current_value, normalized_kind)

def _izom_propui_free_runtime_threshold_value(getter, field_root, prop_type, *, fallback_name='threshold', default_value=None):
    if default_value is None:
        default_value = 0 if prop_type == 'INT' else 0.0

    int_name = f"{field_root}_int"
    float_name = f"{field_root}_float"

    try:
        primary_value = getter(int_name, None) if prop_type == 'INT' else getter(float_name, None)
    except (AttributeError, TypeError, ValueError):
        primary_value = None

    try:
        secondary_value = getter(float_name, None) if prop_type == 'INT' else getter(int_name, None)
    except (AttributeError, TypeError, ValueError):
        secondary_value = None

    if primary_value is None:
        primary_value = getter(fallback_name, default_value)

    if prop_type == 'INT':
        try:
            normalized_primary = int(primary_value)
        except (TypeError, ValueError):
            normalized_primary = int(default_value)
        if normalized_primary == 0 and secondary_value is not None:
            try:
                if abs(float(secondary_value)) > 1e-6:
                    return int(round(float(secondary_value)))
            except (TypeError, ValueError):
                return normalized_primary
        return normalized_primary

    try:
        normalized_primary = float(primary_value)
    except (TypeError, ValueError):
        normalized_primary = float(default_value)
    if abs(normalized_primary) <= 1e-6 and secondary_value is not None:
        try:
            if abs(float(secondary_value)) > 1e-6:
                return float(secondary_value)
        except (TypeError, ValueError):
            return normalized_primary
    return normalized_primary


def _izom_propui_free_rule_compare_range_value(getter, field_root, value_kind, *, default_value=None):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind)
    if not _izom_propui_free_is_numeric_type(normalized_kind):
        return None
    if default_value is None:
        default_value = 0 if normalized_kind == 'INT' else 0.0
    field_name = f"{field_root}_range_{'int' if normalized_kind == 'INT' else 'float'}"
    try:
        raw_value = getter(field_name, default_value)
    except (TypeError, ValueError):
        raw_value = default_value
    try:
        return int(raw_value) if normalized_kind == 'INT' else float(raw_value)
    except (TypeError, ValueError):
        return default_value


def _izom_propui_free_numeric_entry_low(entry, prop_type):
    try:
        if prop_type == 'INT':
            return min(
                int(_izom_propui_free_entry_value(entry, 'min_int', 0)),
                int(_izom_propui_free_entry_value(entry, 'max_int', 5)),
            )
        return min(
            float(_izom_propui_free_entry_value(entry, 'min_float', 0.0)),
            float(_izom_propui_free_entry_value(entry, 'max_float', 1.0)),
        )
    except (TypeError, ValueError):
        return 0 if prop_type == 'INT' else 0.0


def _izom_propui_free_numeric_entry_high(entry, prop_type):
    try:
        if prop_type == 'INT':
            low = _izom_propui_free_numeric_entry_low(entry, prop_type)
            return max(
                low,
                int(_izom_propui_free_entry_value(entry, 'min_int', 0)),
                int(_izom_propui_free_entry_value(entry, 'max_int', low)),
            )
        low = _izom_propui_free_numeric_entry_low(entry, prop_type)
        return max(
            low,
            float(_izom_propui_free_entry_value(entry, 'min_float', 0.0)),
            float(_izom_propui_free_entry_value(entry, 'max_float', low)),
        )
    except (TypeError, ValueError):
        return _izom_propui_free_numeric_entry_low(entry, prop_type)


def _izom_propui_free_numeric_compare_value(entry, prop_type, current_value=None):
    if not _izom_propui_free_is_numeric_type(prop_type):
        return None

    if current_value is None:
        current_value = _izom_propui_free_entry_value(entry, '_current_value', None)
    if current_value is None:
        current_value = _izom_propui_free_entry_value(
            entry,
            'default_int' if prop_type == 'INT' else 'default_float',
            0 if prop_type == 'INT' else 0.0,
        )
    try:
        return int(current_value) if prop_type == 'INT' else float(current_value)
    except (TypeError, ValueError):
        return 0 if prop_type == 'INT' else 0.0



def _izom_propui_free_normalize_bool_state(raw_value, default='WHEN_TRUE'):
    return str(raw_value or default).strip().upper() or default

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
