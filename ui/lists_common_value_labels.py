# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.float_arrays import izom_propui_free_array_visible_value
from ..core.cache_state import izom_propui_free_cached_runtime_parent_lookup
from ..core.value_access_entries import izom_propui_free_entry_value_kind
from ..core.value_labels import (
    _izom_propui_free_is_numeric_type,
    _izom_propui_free_normalize_bool_state,
    _izom_propui_free_rule_kind_value,
)
from .helper_field_clamp_common import _izom_propui_free_editor_float_settings
from .helper_value_labels_source import (
    _izom_propui_free_entry_component_rule_info,
    _izom_propui_free_entry_uses_bool_value_bucket_scope,
    _izom_propui_free_value_label_source_info,
)
from .lists_common_base import _izom_propui_free_pointer


def _izom_propui_free_threshold_storage_value(*args, **kwargs):
    from .helper_value_labels_thresholds import (
        _izom_propui_free_threshold_storage_value as threshold_storage_value,
    )

    return threshold_storage_value(*args, **kwargs)


def _izom_propui_free_resolved_value_label_source_info(owner, active_propname, context=None):
    resolved = _izom_propui_free_value_label_source_info(owner, active_propname, context)
    if isinstance(resolved, dict):
        return dict(resolved)
    return {}


def _izom_propui_free_value_label_number_text(value, value_kind, params=None):
    try:
        if str(value_kind or '').strip().upper() == 'INT':
            return str(int(value))
        decimals, _step = _izom_propui_free_editor_float_settings(params)
        if int(decimals) <= 0:
            return str(int(round(float(value))))
        return f"{float(value):.{int(decimals)}f}"
    except (TypeError, ValueError):
        return '0'


def _izom_propui_free_entry_value(entry, field_name, default=None):
    if isinstance(entry, dict):
        return entry.get(field_name, default)
    try:
        return getattr(entry, field_name, default)
    except (AttributeError, TypeError, ValueError):
        return default


def _izom_propui_free_value_label_match_mode(item):
    mode = str(getattr(item, 'match_mode', 'GREATER') or 'GREATER').strip().upper()
    return mode if mode in {'EQUAL', 'GREATER', 'LESS', 'RANGE'} else 'GREATER'


def _izom_propui_free_value_label_numeric_summary(item, field_root, value_kind, params=None, reference_entry=None, *, use_choices=False):
    normalized_kind = str(value_kind or 'FLOAT').strip().upper() or 'FLOAT'
    primary_field = f"{field_root}_int" if normalized_kind == 'INT' else f"{field_root}_float"
    range_field = f"{field_root}_range_int" if normalized_kind == 'INT' else f"{field_root}_range_float"
    primary_value = _izom_propui_free_threshold_storage_value(item, primary_field, normalized_kind)
    range_value = _izom_propui_free_threshold_storage_value(item, range_field, normalized_kind)

    def number_text(value):
        return _izom_propui_free_value_label_number_text(value, normalized_kind, params=params)

    mode = _izom_propui_free_value_label_match_mode(item)
    primary_text = number_text(primary_value)
    if mode == 'EQUAL':
        return f"= {primary_text}"
    if mode == 'LESS':
        return f"<= {primary_text}"
    if mode == 'RANGE':
        low_value = min(primary_value, range_value)
        high_value = max(primary_value, range_value)
        return f"{number_text(low_value)} to {number_text(high_value)}"
    return f">= {primary_text}"


def _izom_propui_free_value_label_component_text(component_meta, component_slot):
    try:
        resolved_slot = max(1, int(component_slot or 1))
    except (TypeError, ValueError):
        resolved_slot = 1
    labels = tuple(component_meta.get('labels', ()) or ()) if isinstance(component_meta, dict) else ()
    if 0 <= resolved_slot - 1 < len(labels):
        label = str(labels[resolved_slot - 1] or '').strip()
        if label:
            return f"[{label}]"
    return f"[{resolved_slot}]"


def _izom_propui_free_value_label_array_value(item, field_root, value_kind, component_meta):
    normalized_kind = str(value_kind or 'NONE').strip().upper() or 'NONE'
    field_name = f"{field_root}_float_array"
    if normalized_kind == 'INT_ARRAY':
        field_name = f"{field_root}_int_array"
    elif normalized_kind == 'BOOL_ARRAY':
        field_name = f"{field_root}_bool_array"

    try:
        raw_value = getattr(item, field_name, ())
    except AttributeError:
        raw_value = ()

    element_type = 'FLOAT'
    subtype = 'NONE'
    size = 4
    if isinstance(component_meta, dict):
        element_type = str(component_meta.get('element_type', element_type) or element_type)
        subtype = str(component_meta.get('subtype', subtype) or subtype)
        try:
            size = int(component_meta.get('size', size) or size)
        except (TypeError, ValueError):
            size = 4

    return izom_propui_free_array_visible_value(
        raw_value,
        element_type,
        subtype,
        size=size,
        default=raw_value,
    )


def _izom_propui_free_value_label_array_text(item, field_root, value_kind, component_meta, params=None):
    values = _izom_propui_free_value_label_array_value(item, field_root, value_kind, component_meta)
    try:
        values = tuple(values or ())
    except TypeError:
        values = ()
    preview = []
    for value in values[:6]:
        if isinstance(value, bool):
            preview.append('On' if value else 'Off')
        else:
            preview.append(_izom_propui_free_value_label_number_text(value, 'INT' if isinstance(value, int) and not isinstance(value, bool) else 'FLOAT', params=params))
    if len(values) > 6:
        preview.append('...')
    return '[' + ', '.join(preview) + ']'


def _izom_propui_free_self_value_label_row_summary(source_info, item):
    entry = source_info.get('entry')
    params = source_info.get('params')
    reference_entry = source_info.get('source') or entry
    component_info = (
        _izom_propui_free_entry_component_rule_info(entry, item, reference_entry=reference_entry)
        if entry is not None
        else {}
    )
    value_kind = str(component_info.get('value_kind', source_info.get('source_type', 'FLOAT')) or 'FLOAT')
    component_meta = component_info.get('component_meta', {}) if isinstance(component_info, dict) else {}
    use_component = bool(component_info.get('use_component', False))
    effective_value_kind = (
        str(component_meta.get('component_kind', value_kind) or value_kind)
        if use_component else value_kind
    )

    if effective_value_kind == 'BOOL' and use_component:
        state_label = 'On' if _izom_propui_free_normalize_bool_state(getattr(item, 'source_bool_state', 'WHEN_TRUE')) == 'WHEN_TRUE' else 'Off'
        return f"{_izom_propui_free_value_label_component_text(component_meta, component_info.get('component_slot', 1))} = {state_label}"

    if _izom_propui_free_is_numeric_type(effective_value_kind):
        match_text = _izom_propui_free_value_label_numeric_summary(
            item,
            'target_value',
            effective_value_kind,
            params=params,
            reference_entry=reference_entry,
            use_choices=not use_component,
        )
        if use_component:
            return f"{_izom_propui_free_value_label_component_text(component_meta, component_info.get('component_slot', 1))} {match_text}"
        return match_text

    if value_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        return f"= {_izom_propui_free_value_label_array_text(item, 'target_value', value_kind, component_meta, params=params)}"

    return 'Choose Value'


def _izom_propui_free_value_label_row_source_name(source_entry):
    if not isinstance(source_entry, dict):
        return 'None'
    label = str(source_entry.get('label', '') or '').strip()
    prop_id = str(source_entry.get('prop_id', '') or '').strip()
    return label or prop_id or 'Other Entry'


def _izom_propui_free_value_label_fallback_name(source_info):
    if str(source_info.get('target_mode', '') or '') == 'SELF':
        return "Fallback to General Label"
    return "Fallback"


def _izom_propui_free_value_label_row_summary(source_info, item):
    try:
        summary = _izom_propui_free_self_value_label_row_summary(source_info, item)
        if _izom_propui_free_rule_kind_value(item) == 'FALLBACK':
            summary = f"{summary} | Fallback"
        return summary
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return 'Value'

def _izom_propui_free_value_label_cache_key(
    owner,
    active_propname,
    source_info,
    *,
    collection_ptr=0,
    collection_len=0,
    collection_revision=0,
    snapshot_cache_token=0,
    runtime_cache_token=0,
):
    try:
        params_decimals = _izom_propui_free_editor_float_settings(source_info.get('params'))[0]
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        params_decimals = 3
    choice_count = 0
    choice_revision = 0
    return (
        _izom_propui_free_pointer(owner),
        str(active_propname or ''),
        int(collection_ptr or 0),
        int(collection_len or 0),
        int(collection_revision or 0),
        str(source_info.get('collection_name', '') or ''),
        str(source_info.get('target_mode', '') or ''),
        _izom_propui_free_pointer(source_info.get('entry')),
        _izom_propui_free_pointer(source_info.get('collection_owner')),
        _izom_propui_free_pointer(source_info.get('source')),
        int(choice_count),
        int(choice_revision),
        str(source_info.get('source_type', '') or ''),
        bool(getattr(source_info.get('entry'), 'value_labels_use_component', False)),
        int(getattr(source_info.get('entry'), 'value_labels_component_index', 1) or 1),
        int(params_decimals),
        int(snapshot_cache_token or 0),
        int(runtime_cache_token or 0),
    )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
