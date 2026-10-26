# SPDX-License-Identifier: GPL-3.0-or-later

"""Reload-safe ownership for Blender callbacks created by the Free extension."""

import bpy


_IZOM_PROPUI_FREE_LIFECYCLE_STATE_KEY = "_izom_propui_free_lifecycle_state"
_IZOM_PROPUI_FREE_LIFECYCLE_TIMERS_KEY = "_izom_propui_free_lifecycle_timers"
_IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES_KEY = "_izom_propui_free_editor_panel_classes"
_IZOM_PROPUI_FREE_HANDLER_MARKER_ATTR = "_izom_propui_free_lifecycle_handler"
_IZOM_PROPUI_FREE_LIFECYCLE_TIMER_FALLBACK = {}
_IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS = (
    AttributeError,
    KeyError,
    ReferenceError,
    RuntimeError,
    TypeError,
    ValueError,
)


def _izom_propui_free_driver_namespace():
    try:
        namespace = bpy.app.driver_namespace
    except _IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS:
        return None
    return namespace if isinstance(namespace, dict) else None


def _izom_propui_free_process_namespace():
    """Return reload-safe storage that is not cleared by blend-file loads."""
    try:
        namespace = getattr(bpy, '__dict__', None)
    except _IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS:
        return None
    return namespace if isinstance(namespace, dict) else None


def _izom_propui_free_lifecycle_state(*, create=True):
    process_namespace = _izom_propui_free_process_namespace()
    driver_namespace = _izom_propui_free_driver_namespace()
    state = (
        process_namespace.get(_IZOM_PROPUI_FREE_LIFECYCLE_STATE_KEY)
        if process_namespace is not None
        else None
    )
    if not isinstance(state, dict):
        legacy_state = (
            driver_namespace.get(_IZOM_PROPUI_FREE_LIFECYCLE_STATE_KEY)
            if driver_namespace is not None
            else None
        )
        if isinstance(legacy_state, dict):
            state = legacy_state
        elif not create:
            return None
        else:
            state = {'active': False, 'generation': 0}
        if process_namespace is not None:
            process_namespace[_IZOM_PROPUI_FREE_LIFECYCLE_STATE_KEY] = state
    if driver_namespace is not None:
        driver_namespace[_IZOM_PROPUI_FREE_LIFECYCLE_STATE_KEY] = state
    return state


def _izom_propui_free_lifecycle_timer_registry(*, create=True):
    process_namespace = _izom_propui_free_process_namespace()
    driver_namespace = _izom_propui_free_driver_namespace()
    registry = (
        process_namespace.get(_IZOM_PROPUI_FREE_LIFECYCLE_TIMERS_KEY)
        if process_namespace is not None
        else None
    )
    if not isinstance(registry, dict):
        legacy_registry = (
            driver_namespace.get(_IZOM_PROPUI_FREE_LIFECYCLE_TIMERS_KEY)
            if driver_namespace is not None
            else None
        )
        if isinstance(legacy_registry, dict):
            registry = legacy_registry
        elif not create:
            return {}
        else:
            registry = {}
        if process_namespace is not None:
            process_namespace[_IZOM_PROPUI_FREE_LIFECYCLE_TIMERS_KEY] = registry
    if driver_namespace is not None:
        driver_namespace[_IZOM_PROPUI_FREE_LIFECYCLE_TIMERS_KEY] = registry
    return registry


def izom_propui_free_editor_panel_class_registry(*, create=True):
    process_namespace = _izom_propui_free_process_namespace()
    driver_namespace = _izom_propui_free_driver_namespace()
    registry = (
        process_namespace.get(_IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES_KEY)
        if process_namespace is not None
        else None
    )
    if not isinstance(registry, dict):
        legacy_registry = (
            driver_namespace.get(_IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES_KEY)
            if driver_namespace is not None
            else None
        )
        if isinstance(legacy_registry, dict):
            registry = legacy_registry
        elif not create:
            return {}
        else:
            registry = {}
        if process_namespace is not None:
            process_namespace[_IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES_KEY] = registry
    if driver_namespace is not None:
        driver_namespace[_IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES_KEY] = registry
    return registry


def izom_propui_free_set_lifecycle_active(active):
    state = _izom_propui_free_lifecycle_state()
    if state is None:
        return
    next_active = bool(active)
    if next_active:
        state['generation'] = int(state.get('generation', 0) or 0) + 1
    state['active'] = next_active


def izom_propui_free_lifecycle_is_active():
    state = _izom_propui_free_lifecycle_state(create=False)
    return bool(state and state.get('active', False))


def _izom_propui_free_lifecycle_generation():
    state = _izom_propui_free_lifecycle_state(create=False)
    return int(state.get('generation', 0) or 0) if state else 0


def _izom_propui_free_unregister_timer_callback(callback):
    if not callable(callback):
        return
    try:
        if bpy.app.timers.is_registered(callback):
            bpy.app.timers.unregister(callback)
    except _IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS:
        return


def _izom_propui_free_timer_entry_callback(entry, field_name):
    if isinstance(entry, dict):
        callback = entry.get(field_name)
        return callback if callable(callback) else None
    return entry if field_name == 'timer' and callable(entry) else None


def izom_propui_free_register_lifecycle_timer(name, callback, *, first_interval=0.0):
    """Register a timer that cannot outlive its extension generation."""
    timer_name = str(name or '').strip()
    if not timer_name or not callable(callback) or not izom_propui_free_lifecycle_is_active():
        return False

    generation = _izom_propui_free_lifecycle_generation()
    registry = _izom_propui_free_lifecycle_timer_registry()
    previous = registry.pop(timer_name, None)
    _izom_propui_free_unregister_timer_callback(
        _izom_propui_free_timer_entry_callback(previous, 'timer')
    )

    def _managed_timer():
        state = _izom_propui_free_lifecycle_state(create=False)
        entry = registry.get(timer_name)
        if (
            not state
            or not bool(state.get('active', False))
            or int(state.get('generation', 0) or 0) != generation
            or not isinstance(entry, dict)
            or entry.get('timer') is not _managed_timer
        ):
            if isinstance(entry, dict) and entry.get('timer') is _managed_timer:
                registry.pop(timer_name, None)
            return None
        result = None
        try:
            result = callback()
        finally:
            if result is None and registry.get(timer_name) is entry:
                registry.pop(timer_name, None)
        return result

    entry = {
        'callback': callback,
        'timer': _managed_timer,
        'generation': generation,
    }
    registry[timer_name] = entry
    try:
        bpy.app.timers.register(
            _managed_timer,
            first_interval=max(0.0, float(first_interval)),
        )
    except _IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS:
        if registry.get(timer_name) is entry:
            registry.pop(timer_name, None)
        return False
    return True


def izom_propui_free_unregister_lifecycle_timer(name, callback=None):
    timer_name = str(name or '').strip()
    registry = _izom_propui_free_lifecycle_timer_registry(create=False)
    entry = registry.pop(timer_name, None)
    callbacks = (
        _izom_propui_free_timer_entry_callback(entry, 'timer'),
        callback,
    )
    seen = set()
    for candidate in callbacks:
        if not callable(candidate) or id(candidate) in seen:
            continue
        seen.add(id(candidate))
        _izom_propui_free_unregister_timer_callback(candidate)


def izom_propui_free_cancel_all_lifecycle_timers():
    registry = _izom_propui_free_lifecycle_timer_registry(create=False)
    callbacks = tuple(
        _izom_propui_free_timer_entry_callback(entry, 'timer')
        for entry in registry.values()
    )
    registry.clear()
    for callback in callbacks:
        _izom_propui_free_unregister_timer_callback(callback)
    _IZOM_PROPUI_FREE_LIFECYCLE_TIMER_FALLBACK.clear()
    process_namespace = _izom_propui_free_process_namespace()
    if process_namespace is not None:
        process_namespace.pop(_IZOM_PROPUI_FREE_LIFECYCLE_TIMERS_KEY, None)
    driver_namespace = _izom_propui_free_driver_namespace()
    if driver_namespace is not None:
        driver_namespace.pop(_IZOM_PROPUI_FREE_LIFECYCLE_TIMERS_KEY, None)


def _izom_propui_free_handler_has_marker(handler, marker):
    try:
        return str(getattr(handler, _IZOM_PROPUI_FREE_HANDLER_MARKER_ATTR, '') or '') == marker
    except _IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS:
        return False


def izom_propui_free_remove_lifecycle_handler(handlers, marker, callback=None):
    """Remove current and stale-reload copies of one owned handler."""
    marker = str(marker or '').strip()
    if handlers is None or not marker:
        return
    for handler in tuple(handlers):
        if handler is not callback and not _izom_propui_free_handler_has_marker(handler, marker):
            continue
        try:
            handlers.remove(handler)
        except _IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS:
            continue


def izom_propui_free_replace_lifecycle_handler(handlers, marker, callback):
    marker = str(marker or '').strip()
    if handlers is None or not marker or not callable(callback):
        return False
    izom_propui_free_remove_lifecycle_handler(handlers, marker, callback)
    try:
        setattr(callback, _IZOM_PROPUI_FREE_HANDLER_MARKER_ATTR, marker)
        handlers.append(callback)
    except _IZOM_PROPUI_FREE_LIFECYCLE_ACCESS_ERRORS:
        return False
    return True


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
