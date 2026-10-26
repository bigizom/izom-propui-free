# SPDX-License-Identifier: GPL-3.0-or-later

from .model_proxies_common import (
    _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS,
)
from bpy.props import (
    FloatProperty,
    IntProperty,
)



def _izom_propui_free_editor_float_proxy_property(
    field_name,
    *,
    name,
    description,
    precision,
    min_value=None,
    max_value=None,
    default_value=0.0,
):
    low = float(min_value) if min_value is not None else None
    high = float(max_value) if max_value is not None else None
    try:
        default_numeric = float(default_value)
    except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
        default_numeric = 0.0
    if low is not None and default_numeric < low:
        default_numeric = low
    if high is not None and default_numeric > high:
        default_numeric = high

    def _get(item):
        try:
            return float(getattr(item, field_name, default_numeric))
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return default_numeric

    def _set(item, value):
        try:
            numeric_value = float(value)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return
        if low is not None and numeric_value < low:
            numeric_value = low
        if high is not None and numeric_value > high:
            numeric_value = high
        try:
            current_value = float(getattr(item, field_name, 0.0))
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            current_value = None
        if current_value is not None and abs(current_value - numeric_value) <= 1e-9:
            return
        try:
            setattr(item, field_name, numeric_value)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return

    kwargs = {
        'name': name,
        'description': description,
        'default': default_numeric,
        'precision': int(precision),
        'step': 1,
        'get': _get,
        'set': _set,
        'options': {'SKIP_SAVE'},
    }
    if low is not None:
        kwargs['min'] = low
        kwargs['soft_min'] = low
    if high is not None:
        kwargs['max'] = high
        kwargs['soft_max'] = high
    return FloatProperty(**kwargs)


def _izom_propui_free_editor_int_proxy_property(field_name, *, name, description, min_value=None, max_value=None, default_value=0.0):
    int_min = None
    int_max = None
    if min_value is not None:
        int_min = int(float(min_value))
        if float(int_min) < float(min_value):
            int_min += 1
    if max_value is not None:
        int_max = int(float(max_value))
        if float(int_max) > float(max_value):
            int_max -= 1
    try:
        default_int = int(round(float(default_value)))
    except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
        default_int = 0
    if int_min is not None and default_int < int_min:
        default_int = int_min
    if int_max is not None and default_int > int_max:
        default_int = int_max

    def _get(item):
        try:
            return int(round(float(getattr(item, field_name, default_int))))
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return default_int

    def _set(item, value):
        try:
            numeric_value = float(int(value))
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return
        if int_min is not None and numeric_value < float(int_min):
            numeric_value = float(int_min)
        if int_max is not None and numeric_value > float(int_max):
            numeric_value = float(int_max)
        try:
            current_value = float(getattr(item, field_name, 0.0))
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            current_value = None
        if current_value is not None and abs(current_value - numeric_value) <= 1e-9:
            return
        try:
            setattr(item, field_name, numeric_value)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return

    kwargs = {
        'name': name,
        'description': description,
        'default': default_int,
        'get': _get,
        'set': _set,
        'options': {'SKIP_SAVE'},
    }
    if int_min is not None:
        kwargs['min'] = int_min
    if int_max is not None:
        kwargs['max'] = int_max
    return IntProperty(**kwargs)


def _izom_propui_free_add_editor_float_proxy_properties(cls, field_specs):
    annotations = dict(getattr(cls, '__annotations__', {}))
    for field_name, meta in field_specs.items():
        field_label = str(meta.get('name', field_name))
        field_description = str(meta.get('description', '') or '')
        min_value = meta.get('min')
        max_value = meta.get('max')
        default_value = meta.get('default', 0.0)
        for precision in range(7):
            annotations[f"{field_name}_editor_p{precision}"] = _izom_propui_free_editor_float_proxy_property(
                field_name,
                name=field_label,
                description=field_description,
                precision=precision,
                min_value=min_value,
                max_value=max_value,
                default_value=default_value,
            )
        annotations[f"{field_name}_editor_i"] = _izom_propui_free_editor_int_proxy_property(
            field_name,
            name=field_label,
            description=field_description,
            min_value=min_value,
            max_value=max_value,
            default_value=default_value,
        )
    cls.__annotations__ = annotations

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
