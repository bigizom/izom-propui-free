# SPDX-License-Identifier: GPL-3.0-or-later

from .model_proxies_common import (
    _izom_propui_free_bounds_cache_key,
    izom_propui_free_log_recovered,
)
import math
from bpy.props import FloatVectorProperty
from ..core.constants_display import IZOM_PROPUI_FREE_ARRAY_SIZE_MAX
from ..core.float_arrays import (
    izom_propui_free_array_storage_from_visible,
    izom_propui_free_array_visible_value,
    izom_propui_free_normalize_array_storage,
)
from .helper_cache_updates_float_storage import _izom_propui_free_pending_float_array_storage



def _izom_propui_free_color_proxy_guard_key(item, proxy_name):
    return (str(proxy_name), _izom_propui_free_bounds_cache_key(item))


def _izom_propui_free_color_component(value, default=1.0):
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        result = float(default)
    if not math.isfinite(result):
        result = float(default)
    return min(max(result, 0.0), 1.0)


def _izom_propui_free_color_proxy_components(value, visible_size, *, default_component=1.0):
    try:
        sequence = list(value)
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        sequence = []

    result = []
    for index in range(visible_size):
        try:
            raw = float(sequence[index]) if index < len(sequence) else default_component
        except (TypeError, ValueError, OverflowError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            raw = default_component
        result.append(_izom_propui_free_color_component(raw, default_component))
    return tuple(result)


def _izom_propui_free_color_proxy_value_tuple(item, field_name, visible_size):
    pending_storage = _izom_propui_free_pending_float_array_storage(item, field_name)
    try:
        current = list(
            pending_storage
            if pending_storage is not None
            else getattr(item, field_name, (1.0,) * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX))
        )
    except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        current = [1.0] * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)
    visible_value = izom_propui_free_array_visible_value(
        current,
        'FLOAT',
        'COLOR',
        size=visible_size,
        default=current,
    )
    return _izom_propui_free_color_proxy_components(visible_value, visible_size)


def _izom_propui_free_sync_float_array_color_proxy(item, field_name, *, size=4, proxy_name=None):
    try:
        visible_size = max(3, min(4, int(size or 4)))
    except (TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        visible_size = 4
    resolved_proxy_name = str(proxy_name or _izom_propui_free_float_array_color_proxy_name(field_name, visible_size))
    if not hasattr(item, resolved_proxy_name):
        return resolved_proxy_name

    return resolved_proxy_name


def _izom_propui_free_store_float_array_color_value(
    item,
    field_name,
    value,
    visible_size,
    *,
    defer_storage_write=False,
):
    expected = _izom_propui_free_color_proxy_components(value, visible_size)
    try:
        current_storage = list(getattr(item, field_name, (1.0,) * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)))
    except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        current_storage = [1.0] * int(IZOM_PROPUI_FREE_ARRAY_SIZE_MAX)
    try:
        new_storage = izom_propui_free_array_storage_from_visible(
            expected,
            'FLOAT',
            'COLOR',
            size=visible_size,
            previous=current_storage,
            default=current_storage,
        )
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return
    try:
        current_normalized = tuple(izom_propui_free_normalize_array_storage(current_storage, 'FLOAT'))
    except (TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        current_normalized = ()
    if len(current_normalized) >= len(new_storage) and all(
        abs(float(current_normalized[index]) - float(new_storage[index])) <= 1e-9
        for index in range(len(new_storage))
    ):
        return
    if defer_storage_write:
        try:
            from .helper_cache_updates import _izom_propui_free_schedule_float_array_storage_commit
        except (ImportError, AttributeError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            _izom_propui_free_schedule_float_array_storage_commit = None

        if _izom_propui_free_schedule_float_array_storage_commit is not None:
            if _izom_propui_free_schedule_float_array_storage_commit(item, field_name, new_storage):
                return
    try:
        setattr(item, field_name, new_storage)
    except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )


def _izom_propui_free_float_array_color_proxy_property(
    field_name,
    *,
    size=4,
    name="Color",
    description="",
    proxy_name=None,
    defer_storage_write=False,
):
    try:
        visible_size = max(3, min(4, int(size or 4)))
    except (TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        visible_size = 4

    resolved_proxy_name = str(proxy_name or f"{str(field_name)}_color")

    def _get(item):
        return _izom_propui_free_color_proxy_value_tuple(item, field_name, visible_size)

    def _set(item, value):
        _izom_propui_free_store_float_array_color_value(
            item,
            field_name,
            value,
            visible_size,
            defer_storage_write=defer_storage_write,
        )

    return FloatVectorProperty(
        name=name,
        description=description,
        default=(1.0,) * visible_size,
        min=0.0,
        max=1.0,
        size=visible_size,
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        get=_get,
        set=_set,
        options={'SKIP_SAVE'},
    )


def _izom_propui_free_direct_float_array_color_property(
    field_name,
    *,
    name="Color",
    description="",
    defer_storage_write=False,
):
    resolved_proxy_name = f"{str(field_name)}_color"

    def _get(item):
        return _izom_propui_free_color_proxy_value_tuple(item, field_name, 4)

    def _set(item, value):
        _izom_propui_free_store_float_array_color_value(
            item,
            field_name,
            value,
            4,
            defer_storage_write=defer_storage_write,
        )

    return FloatVectorProperty(
        name=name,
        description=description,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        get=_get,
        set=_set,
        options={'SKIP_SAVE'},
    )


def _izom_propui_free_float_array_color_proxy_name(field_name, size=4):
    try:
        normalized_size = max(3, min(4, int(size or 4)))
    except (TypeError, ValueError, OverflowError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        normalized_size = 4
    return f"{str(field_name)}_color_{normalized_size}"

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
