# SPDX-License-Identifier: GPL-3.0-or-later

"""Undo-independent Free editor session state stored on WindowManager."""

import json

import bpy
from bpy.app.handlers import persistent
from bpy.props import CollectionProperty, StringProperty
from bpy.types import PropertyGroup
from .lifecycle import (
    izom_propui_free_remove_lifecycle_handler,
    izom_propui_free_replace_lifecycle_handler,
)


_SESSION_COLLECTION_ATTR = "izom_propui_free_editor_sessions"
_SESSION_OWNER_CACHE = {}
_SESSION_VALUE_CACHE = {}
_DATA_BINDING_CACHE = {}
_DATA_SESSION_CACHE = {}
_EDITOR_SESSION_REGISTERED = False


class IZOM_PROPUI_FREE_EditorSession(PropertyGroup):
    owner_key: StringProperty(default="", options={'HIDDEN'})
    values_json: StringProperty(default="{}", options={'HIDDEN'})


CLASSES = (IZOM_PROPUI_FREE_EditorSession,)


def _window_manager():
    try:
        return bpy.context.window_manager
    except (AttributeError, RuntimeError, ReferenceError):
        return None


def _data_path(data):
    try:
        return str(data.path_from_id() or "")
    except (AttributeError, ValueError, RuntimeError, ReferenceError):
        return ""


def _pointer(data):
    try:
        return int(data.as_pointer())
    except (AttributeError, RuntimeError, ReferenceError):
        return id(data)


def _id_key(data):
    id_data = getattr(data, "id_data", None)
    session_uid = getattr(id_data, "session_uid", 0) if id_data is not None else 0
    if session_uid:
        id_key = f"UID:{int(session_uid)}"
    else:
        try:
            id_key = f"PTR:{int(id_data.as_pointer())}"
        except (AttributeError, RuntimeError, ReferenceError):
            id_key = f"NAME:{getattr(id_data, 'name_full', getattr(id_data, 'name', ''))}"
    return id_key


def _type_name(data):
    return str(
        getattr(getattr(data, "bl_rna", None), "identifier", type(data).__name__)
        or type(data).__name__
    )


def _data_binding(data):
    pointer = _pointer(data)
    uid = str(getattr(data, "uid", "") or "").strip()
    cached = _DATA_BINDING_CACHE.get(pointer)
    if cached is not None and cached[0] == uid and (uid or cached[3]):
        return cached

    path = _data_path(data)
    owner_path = "izom_propui_free" if path.startswith("izom_propui_free") else (path or "ROOT")
    is_root = not uid and (not path or path == owner_path)
    subject_key = "ROOT" if is_root else f"{_type_name(data)}:{uid or path or f'PTR:{pointer}'}"
    binding = (uid, f"{_id_key(data)}|{owner_path}", subject_key, is_root)
    if uid or is_root:
        _DATA_BINDING_CACHE[pointer] = binding
    return binding


def _state_key(data, field_name, binding=None):
    resolved = binding or _data_binding(data)
    return f"{resolved[2]}|{str(field_name or '').strip()}"


def _editor_session_for_binding(data, binding, *, create=False):
    wm = _window_manager()
    collection = getattr(wm, _SESSION_COLLECTION_ATTR, None) if wm is not None else None
    if collection is None or data is None:
        return None
    owner_key = binding[1]
    try:
        wm_key = int(wm.as_pointer())
    except (AttributeError, RuntimeError, ReferenceError):
        wm_key = id(wm)
    data_cache_key = (wm_key, _pointer(data))
    stable_binding = bool(binding[0] or binding[3])
    cached_data_session = _DATA_SESSION_CACHE.get(data_cache_key) if stable_binding else None
    if cached_data_session is not None and cached_data_session[0] == binding[0]:
        try:
            int(cached_data_session[1].as_pointer())
            return cached_data_session[1]
        except (AttributeError, RuntimeError, ReferenceError):
            _DATA_SESSION_CACHE.pop(data_cache_key, None)
    cache_key = (wm_key, owner_key)
    cached = _SESSION_OWNER_CACHE.get(cache_key)
    try:
        if cached is not None and str(cached.owner_key) == owner_key:
            if stable_binding:
                _DATA_SESSION_CACHE[data_cache_key] = (binding[0], cached)
            return cached
    except (AttributeError, RuntimeError, ReferenceError):
        _SESSION_OWNER_CACHE.pop(cache_key, None)
    for item in collection:
        if str(getattr(item, "owner_key", "") or "") == owner_key:
            _SESSION_OWNER_CACHE[cache_key] = item
            if stable_binding:
                _DATA_SESSION_CACHE[data_cache_key] = (binding[0], item)
            return item
    if not create:
        return None
    item = collection.add()
    item.owner_key = owner_key
    item.values_json = "{}"
    _SESSION_OWNER_CACHE[cache_key] = item
    if stable_binding:
        _DATA_SESSION_CACHE[data_cache_key] = (binding[0], item)
    return item


def izom_propui_free_editor_session(data, *, create=False):
    if not _EDITOR_SESSION_REGISTERED or data is None:
        return None
    return _editor_session_for_binding(data, _data_binding(data), create=create)


def _values(session):
    if session is None:
        return {}
    try:
        pointer = int(session.as_pointer())
    except (AttributeError, RuntimeError, ReferenceError):
        return {}
    cached = _SESSION_VALUE_CACHE.get(pointer)
    if cached is not None:
        return cached
    raw = str(session.values_json or "{}")
    try:
        values = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        values = {}
    if not isinstance(values, dict):
        values = {}
    _SESSION_VALUE_CACHE[pointer] = values
    return values


def _legacy_value(data, field_name, default):
    try:
        return data.get(field_name, default)
    except (AttributeError, TypeError, RuntimeError, ReferenceError):
        return default


def izom_propui_free_editor_session_value(data, field_name, default=None):
    if not _EDITOR_SESSION_REGISTERED:
        return _legacy_value(data, field_name, default)
    binding = _data_binding(data)
    values = _values(_editor_session_for_binding(data, binding, create=False))
    key = _state_key(data, field_name, binding)
    if key in values:
        return values[key]
    try:
        return data.get(field_name, default)
    except (AttributeError, TypeError, RuntimeError, ReferenceError):
        return default


def _session_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def izom_propui_free_set_editor_session_value(data, field_name, value):
    if not _EDITOR_SESSION_REGISTERED:
        return False
    binding = _data_binding(data)
    session = _editor_session_for_binding(data, binding, create=True)
    if session is None:
        return False
    values = _values(session)
    key = _state_key(data, field_name, binding)
    if key in values and values[key] == value:
        return False
    values[key] = value
    raw = json.dumps(values, sort_keys=True, separators=(",", ":"))
    session.values_json = raw
    try:
        _SESSION_VALUE_CACHE[int(session.as_pointer())] = values
    except (AttributeError, RuntimeError, ReferenceError):
        return True
    return True


def izom_propui_free_session_bool_property(field_name, *, default=False, **kwargs):
    def getter(data):
        try:
            return bool(izom_propui_free_editor_session_value(data, field_name, default))
        except (RecursionError, ReferenceError, RuntimeError):
            return bool(default)

    def setter(data, value):
        try:
            izom_propui_free_set_editor_session_value(data, field_name, bool(value))
        except (RecursionError, ReferenceError, RuntimeError):
            return

    return bpy.props.BoolProperty(
        default=default,
        get=getter,
        set=setter,
        **kwargs,
    )


def izom_propui_free_session_int_property(field_name, *, default=0, **kwargs):
    def getter(data):
        try:
            return _session_int(izom_propui_free_editor_session_value(data, field_name, default), default)
        except (RecursionError, ReferenceError, RuntimeError):
            return int(default)

    def setter(data, value):
        try:
            izom_propui_free_set_editor_session_value(data, field_name, int(value))
        except (RecursionError, ReferenceError, RuntimeError):
            return

    return bpy.props.IntProperty(
        default=default,
        get=getter,
        set=setter,
        **kwargs,
    )


def izom_propui_free_session_string_property(field_name, *, default="", **kwargs):
    def getter(data):
        try:
            return str(izom_propui_free_editor_session_value(data, field_name, default) or "")
        except (RecursionError, ReferenceError, RuntimeError):
            return str(default or "")

    def setter(data, value):
        try:
            izom_propui_free_set_editor_session_value(data, field_name, str(value or ""))
        except (RecursionError, ReferenceError, RuntimeError):
            return

    return bpy.props.StringProperty(
        default=default,
        get=getter,
        set=setter,
        **kwargs,
    )


def izom_propui_free_session_enum_property(field_name, *, default_value=0, **kwargs):
    def getter(data):
        try:
            return _session_int(izom_propui_free_editor_session_value(data, field_name, default_value), default_value)
        except (RecursionError, ReferenceError, RuntimeError):
            return int(default_value)

    def setter(data, value):
        try:
            izom_propui_free_set_editor_session_value(data, field_name, int(value))
        except (RecursionError, ReferenceError, RuntimeError):
            return

    return bpy.props.EnumProperty(
        get=getter,
        set=setter,
        **kwargs,
    )


def izom_propui_free_invalidate_editor_session_bindings():
    """Drop pointer-derived accelerators after authored collection changes."""
    _DATA_BINDING_CACHE.clear()
    _DATA_SESSION_CACHE.clear()


def izom_propui_free_clear_editor_sessions():
    _SESSION_OWNER_CACHE.clear()
    _SESSION_VALUE_CACHE.clear()
    _DATA_BINDING_CACHE.clear()
    _DATA_SESSION_CACHE.clear()
    for wm in getattr(bpy.data, "window_managers", ()):
        collection = getattr(wm, _SESSION_COLLECTION_ATTR, None)
        if collection is not None:
            collection.clear()


@persistent
def _izom_propui_free_editor_session_load_post(_unused):
    izom_propui_free_clear_editor_sessions()


def izom_propui_free_register_editor_sessions():
    global _EDITOR_SESSION_REGISTERED
    if not hasattr(bpy.types.WindowManager, _SESSION_COLLECTION_ATTR):
        setattr(bpy.types.WindowManager, _SESSION_COLLECTION_ATTR, CollectionProperty(type=IZOM_PROPUI_FREE_EditorSession))
    izom_propui_free_replace_lifecycle_handler(
        bpy.app.handlers.load_post,
        'editor_session_load_post',
        _izom_propui_free_editor_session_load_post,
    )
    izom_propui_free_clear_editor_sessions()
    from ..core.editor_hooks import izom_propui_free_set_editor_hooks
    from .helper_cache_updates_entry_params import _izom_propui_free_clear_cached_entry_params
    izom_propui_free_set_editor_hooks(invalidate=_izom_propui_free_clear_cached_entry_params)
    _EDITOR_SESSION_REGISTERED = True


def izom_propui_free_unregister_editor_sessions():
    global _EDITOR_SESSION_REGISTERED
    _EDITOR_SESSION_REGISTERED = False
    from ..core.editor_hooks import izom_propui_free_set_editor_hooks
    izom_propui_free_set_editor_hooks()
    izom_propui_free_remove_lifecycle_handler(
        bpy.app.handlers.load_post,
        'editor_session_load_post',
        _izom_propui_free_editor_session_load_post,
    )
    izom_propui_free_clear_editor_sessions()
    if hasattr(bpy.types.WindowManager, _SESSION_COLLECTION_ATTR):
        delattr(bpy.types.WindowManager, _SESSION_COLLECTION_ATTR)
