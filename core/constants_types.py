# SPDX-License-Identifier: GPL-3.0-or-later

IZOM_PROPUI_FREE_PROP_TYPE_ITEMS = [
    ('FLOAT', 'Float', 'Floating-point custom property'),
    ('INT', 'Integer', 'Integer custom property'),
    ('BOOL', 'Boolean', 'Boolean custom property'),
    ('ARRAY', 'Array', 'Typed float, integer, or boolean array custom property with selectable subtype and size'),
    ('TEXT', 'Text', 'Text-only entry shown in the generated UI without an interactable property'),
]

IZOM_PROPUI_FREE_PROP_TYPE_IDS = frozenset(identifier for identifier, _label, _description in IZOM_PROPUI_FREE_PROP_TYPE_ITEMS)
IZOM_PROPUI_FREE_MANAGED_PROP_TYPES = frozenset({'FLOAT', 'INT', 'BOOL', 'ARRAY'})


def izom_propui_free_is_managed_prop_type(prop_type):
    return str(prop_type or '').strip().upper() in IZOM_PROPUI_FREE_MANAGED_PROP_TYPES


IZOM_PROPUI_FREE_ARRAY_ELEMENT_TYPE_ITEMS = [
    ('FLOAT', 'Float', 'Array of floating-point values'),
    ('INT', 'Integer', 'Array of integer values'),
    ('BOOL', 'Boolean', 'Array of boolean values'),
]

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
