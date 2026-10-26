# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
import bpy



IZOM_PROPUI_FREE_TREE_INDENT = 3.60
IZOM_PROPUI_FREE_GL_CHILD_OFFSET = 1.32
IZOM_PROPUI_FREE_UI_LIST_CACHE_LIMIT = 64
IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSED_ICON = 'RIGHTARROW'
IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON = 'DOWNARROW_HLT'
IZOM_PROPUI_FREE_ENTRY_LIST_NAME_MIN_WIDTH = 6.50
IZOM_PROPUI_FREE_ENTRY_LIST_NAME_BASE_WIDTH = 2.20
IZOM_PROPUI_FREE_ENTRY_LIST_NAME_CHAR_WIDTH = 0.42
IZOM_PROPUI_FREE_ENTRY_LIST_NAME_DEPTH_WIDTH = 1.15
IZOM_PROPUI_FREE_ENTRY_LIST_NAME_TREE_SLOT_WIDTH = 1.20
IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_WIDTH = 12.00
IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_MIN_WIDTH = 6.25
IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_WIDTH = 8.50
IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_MIN_WIDTH = 5.00
IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_DROPDOWN_PAD = 1.10


_IZOM_PROPUI_FREE_ENTRY_TYPE_ICONS = {
    'FLOAT': 'NODE_SOCKET_FLOAT',
    'INT': 'NODE_SOCKET_INT',
    'BOOL': 'NODE_SOCKET_BOOLEAN',
    'ARRAY': 'NODE_SOCKET_VECTOR',
    'TEXT': 'TEXT',
}

_IZOM_PROPUI_FREE_OBJECT_TYPE_ICONS = {
    'ARMATURE': 'ARMATURE_DATA',
    'CAMERA': 'CAMERA_DATA',
    'CURVE': 'CURVE_DATA',
    'EMPTY': 'EMPTY_DATA',
    'FONT': 'FONT_DATA',
    'GPENCIL': 'OUTLINER_DATA_GREASEPENCIL',
    'GREASEPENCIL': 'OUTLINER_DATA_GREASEPENCIL',
    'LATTICE': 'LATTICE_DATA',
    'LIGHT': 'LIGHT_DATA',
    'LIGHT_PROBE': 'LIGHTPROBE_SPHERE',
    'MESH': 'MESH_DATA',
    'META': 'META_DATA',
    'SPEAKER': 'SPEAKER',
    'SURFACE': 'SURFACE_DATA',
    'VOLUME': 'VOLUME_DATA',
}


_IZOM_PROPUI_FREE_ENTRY_LIST_DRAW_CACHE = {}
_IZOM_PROPUI_FREE_ENTRY_LIST_FILTER_CACHE = {}
_IZOM_PROPUI_FREE_VALUE_LABEL_LIST_CACHE = {}
_IZOM_PROPUI_FREE_VALUE_LABEL_FILTER_CACHE = {}
_IZOM_PROPUI_FREE_LAYOUT_LIST_STATE_CACHE = {}
_IZOM_PROPUI_FREE_LAYOUT_ENTRY_FILTER_CACHE = {}
_IZOM_PROPUI_FREE_VISIBILITY_ITEM_ICON_CACHE = {}


def _izom_propui_free_clear_ui_list_session_caches():
    _IZOM_PROPUI_FREE_ENTRY_LIST_DRAW_CACHE.clear()
    _IZOM_PROPUI_FREE_ENTRY_LIST_FILTER_CACHE.clear()
    _IZOM_PROPUI_FREE_VALUE_LABEL_LIST_CACHE.clear()
    _IZOM_PROPUI_FREE_VALUE_LABEL_FILTER_CACHE.clear()
    _IZOM_PROPUI_FREE_LAYOUT_LIST_STATE_CACHE.clear()
    _IZOM_PROPUI_FREE_LAYOUT_ENTRY_FILTER_CACHE.clear()
    _IZOM_PROPUI_FREE_VISIBILITY_ITEM_ICON_CACHE.clear()


def _izom_propui_free_pointer(value):
    try:
        return int(value.as_pointer())
    except (AttributeError, TypeError, ValueError):
        return 0


def _izom_propui_free_cached_lookup(cache, key, build_fn):
    cached = cache.get(key)
    if cached is not None:
        return cached
    value = build_fn()
    if len(cache) >= IZOM_PROPUI_FREE_UI_LIST_CACHE_LIMIT:
        cache.clear()
    cache[key] = value
    return value


def _izom_propui_free_safe_int_value(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _izom_propui_free_safe_collection_items(value):
    if value is None:
        return []
    try:
        return list(value)
    except (TypeError, ReferenceError):
        return []


def _izom_propui_free_entry_type_icon(prop_type):
    normalized = str(prop_type or 'FLOAT').strip().upper() or 'FLOAT'
    return _IZOM_PROPUI_FREE_ENTRY_TYPE_ICONS.get(normalized, 'DOT')


def _izom_propui_free_resolve_visibility_item_icon(kind, object_name):
    obj = None
    if object_name:
        try:
            obj = bpy.data.objects.get(object_name)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            obj = None
    obj_type = str(getattr(obj, 'type', '') or '').strip().upper()
    if obj_type:
        return _IZOM_PROPUI_FREE_OBJECT_TYPE_ICONS.get(obj_type, 'OBJECT_DATA')
    return 'BONE_DATA' if kind == 'BONE' else 'OBJECT_DATA'


def _izom_propui_free_visibility_item_icon(item):
    kind = str(getattr(item, 'kind', 'OBJECT') or 'OBJECT').strip().upper()
    if kind in {'POSE_BONE', 'BONE'}:
        return 'BONE_DATA'
    object_name = str(getattr(item, 'object_name', '') or '').strip()
    return _izom_propui_free_cached_lookup(
        _IZOM_PROPUI_FREE_VISIBILITY_ITEM_ICON_CACHE,
        (kind, object_name),
        lambda: _izom_propui_free_resolve_visibility_item_icon(kind, object_name),
    )


def _izom_propui_free_visibility_item_label(item):
    label = str(getattr(item, 'label', '') or '').strip()
    return label or str(getattr(item, 'object_name', '') or '').strip() or 'Object'

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), extra=('bpy',))
