# SPDX-License-Identifier: GPL-3.0-or-later

import collections


_IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE = collections.OrderedDict()
_IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE_LIMIT = 64


def _izom_propui_free_cache_remember(cache, key, value, limit):
    cache[key] = value
    cache.move_to_end(key)
    while len(cache) > limit:
        cache.popitem(last=False)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
