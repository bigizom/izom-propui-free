# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared ``__all__`` computation for PropUI's re-export hub modules.

Some modules expose a public surface through facade imports and rely on
``__all__`` to control what propagates. This helper keeps that filtering
consistent across every hub module.

Two shapes are needed:

- Re-export hubs that deliberately forward third-party names (``bpy``,
  ``Operator``, ``EnumProperty``, ...) to their siblings use ``all_public=True``
  (every non-dunder name).
- Hubs that expose only PropUI's own surface use the default (PropUI-prefixed
  names), optionally plus an ``extra`` allow-list for specific third-party
  names like ``bpy``/``UIList`` or sentinels like ``CLASSES``.

The helper excludes itself by identity so it never leaks into a module's
public surface.
"""

_IZOM_PUBLIC_PREFIXES = (
    "izom_propui_free",
    "_izom_propui_free",
    "IZOM_PROPUI_FREE",
    "_IZOM_PROPUI_FREE",
    "draw_izom_propui_free",
)


def izom_propui_free_public_names(namespace, *, all_public=False, extra=()):
    """Return the ``__all__`` tuple for a module given its ``globals()``.

    ``all_public`` exports every non-dunder name; otherwise only PropUI-prefixed
    names are exported. ``extra`` adds specific names (e.g. ``('bpy', 'UIList')``)
    regardless of prefix.
    """
    allow = set(extra)
    names = []
    for name, value in namespace.items():
        if name.startswith("__"):
            continue
        if value is izom_propui_free_public_names:
            continue
        if all_public or name in allow or name.startswith(_IZOM_PUBLIC_PREFIXES):
            names.append(name)
    return tuple(names)
