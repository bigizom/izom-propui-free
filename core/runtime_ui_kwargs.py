# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import math

from .runtime_idprops import (
    _izom_propui_free_detect_array_element_type,
    _izom_propui_free_detect_supported_prop_type,
    _izom_propui_free_sequence_value,
    izom_propui_free_log_recovered,
)
from .constants_display import IZOM_PROPUI_FREE_FLOAT_SUBTYPE_ITEMS
from .constants_serialized import (
    IZOM_PROPUI_FREE_MAX_FLOAT_PRECISION,
    IZOM_PROPUI_FREE_MAX_NUMERIC_STEP,
)
from .float_arrays import (
    izom_propui_free_array_value_kind,
    izom_propui_free_array_visible_value,
    izom_propui_free_normalize_array_element_type,
    izom_propui_free_normalize_array_size,
    izom_propui_free_normalize_array_subtype,
)
from .snapshot_entries_runtime import _izom_propui_free_snapshot_entry
from .text import _izom_propui_free_limit_tooltip_text
from .value_access_common import _izom_propui_free_entry_value
from .value_access_entries import (
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_size,
    izom_propui_free_entry_array_subtype,
    izom_propui_free_entry_array_visible_value,
    izom_propui_free_entry_float_array_subtype,
)


def _izom_propui_free_float_soft_limits(entry, low, high):
    if not bool(entry.get('use_soft_limits', False)):
        return float(low), float(high)
    soft_low = float(entry.get('soft_min_float', low))
    soft_high = float(entry.get('soft_max_float', high))
    if soft_low > soft_high:
        soft_low, soft_high = soft_high, soft_low
    soft_low = min(max(soft_low, low), high)
    soft_high = min(max(soft_high, low), high)
    return soft_low, soft_high

def _izom_propui_free_int_soft_limits(entry, low, high):
    if not bool(entry.get('use_soft_limits', False)):
        return int(low), int(high)
    soft_low = int(entry.get('soft_min_int', low))
    soft_high = int(entry.get('soft_max_int', high))
    if soft_low > soft_high:
        soft_low, soft_high = soft_high, soft_low
    soft_low = min(max(soft_low, low), high)
    soft_high = min(max(soft_high, low), high)
    return soft_low, soft_high

def _izom_propui_free_is_native_color_array(element_type, subtype):
    normalized_element_type = izom_propui_free_normalize_array_element_type(element_type, 'FLOAT')
    if normalized_element_type != 'FLOAT':
        return False
    return izom_propui_free_array_value_kind(normalized_element_type, subtype) == 'COLOR'

def _izom_propui_free_native_color_components(value, default_component=1.0):
    try:
        sequence = list(value)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        sequence = []

    result = []
    for item in sequence:
        result.append(_izom_propui_free_clamp_float(item, default=default_component, min_value=0.0, max_value=1.0))
    return tuple(result)

def _izom_propui_free_clamp_int(value, default=0, min_value=None, max_value=None):
    try:
        result = int(value)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        result = int(default)
    if min_value is not None:
        result = max(int(min_value), result)
    if max_value is not None:
        result = min(int(max_value), result)
    return result

def _izom_propui_free_clamp_float(value, default=0.0, min_value=None, max_value=None):
    try:
        result = float(value)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        result = float(default)
    if not math.isfinite(result):
        result = float(default)
    if min_value is not None:
        result = max(float(min_value), result)
    if max_value is not None:
        result = min(float(max_value), result)
    return result

def _izom_propui_free_normalize_float_precision_value(precision_value, default=3):
    return max(0, min(IZOM_PROPUI_FREE_MAX_FLOAT_PRECISION, _izom_propui_free_clamp_int(precision_value, default=default)))

def _izom_propui_free_normalize_int_step_value(step_value, default=1):
    return max(1, min(IZOM_PROPUI_FREE_MAX_NUMERIC_STEP, _izom_propui_free_clamp_int(step_value, default=default)))

def _izom_propui_free_normalize_float_subtype_value(subtype_value, default='NONE'):
    valid = {item[0] for item in IZOM_PROPUI_FREE_FLOAT_SUBTYPE_ITEMS}
    subtype = str(subtype_value or default).strip() or default
    return subtype if subtype in valid else default

def _izom_propui_free_build_copy_ui_data_kwargs(ui_data, value):
    if not ui_data:
        return {}

    prop_type = _izom_propui_free_detect_supported_prop_type(value, ui_data)
    description = str(ui_data.get('description', '') or '').strip()
    kwargs = {'description': description} if description else {}

    if prop_type == 'FLOAT':
        current_value = _izom_propui_free_clamp_float(value, default=0.0)
        low = _izom_propui_free_clamp_float(ui_data.get('min', current_value), default=current_value)
        high = _izom_propui_free_clamp_float(ui_data.get('max', current_value), default=current_value)
        if low > high:
            low, high = high, low
        soft_low = _izom_propui_free_clamp_float(ui_data.get('soft_min', low), default=low, min_value=low, max_value=high)
        soft_high = _izom_propui_free_clamp_float(ui_data.get('soft_max', high), default=high, min_value=low, max_value=high)
        if soft_low > soft_high:
            soft_low, soft_high = soft_high, soft_low
        kwargs.update(
            default=_izom_propui_free_clamp_float(ui_data.get('default', current_value), default=current_value, min_value=low, max_value=high),
            min=low,
            max=high,
            soft_min=soft_low,
            soft_max=soft_high,
            step=_izom_propui_free_float_step_from_ui_data(ui_data.get('step', 0.10)),
            precision=_izom_propui_free_normalize_float_precision_value(ui_data.get('precision', 3)),
            subtype=_izom_propui_free_normalize_float_subtype_value(ui_data.get('subtype', 'NONE')),
        )
    elif prop_type == 'INT':
        current_value = _izom_propui_free_clamp_int(value, default=0)
        low = _izom_propui_free_clamp_int(ui_data.get('min', current_value), default=current_value)
        high = _izom_propui_free_clamp_int(ui_data.get('max', current_value), default=current_value)
        if low > high:
            low, high = high, low
        soft_low = _izom_propui_free_clamp_int(ui_data.get('soft_min', low), default=low, min_value=low, max_value=high)
        soft_high = _izom_propui_free_clamp_int(ui_data.get('soft_max', high), default=high, min_value=low, max_value=high)
        if soft_low > soft_high:
            soft_low, soft_high = soft_high, soft_low
        kwargs.update(
            default=_izom_propui_free_clamp_int(ui_data.get('default', current_value), default=current_value, min_value=low, max_value=high),
            min=low,
            max=high,
            soft_min=soft_low,
            soft_max=soft_high,
            step=_izom_propui_free_normalize_int_step_value(ui_data.get('step', 1)),
        )
    elif prop_type == 'BOOL':
        kwargs['default'] = bool(ui_data.get('default', value))
    elif prop_type == 'ARRAY':
        array_element_type = _izom_propui_free_detect_array_element_type(value, ui_data)
        array_subtype = izom_propui_free_normalize_array_subtype(ui_data.get('subtype', 'NONE'), array_element_type, 'NONE')
        is_native_color_array = _izom_propui_free_is_native_color_array(array_element_type, array_subtype)
        raw_size = ui_data.get('size', None)
        if raw_size is None:
            sequence = _izom_propui_free_sequence_value(value) or []
            raw_size = len(sequence)
        array_size = izom_propui_free_normalize_array_size(raw_size, array_subtype, array_element_type, default=raw_size)
        current_value = tuple(
            izom_propui_free_array_visible_value(
                value,
                array_element_type,
                array_subtype,
                size=array_size,
            )
        )
        if array_element_type == 'FLOAT':
            kwargs['subtype'] = array_subtype
        if array_element_type == 'FLOAT' and is_native_color_array:
            kwargs.update(
                default=_izom_propui_free_native_color_components(current_value),
                min=0.0,
                max=1.0,
                soft_min=0.0,
                soft_max=1.0,
            )
        elif array_element_type == 'FLOAT':
            low = _izom_propui_free_clamp_float(ui_data.get('min', 0.0), default=0.0)
            high = _izom_propui_free_clamp_float(ui_data.get('max', 1.0), default=1.0)
            if low > high:
                low, high = high, low
            soft_low = _izom_propui_free_clamp_float(ui_data.get('soft_min', low), default=low, min_value=low, max_value=high)
            soft_high = _izom_propui_free_clamp_float(ui_data.get('soft_max', high), default=high, min_value=low, max_value=high)
            if soft_low > soft_high:
                soft_low, soft_high = soft_high, soft_low
            default_value = tuple(
                min(max(float(component), low), high)
                for component in izom_propui_free_array_visible_value(
                    ui_data.get('default', current_value),
                    array_element_type,
                    array_subtype,
                    size=array_size,
                    default=current_value,
                )
            )
            kwargs.update(
                default=default_value,
                min=low,
                max=high,
                soft_min=soft_low,
                soft_max=soft_high,
                step=_izom_propui_free_float_step_from_ui_data(ui_data.get('step', 0.10)),
                precision=_izom_propui_free_normalize_float_precision_value(ui_data.get('precision', 3)),
            )
        elif array_element_type == 'INT':
            low = _izom_propui_free_clamp_int(ui_data.get('min', 0), default=0)
            high = _izom_propui_free_clamp_int(ui_data.get('max', 1), default=1)
            if low > high:
                low, high = high, low
            soft_low = _izom_propui_free_clamp_int(ui_data.get('soft_min', low), default=low, min_value=low, max_value=high)
            soft_high = _izom_propui_free_clamp_int(ui_data.get('soft_max', high), default=high, min_value=low, max_value=high)
            if soft_low > soft_high:
                soft_low, soft_high = soft_high, soft_low
            default_value = tuple(
                _izom_propui_free_clamp_int(component, default=0, min_value=low, max_value=high)
                for component in izom_propui_free_array_visible_value(
                    ui_data.get('default', current_value),
                    array_element_type,
                    array_subtype,
                    size=array_size,
                    default=current_value,
                )
            )
            kwargs.update(
                default=default_value,
                min=low,
                max=high,
                soft_min=soft_low,
                soft_max=soft_high,
                step=_izom_propui_free_normalize_int_step_value(ui_data.get('step', 1)),
            )
        else:
            kwargs['default'] = tuple(
                bool(component)
                for component in izom_propui_free_array_visible_value(
                    ui_data.get('default', current_value),
                    array_element_type,
                    array_subtype,
                    size=array_size,
                    default=current_value,
                )
            )

    return kwargs

def _izom_propui_free_build_entry_custom_prop_ui_kwargs(entry, prop_id='', fallback_value=None):
    prop_type = str(_izom_propui_free_entry_value(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    description = izom_propui_free_build_entry_tooltip(entry, prop_id, current_value=fallback_value)
    kwargs = {'description': description}

    if prop_type == 'FLOAT':
        min_value = _izom_propui_free_clamp_float(_izom_propui_free_entry_value(entry, 'min_float', 0.0), default=0.0)
        max_value = _izom_propui_free_clamp_float(_izom_propui_free_entry_value(entry, 'max_float', 1.0), default=1.0)
        low = min(min_value, max_value)
        high = max(min_value, max_value)
        soft_low, soft_high = _izom_propui_free_float_soft_limits(
            {
                'use_soft_limits': bool(_izom_propui_free_entry_value(entry, 'use_soft_limits', False)),
                'soft_min_float': _izom_propui_free_entry_value(entry, 'soft_min_float', low),
                'soft_max_float': _izom_propui_free_entry_value(entry, 'soft_max_float', high),
            },
            low,
            high,
        )
        default_source = low if fallback_value is None else fallback_value
        kwargs.update(
            default=_izom_propui_free_clamp_float(
                _izom_propui_free_entry_value(entry, 'default_float', default_source),
                default=default_source,
                min_value=low,
                max_value=high,
            ),
            min=low,
            max=high,
            soft_min=soft_low,
            soft_max=soft_high,
            step=_izom_propui_free_normalize_float_step_value(_izom_propui_free_entry_value(entry, 'step_float', 0.10)),
            precision=_izom_propui_free_normalize_float_precision_value(_izom_propui_free_entry_value(entry, 'precision', 3)),
            subtype=_izom_propui_free_normalize_float_subtype_value(_izom_propui_free_entry_value(entry, 'float_subtype', 'NONE')),
        )
    elif prop_type == 'INT':
        min_value = _izom_propui_free_clamp_int(_izom_propui_free_entry_value(entry, 'min_int', 0), default=0)
        max_value = _izom_propui_free_clamp_int(_izom_propui_free_entry_value(entry, 'max_int', 5), default=1)
        low = min(min_value, max_value)
        high = max(min_value, max_value)
        soft_low, soft_high = _izom_propui_free_int_soft_limits(
            {
                'use_soft_limits': bool(_izom_propui_free_entry_value(entry, 'use_soft_limits', False)),
                'soft_min_int': _izom_propui_free_entry_value(entry, 'soft_min_int', low),
                'soft_max_int': _izom_propui_free_entry_value(entry, 'soft_max_int', high),
            },
            low,
            high,
        )
        default_source = low if fallback_value is None else fallback_value
        kwargs.update(
            default=_izom_propui_free_clamp_int(
                _izom_propui_free_entry_value(entry, 'default_int', default_source),
                default=default_source,
                min_value=low,
                max_value=high,
            ),
            min=low,
            max=high,
            soft_min=soft_low,
            soft_max=soft_high,
            step=_izom_propui_free_normalize_int_step_value(_izom_propui_free_entry_value(entry, 'step_int', 1)),
        )
    elif prop_type == 'BOOL':
        kwargs['default'] = bool(_izom_propui_free_entry_value(entry, 'default_bool', fallback_value if fallback_value is not None else False))
    elif prop_type == 'ARRAY':
        array_element_type = (
            izom_propui_free_entry_array_element_type(entry, 'FLOAT')
            if prop_type == 'ARRAY' else
            'FLOAT'
        )
        array_subtype = (
            izom_propui_free_entry_array_subtype(entry, 'NONE')
            if prop_type == 'ARRAY' else
            izom_propui_free_entry_float_array_subtype(entry, 'NONE')
        )
        is_native_color_array = _izom_propui_free_is_native_color_array(array_element_type, array_subtype)
        array_size = (
            izom_propui_free_entry_array_size(entry, 4)
            if prop_type == 'ARRAY' else
            izom_propui_free_normalize_array_size(None, array_subtype, array_element_type)
        )
        if fallback_value is not None:
            try:
                fallback_sequence = tuple(fallback_value)
            except TypeError:
                fallback_sequence = ()
            if len(fallback_sequence) == array_size:
                default_source = fallback_sequence
            else:
                default_source = izom_propui_free_array_visible_value(
                    fallback_value,
                    array_element_type,
                    array_subtype,
                    size=array_size,
                )
        else:
            default_source = izom_propui_free_entry_array_visible_value(entry, 'default')
        if array_element_type == 'FLOAT':
            kwargs['subtype'] = array_subtype
        if array_element_type == 'FLOAT' and is_native_color_array:
            kwargs.update(
                default=_izom_propui_free_native_color_components(default_source),
                min=0.0,
                max=1.0,
                soft_min=0.0,
                soft_max=1.0,
            )
        elif array_element_type == 'FLOAT':
            min_value = _izom_propui_free_clamp_float(_izom_propui_free_entry_value(entry, 'min_float', 0.0), default=0.0)
            max_value = _izom_propui_free_clamp_float(_izom_propui_free_entry_value(entry, 'max_float', 1.0), default=1.0)
            low = min(min_value, max_value)
            high = max(min_value, max_value)
            soft_low, soft_high = _izom_propui_free_float_soft_limits(
                {
                    'use_soft_limits': bool(_izom_propui_free_entry_value(entry, 'use_soft_limits', False)),
                    'soft_min_float': _izom_propui_free_entry_value(entry, 'soft_min_float', low),
                    'soft_max_float': _izom_propui_free_entry_value(entry, 'soft_max_float', high),
                },
                low,
                high,
            )
            kwargs.update(
                default=tuple(min(max(float(component), low), high) for component in default_source),
                min=low,
                max=high,
                soft_min=soft_low,
                soft_max=soft_high,
                step=_izom_propui_free_normalize_float_step_value(_izom_propui_free_entry_value(entry, 'step_float', 0.10)),
                precision=_izom_propui_free_normalize_float_precision_value(_izom_propui_free_entry_value(entry, 'precision', 3)),
            )
        elif array_element_type == 'INT':
            min_value = _izom_propui_free_clamp_int(_izom_propui_free_entry_value(entry, 'min_int', 0), default=0)
            max_value = _izom_propui_free_clamp_int(_izom_propui_free_entry_value(entry, 'max_int', 5), default=1)
            low = min(min_value, max_value)
            high = max(min_value, max_value)
            soft_low, soft_high = _izom_propui_free_int_soft_limits(
                {
                    'use_soft_limits': bool(_izom_propui_free_entry_value(entry, 'use_soft_limits', False)),
                    'soft_min_int': _izom_propui_free_entry_value(entry, 'soft_min_int', low),
                    'soft_max_int': _izom_propui_free_entry_value(entry, 'soft_max_int', high),
                },
                low,
                high,
            )
            kwargs.update(
                default=tuple(
                    _izom_propui_free_clamp_int(component, default=0, min_value=low, max_value=high)
                    for component in default_source
                ),
                min=low,
                max=high,
                soft_min=soft_low,
                soft_max=soft_high,
                step=_izom_propui_free_normalize_int_step_value(_izom_propui_free_entry_value(entry, 'step_int', 1)),
            )
        else:
            kwargs['default'] = tuple(bool(component) for component in default_source)

    return kwargs

def _izom_propui_free_normalize_float_step_value(step_value, default=0.10):
    try:
        step = float(step_value)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        step = float(default)
    if not math.isfinite(step):
        step = float(default)
    return max(0.01, step)

def _izom_propui_free_float_step_from_ui_data(step_value, default=0.10):
    step = _izom_propui_free_normalize_float_step_value(step_value, default=default)
    if 1.0 <= step <= 100.0 and abs(step - round(step)) < 1e-9:
        step = step / 100.0
    return max(0.01, min(1.0, step))

def izom_propui_free_build_entry_tooltip(entry, prop_id='', current_value=None):
    runtime_entry = entry if isinstance(entry, dict) else _izom_propui_free_snapshot_entry(entry)
    static_tooltip = str(runtime_entry.get('description', '') or '').strip()
    if not static_tooltip:
        return ''
    return _izom_propui_free_limit_tooltip_text(static_tooltip)

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
