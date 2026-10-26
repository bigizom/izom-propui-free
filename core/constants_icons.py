# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .diagnostics import izom_propui_free_log_recovered


_IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE = None
_IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE = None
_IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE = None


def _izom_propui_free_clear_blender_icon_cache():
    global _IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE
    global _IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE
    global _IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE

    _IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE = None
    _IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE = None
    _IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE = None


def izom_propui_free_blender_icon_label(identifier):
    normalized = str(identifier or 'NONE').strip().upper() or 'NONE'
    if normalized == 'NONE':
        return 'No Icon'
    return " ".join(part.capitalize() for part in normalized.split('_') if part) or normalized


def izom_propui_free_blender_icon_items(_self=None, _context=None):
    global _IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE
    global _IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE
    global _IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE
    if _IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE is not None:
        return _IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE

    icon_ids = []
    try:
        import bpy

        icon_ids = list(bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items.keys())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        icon_ids = []

    if not icon_ids:
        icon_ids = [
            'NONE',
            'BOOKMARKS',
            'INFO',
            'DRIVER',
            'NODE_TOP',
            'FILE_REFRESH',
        ]

    items = []
    for index, icon_id in enumerate(icon_ids):
        identifier = str(icon_id or 'NONE').strip().upper() or 'NONE'
        label = izom_propui_free_blender_icon_label(identifier)
        description = 'Draw no icon' if identifier == 'NONE' else f"Draw the Blender '{label}' icon"
        items.append((identifier, label, description, identifier, index))

    _IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE = items
    _IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE = {item[0] for item in items}
    _IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE = {
        item[0]: int(item[4]) if len(item) >= 5 else index
        for index, item in enumerate(items)
    }
    return _IZOM_PROPUI_FREE_BLENDER_ICON_ITEMS_CACHE


def izom_propui_free_blender_icon_ids():
    global _IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE
    if _IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE is None:
        izom_propui_free_blender_icon_items()
    return _IZOM_PROPUI_FREE_BLENDER_ICON_IDS_CACHE


def _izom_propui_free_blender_icon_index_map():
    global _IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE
    if _IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE is None:
        izom_propui_free_blender_icon_items()
    return _IZOM_PROPUI_FREE_BLENDER_ICON_INDEX_CACHE


def izom_propui_free_blender_icon_default_number(identifier='NONE'):
    target = str(identifier or 'NONE').strip().upper() or 'NONE'
    return int(_izom_propui_free_blender_icon_index_map().get(target, 0))


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)
