# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .model_proxies_arrays import (
    IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
    _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS,
    _izom_propui_free_array_proxy_default,
    _izom_propui_free_clamp_owner_float_value,
    izom_propui_free_log_recovered,
    izom_propui_free_normalize_array_storage,
)
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
)



def _izom_propui_free_array_component_proxy_name(field_name, element_type, component_index, precision=None):
    normalized_type = str(element_type or 'FLOAT').strip().upper() or 'FLOAT'
    precision_suffix = ''
    if normalized_type == 'FLOAT' and precision is not None:
        try:
            precision_suffix = f"__p{max(0, min(6, int(precision)))}"
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            precision_suffix = ''
    return f"{str(field_name)}__component__{normalized_type.lower()}__{int(component_index)}{precision_suffix}"


def _izom_propui_free_array_component_proxy_property(field_name, element_type, component_index, *, name, description, precision=3, default_value=None):
    normalized_type = str(element_type or 'FLOAT').strip().upper() or 'FLOAT'
    index = int(component_index)
    if normalized_type == 'BOOL':
        component_default = bool(default_value) if default_value is not None else False
    elif normalized_type == 'INT':
        try:
            component_default = int(default_value) if default_value is not None else 0
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            component_default = 0
    else:
        try:
            component_default = float(default_value) if default_value is not None else 1.0
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            component_default = 1.0
    default_storage = (component_default,) * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)

    def _get_sequence(item):
        try:
            current = getattr(item, field_name)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            current = ()
        return list(izom_propui_free_normalize_array_storage(current, normalized_type, default=default_storage))

    def _set_sequence(item, values):
        try:
            setattr(item, field_name, values)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return

    if normalized_type == 'BOOL':
        default_bool = bool(component_default)

        def _get(item):
            sequence = _get_sequence(item)
            return bool(sequence[index]) if index < len(sequence) else default_bool

        def _set(item, value):
            sequence = _get_sequence(item)
            next_value = bool(value)
            if index < len(sequence) and bool(sequence[index]) == next_value:
                return
            sequence[index] = next_value
            _set_sequence(item, tuple(sequence))

        return BoolProperty(
            name=name,
            description=description,
            default=default_bool,
            get=_get,
            set=_set,
            options={'SKIP_SAVE'},
        )

    if normalized_type == 'INT':
        default_int = int(component_default)

        def _get(item):
            sequence = _get_sequence(item)
            return int(sequence[index]) if index < len(sequence) else default_int

        def _set(item, value):
            sequence = _get_sequence(item)
            try:
                next_value = int(value)
            except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
                return
            if index < len(sequence) and int(sequence[index]) == next_value:
                return
            sequence[index] = next_value
            _set_sequence(item, tuple(sequence))

        return IntProperty(
            name=name,
            description=description,
            default=default_int,
            get=_get,
            set=_set,
            options={'SKIP_SAVE'},
        )

    default_float = float(component_default)

    def _get(item):
        sequence = _get_sequence(item)
        return float(sequence[index]) if index < len(sequence) else default_float

    def _set(item, value):
        sequence = _get_sequence(item)
        try:
            next_value = _izom_propui_free_clamp_owner_float_value(item, value, field_name=field_name)
        except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
            return
        if index < len(sequence) and abs(float(sequence[index]) - next_value) <= 1e-9:
            return
        sequence[index] = next_value
        _set_sequence(item, tuple(sequence))

    return FloatProperty(
        name=name,
        description=description,
        default=default_float,
        precision=max(0, min(6, int(precision))),
        step=1,
        get=_get,
        set=_set,
        options={'SKIP_SAVE'},
    )


def _izom_propui_free_add_array_component_proxy_properties(cls, field_specs):
    annotations = dict(getattr(cls, '__annotations__', {}))
    for field_name, meta in field_specs.items():
        field_label = str(meta.get('name', field_name))
        field_description = str(meta.get('description', '') or '')
        for element_type in ('FLOAT', 'INT', 'BOOL'):
            default_value = _izom_propui_free_array_proxy_default(meta, element_type)
            for component_index in range(int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)):
                if element_type == 'FLOAT':
                    for precision in range(7):
                        annotations[_izom_propui_free_array_component_proxy_name(field_name, element_type, component_index, precision)] = _izom_propui_free_array_component_proxy_property(
                            field_name,
                            element_type,
                            component_index,
                            name=field_label,
                            description=field_description,
                            precision=precision,
                            default_value=default_value,
                        )
                    annotations[_izom_propui_free_array_component_proxy_name(field_name, element_type, component_index)] = annotations[
                        _izom_propui_free_array_component_proxy_name(field_name, element_type, component_index, 3)
                    ]
                else:
                    annotations[_izom_propui_free_array_component_proxy_name(field_name, element_type, component_index)] = _izom_propui_free_array_component_proxy_property(
                        field_name,
                        element_type,
                        component_index,
                        name=field_label,
                        description=field_description,
                        default_value=default_value,
                    )
    cls.__annotations__ = annotations

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
