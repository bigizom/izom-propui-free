# SPDX-License-Identifier: GPL-3.0-or-later
"""Optional UI services; core modules never import their UI implementation."""

_IZOM_PROPUI_FREE_ENTRY_CACHE_INVALIDATOR = None
_IZOM_PROPUI_FREE_SESSION_BINDING_PRIMER = None


def izom_propui_free_set_editor_hooks(*, invalidate=None, prime=None):
    global _IZOM_PROPUI_FREE_ENTRY_CACHE_INVALIDATOR, _IZOM_PROPUI_FREE_SESSION_BINDING_PRIMER
    _IZOM_PROPUI_FREE_ENTRY_CACHE_INVALIDATOR = invalidate
    _IZOM_PROPUI_FREE_SESSION_BINDING_PRIMER = prime


def izom_propui_free_invalidate_editor_entry_cache(params=None):
    if _IZOM_PROPUI_FREE_ENTRY_CACHE_INVALIDATOR is not None:
        _IZOM_PROPUI_FREE_ENTRY_CACHE_INVALIDATOR(params)
