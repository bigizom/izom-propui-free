# SPDX-License-Identifier: GPL-3.0-or-later

"""
Namespace Consolidation Module (ui/helpers.py)

This module dynamically gathers and re-exports functions and definitions from
all the 'helper_' files in this directory (helper_cache_updates, helper_field_clamp, etc.).
It acts as a routed namespace hub for sibling UI modules.

CRITICAL: By routing imports through this consolidated interface, we resolve and
prevent Python circular dependency loops during Blender addon startup/registration.
Do NOT remove or restructure these re-exports without tracing the dependency graph.
"""

from . import helper_cache_updates as _helper_cache_updates
from . import helper_field_clamp as _helper_field_clamp
from . import helper_layout as _helper_layout
from . import helper_selection as _helper_selection
from . import helper_validation as _helper_validation
from . import helper_value_labels as _helper_value_labels


def _izom_propui_free_export_helper_module(module):
    exported_names = tuple(getattr(module, '__all__', ()) or ())
    if exported_names:
        for name in exported_names:
            if hasattr(module, name):
                globals()[name] = getattr(module, name)
        return

    for name in dir(module):
        if not (
            name.startswith('_izom_propui_free')
            or name.startswith('_IZOM_PROPUI_FREE')
            or name.startswith('IZOM_PROPUI_FREE')
            or name.startswith('izom_propui_free')
            or name.startswith('draw_')
        ):
            continue
        value = getattr(module, name)
        if getattr(value, '__module__', module.__name__) != module.__name__:
            continue
        globals()[name] = value


for _module in (
    _helper_cache_updates,
    _helper_field_clamp,
    _helper_layout,
    _helper_selection,
    _helper_validation,
    _helper_value_labels,
):
    _izom_propui_free_export_helper_module(_module)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
