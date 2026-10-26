# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .diagnostics import izom_propui_free_log_recovered
_IZOM_PROPUI_FREE_SUPPORTED_VALUE_KINDS = {
    'BOOL',
    'INT',
    'FLOAT',
    'BOOL_ARRAY',
    'INT_ARRAY',
    'VECTOR',
    'COLOR',
}
_IZOM_PROPUI_FREE_SCALAR_LABEL_LAYOUT_VALUE_KINDS = frozenset({
    'BOOL',
    'FLOAT',
    'INT',
})
_IZOM_PROPUI_FREE_FLOAT_TOLERANCE = 1e-6

def _izom_propui_free_entry_value(entry, name, default=None):
    if isinstance(entry, dict):
        return entry.get(name, default)
    return getattr(entry, name, default)

def izom_propui_free_normalize_value_kind(value_kind, default='NONE'):
    if isinstance(value_kind, str):
        if value_kind in _IZOM_PROPUI_FREE_SUPPORTED_VALUE_KINDS or value_kind in {'NONE', 'TEXT'}:
            return value_kind
    normalized = str(value_kind or default).strip().upper() or default
    if normalized in _IZOM_PROPUI_FREE_SUPPORTED_VALUE_KINDS or normalized in {'NONE', 'TEXT'}:
        return normalized
    return str(default or 'NONE').strip().upper() or 'NONE'

def izom_propui_free_is_numeric_value_kind(value_kind):
    if value_kind in {'FLOAT', 'INT'}:
        return True
    return izom_propui_free_normalize_value_kind(value_kind) in {'FLOAT', 'INT'}

def izom_propui_free_is_exact_match_value_kind(value_kind):
    if value_kind in {'VECTOR', 'COLOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        return True
    return izom_propui_free_normalize_value_kind(value_kind) in {'VECTOR', 'COLOR', 'INT_ARRAY', 'BOOL_ARRAY'}

def izom_propui_free_uses_scalar_label_layout(value_kind):
    return izom_propui_free_normalize_value_kind(value_kind) in _IZOM_PROPUI_FREE_SCALAR_LABEL_LAYOUT_VALUE_KINDS


def izom_propui_free_custom_component_value_kind(value_kind, *, none_value='NONE'):
    normalized_kind = izom_propui_free_normalize_value_kind(value_kind)
    if normalized_kind in {'VECTOR', 'COLOR'}:
        return 'FLOAT'
    if normalized_kind == 'INT_ARRAY':
        return 'INT'
    if normalized_kind == 'BOOL_ARRAY':
        return 'BOOL'
    return none_value

def izom_propui_free_entry_array_component_labels(entry, subtype='NONE', *, size=None, element_type='FLOAT'):
    try:
        resolved_size = int(size if size is not None else 4)
    except (TypeError, ValueError):
        resolved_size = 4
    return tuple('' for _index in range(max(0, resolved_size)))

def izom_propui_free_clamp_component_slot(component_slot, size, default=1):
    try:
        resolved = int(component_slot)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        resolved = int(default)
    try:
        limit = int(size)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        limit = int(default)
    if limit < 1:
        limit = 1
    return max(1, min(limit, resolved))

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
