# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .model_proxies_color import (
    FloatVectorProperty,
    IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
    _izom_propui_free_float_array_color_proxy_name,
    _izom_propui_free_float_array_color_proxy_property,
    izom_propui_free_array_storage_from_visible,
    izom_propui_free_array_visible_value,
    izom_propui_free_log_recovered,
    izom_propui_free_normalize_array_storage,
)
from ..core.constants_display import IZOM_PROPUI_FREE_FLOAT_ARRAY_SUBTYPE_ITEMS
from ..core.float_arrays import (
    izom_propui_free_float_array_ui_subtype,
    izom_propui_free_float_array_visible_size,
    izom_propui_free_normalize_float_array_subtype,
)
from .model_proxies_common import (
    _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS,
    _izom_propui_free_clamp_owner_float_value,
)



def _izom_propui_free_array_proxy_default(meta, element_type):
    normalized_type = str(element_type or 'FLOAT').strip().upper() or 'FLOAT'
    key_by_type = {
        'FLOAT': 'float_default',
        'INT': 'int_default',
        'BOOL': 'bool_default',
    }
    fallback_by_type = {
        'FLOAT': 1.0,
        'INT': 0,
        'BOOL': False,
    }
    key = key_by_type.get(normalized_type, 'float_default')
    if isinstance(meta, dict) and key in meta:
        return meta.get(key)
    if isinstance(meta, dict) and 'default' in meta:
        default_value = meta.get('default')
        if isinstance(default_value, dict):
            return default_value.get(normalized_type, fallback_by_type.get(normalized_type, 1.0))
        if not isinstance(default_value, (list, tuple)):
            return default_value
    return fallback_by_type.get(normalized_type, 1.0)


def _izom_propui_free_float_array_proxy_property(
    field_name,
    *,
    subtype,
    size=None,
    name="Value",
    description="",
    default_value=1.0,
):
    normalized_subtype = izom_propui_free_normalize_float_array_subtype(subtype)
    is_color_subtype = normalized_subtype in {'COLOR', 'COLOR_GAMMA'}
    try:
        visible_size = max(1, min(int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX), int(size or izom_propui_free_float_array_visible_size(normalized_subtype))))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        visible_size = izom_propui_free_float_array_visible_size(normalized_subtype)
    ui_subtype = izom_propui_free_float_array_ui_subtype(normalized_subtype)
    if is_color_subtype and visible_size not in {3, 4}:
        ui_subtype = 'NONE'
    try:
        default_component = float(default_value)
    except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
        default_component = 1.0
    default_storage = (default_component,) * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)
    default_visible = tuple(default_storage[:visible_size])

    def _get(item):
        try:
            current = getattr(item, field_name, default_storage)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            current = default_storage
        return list(
            izom_propui_free_array_visible_value(
                current,
                'FLOAT',
                normalized_subtype,
                size=visible_size,
                default=default_storage,
            )
        )

    def _set(item, value):
        try:
            current = getattr(item, field_name, default_storage)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            current = default_storage
        try:
            values = list(value)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return
        clamped_values = [
            _izom_propui_free_clamp_owner_float_value(item, component, field_name=field_name)
            for component in values[:visible_size]
        ]
        new_storage = izom_propui_free_array_storage_from_visible(
            clamped_values,
            'FLOAT',
            normalized_subtype,
            size=visible_size,
            previous=current,
            default=default_storage,
        )
        try:
            current_storage = tuple(izom_propui_free_normalize_array_storage(getattr(item, field_name, default_storage), 'FLOAT', default=default_storage))
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            current_storage = ()
        if len(current_storage) >= len(new_storage) and all(
            abs(float(current_storage[index]) - float(new_storage[index])) <= 1e-9
            for index in range(len(new_storage))
        ):
            return
        try:
            setattr(item, field_name, new_storage)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return

    return FloatVectorProperty(
        name=name,
        description=description,
        size=visible_size,
        subtype=ui_subtype,
        default=default_visible,
        get=_get,
        set=_set,
        options={'SKIP_SAVE'},
    )


def _izom_propui_free_float_array_proxy_name(field_name, subtype, size=None):
    normalized_subtype = izom_propui_free_normalize_float_array_subtype(subtype)
    if size is not None:
        return f"{str(field_name)}__proxy__{normalized_subtype.lower()}__{int(size)}"
    return f"{str(field_name)}__proxy__{normalized_subtype.lower()}"


def _izom_propui_free_add_float_array_proxy_properties(cls, field_specs):
    annotations = dict(getattr(cls, '__annotations__', {}))
    for field_name, meta in field_specs.items():
        field_label = str(meta.get('name', field_name))
        field_description = str(meta.get('description', '') or '')
        default_value = _izom_propui_free_array_proxy_default(meta, 'FLOAT')
        annotations[_izom_propui_free_float_array_color_proxy_name(field_name, 3)] = _izom_propui_free_float_array_color_proxy_property(
            field_name,
            size=3,
            name=field_label,
            description=field_description,
            proxy_name=_izom_propui_free_float_array_color_proxy_name(field_name, 3),
        )
        annotations[_izom_propui_free_float_array_color_proxy_name(field_name, 4)] = _izom_propui_free_float_array_color_proxy_property(
            field_name,
            size=4,
            name=field_label,
            description=field_description,
            proxy_name=_izom_propui_free_float_array_color_proxy_name(field_name, 4),
        )
        for subtype, _label, _description in IZOM_PROPUI_FREE_FLOAT_ARRAY_SUBTYPE_ITEMS:
            default_proxy_name = _izom_propui_free_float_array_proxy_name(field_name, subtype)
            annotations[default_proxy_name] = _izom_propui_free_float_array_proxy_property(
                field_name,
                subtype=subtype,
                size=izom_propui_free_float_array_visible_size(subtype),
                name=field_label,
                description=field_description,
                default_value=default_value,
            )
            for visible_size in range(1, int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX) + 1):
                proxy_name = _izom_propui_free_float_array_proxy_name(field_name, subtype, visible_size)
                try:
                    annotations[proxy_name] = _izom_propui_free_float_array_proxy_property(
                        field_name,
                        subtype=subtype,
                        size=visible_size,
                        name=field_label,
                        description=field_description,
                        default_value=default_value,
                    )
                except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
                    continue
    cls.__annotations__ = annotations

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
