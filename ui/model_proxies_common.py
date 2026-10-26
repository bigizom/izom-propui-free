# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
from .helper_value_labels_source import _izom_propui_free_find_value_label_owner



_IZOM_PROPUI_FREE_PROXY_EXCEPTIONS = (AttributeError, TypeError, ValueError, ReferenceError)
_IZOM_PROPUI_FREE_BOUNDS_ITEM_CACHE = {}
_IZOM_PROPUI_FREE_COLOR_PROXY_SYNC_GUARD = set()


def _izom_propui_free_clear_proxy_session_caches():
    _IZOM_PROPUI_FREE_BOUNDS_ITEM_CACHE.clear()
    _IZOM_PROPUI_FREE_COLOR_PROXY_SYNC_GUARD.clear()


def _izom_propui_free_bounds_cache_key(item):
    try:
        return int(item.as_pointer())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return id(item)


def _izom_propui_free_has_own_float_bounds(item):
    if isinstance(item, dict):
        return 'min_float' in item
    try:
        return 'min_float' in item.bl_rna.properties
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return hasattr(item, 'min_float')


def _izom_propui_free_proxy_value(item, field_name, default=None):
    if isinstance(item, dict):
        return item.get(field_name, default)
    return getattr(item, field_name, default)


def _izom_propui_free_resolve_bounds_item(item, field_name=None):
    if _izom_propui_free_has_own_float_bounds(item):
        return item
    try:
        source_component_index = int(getattr(item, 'source_component_index', 0) or 0)
    except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
        source_component_index = 0
    cache_key = (
        _izom_propui_free_bounds_cache_key(item),
        str(field_name or ''),
        source_component_index,
    )
    cached = _IZOM_PROPUI_FREE_BOUNDS_ITEM_CACHE.get(cache_key)
    if cached is not None and _izom_propui_free_has_own_float_bounds(cached):
        return cached
    try:
        params, entry, _coll_owner, _coll_name, _index = _izom_propui_free_find_value_label_owner(item)
        if entry is not None and _izom_propui_free_has_own_float_bounds(entry):
            _IZOM_PROPUI_FREE_BOUNDS_ITEM_CACHE[cache_key] = entry
            return entry
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    _IZOM_PROPUI_FREE_BOUNDS_ITEM_CACHE.pop(cache_key, None)
    return item


def _izom_propui_free_owner_float_bounds(item, field_name=None):
    bounds_item = _izom_propui_free_resolve_bounds_item(item, field_name=field_name)
    try:
        low = float(_izom_propui_free_proxy_value(bounds_item, 'min_float', 0.0))
    except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
        low = 0.0
    try:
        high = float(_izom_propui_free_proxy_value(bounds_item, 'max_float', 1.0))
    except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
        high = 1.0
    if high < low:
        low, high = high, low
    return low, high


def _izom_propui_free_clamp_owner_float_value(item, value, field_name=None):
    low, high = _izom_propui_free_owner_float_bounds(item, field_name=field_name)
    try:
        numeric_value = float(value)
    except _IZOM_PROPUI_FREE_PROXY_EXCEPTIONS:
        numeric_value = low
    try:
        from .helper_cache_updates import _izom_propui_free_find_params_for_entry, _izom_propui_free_snap_editor_float_value_for_params
        from .helper_value_labels import _izom_propui_free_find_value_label_owner

        params = _izom_propui_free_find_params_for_entry(item, None)
        if params is None:
            params, _entry, _owner, _collection_name, _index = _izom_propui_free_find_value_label_owner(item)
        numeric_value = _izom_propui_free_snap_editor_float_value_for_params(params, numeric_value, base=low)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    return min(max(numeric_value, low), high)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
