# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .runtime_common import (
    IZOM_PROPUI_FREE_INTERNAL_PROP_IDS,
    _izom_propui_free_kind_from_idprop,
    _izom_propui_free_sequence_value,
    izom_propui_free_log_recovered,
    izom_propui_free_values_match,
)

def _izom_propui_free_should_skip_import_key(key):
    return key in IZOM_PROPUI_FREE_INTERNAL_PROP_IDS

def _izom_propui_free_detect_array_element_type(value, ui_data=None):
    sequence = _izom_propui_free_sequence_value(value)
    if sequence is None:
        return 'FLOAT'
    typecode = str(getattr(value, 'typecode', '') or '').strip().lower()
    if typecode == 'b':
        return 'BOOL'
    if typecode == 'i':
        return 'INT'
    if all(isinstance(item, bool) for item in sequence):
        return 'BOOL'
    if all(isinstance(item, int) and not isinstance(item, bool) for item in sequence):
        return 'INT'
    return 'FLOAT'

def _izom_propui_free_detect_supported_prop_type(value, ui_data=None):
    value_kind = _izom_propui_free_kind_from_idprop(value, ui_data)
    if value_kind == 'BOOL':
        return 'BOOL'
    if value_kind == 'INT':
        return 'INT'
    if value_kind == 'FLOAT':
        return 'FLOAT'
    if value_kind in {'BOOL_ARRAY', 'INT_ARRAY', 'VECTOR', 'COLOR'}:
        return 'ARRAY'
    return None

def _izom_propui_free_idprop_runtime_type(value):
    value_kind = _izom_propui_free_kind_from_idprop(value)
    if value_kind == 'BOOL':
        return 'BOOL'
    if value_kind == 'INT':
        return 'INT'
    if value_kind == 'FLOAT':
        return 'FLOAT'
    if value_kind == 'BOOL_ARRAY':
        return 'BOOL_ARRAY'
    if value_kind == 'INT_ARRAY':
        return 'INT_ARRAY'
    if value_kind in {'VECTOR', 'COLOR'}:
        return 'VECTOR'
    if value_kind == 'NONE':
        return 'NONE'
    return type(value).__name__


def _izom_propui_free_value_matches_generic(current_value, desired_value):
    current_type = _izom_propui_free_idprop_runtime_type(current_value)
    desired_type = _izom_propui_free_idprop_runtime_type(desired_value)
    if current_type != desired_type:
        return False
    if desired_type == 'FLOAT':
        try:
            return abs(float(current_value) - float(desired_value)) <= 1e-9
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
            )
            return False
    if desired_type in {'VECTOR', 'COLOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        return izom_propui_free_values_match(current_value, desired_value, desired_type)
    return current_value == desired_value

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
