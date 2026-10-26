# SPDX-License-Identifier: GPL-3.0-or-later

from .cache_common import (
    _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE,
    _izom_propui_free_pointer_guard_key,
)


def izom_propui_free_cached_value_label_owner_map(params):
    if params is None:
        return {}

    cache_key = _izom_propui_free_pointer_guard_key(params)
    cached = _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE.get(cache_key)
    if cached is not None:
        return cached

    owner_map = {}
    for entry in getattr(params, 'izom_propui_free_entries', []) or []:
        for index, candidate in enumerate(getattr(entry, 'value_labels', None) or []):
            owner_map[_izom_propui_free_pointer_guard_key(candidate)] = (params, entry, entry, 'value_labels', index)

    _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE[cache_key] = owner_map
    return owner_map


def izom_propui_free_remember_value_label_owner(params, item, entry, collection_owner, collection_name, index):
    if params is None or item is None or collection_owner is None:
        return
    try:
        cache_key = _izom_propui_free_pointer_guard_key(params)
        item_key = _izom_propui_free_pointer_guard_key(item)
        owner_map = _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE.setdefault(cache_key, {})
        owner_map[item_key] = (
            params,
            entry,
            collection_owner,
            str(collection_name or ''),
            int(index or 0),
        )
    except (AttributeError, TypeError, ValueError, ReferenceError):
        return

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
