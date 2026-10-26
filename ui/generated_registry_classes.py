# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_registry_common import (
    _izom_propui_free_is_generated_panel_class_name,
    _izom_propui_free_is_portable_registry_key,
)
import bpy
from ..core.diagnostics import (
    IZOM_PROPUI_FREE_RECOVERABLE_ERRORS,
    izom_propui_free_log_debug,
    izom_propui_free_log_warning,
)


def _izom_propui_free_registered_generated_panel_classes():
    panel_classes = []
    try:
        type_names = list(dir(bpy.types))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not inspect registered Blender panel classes",
            category='Generated UI',
            exception=exc,
        )
        return panel_classes
    for type_name in type_names:
        if not _izom_propui_free_is_generated_panel_class_name(type_name):
            continue
        try:
            panel_class = getattr(bpy.types, type_name, None)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_debug(
                f"Could not inspect generated panel class {type_name}",
                category='Generated UI',
                exception=exc,
            )
            continue
        if isinstance(panel_class, type):
            panel_classes.append(panel_class)
    return panel_classes


def _izom_propui_free_split_portable_registry_items(items):
    panel_classes = []
    unexpected_items = []
    for item in list(items or []):
        if isinstance(item, type):
            panel_classes.append(item)
        elif item is not None:
            unexpected_items.append(item)
    return panel_classes, unexpected_items


def _izom_propui_free_portable_registry_class_count(namespace, key):
    classes, _unexpected = _izom_propui_free_split_portable_registry_items(
        namespace.get(str(key or '').strip(), []) if namespace is not None else []
    )
    return len(classes)


def _izom_propui_free_portable_registry_classes(namespace, key):
    classes, _unexpected = _izom_propui_free_split_portable_registry_items(
        namespace.get(str(key or '').strip(), []) if namespace is not None else []
    )
    return classes


def _izom_propui_free_unregister_generated_panel_class(panel_class):
    try:
        bpy.utils.unregister_class(panel_class)
        return True
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            f"Could not unregister portable generated panel {getattr(panel_class, '__name__', panel_class)}",
            category='Generated UI',
            exception=exc,
        )
    return False


def _izom_propui_free_unregister_handler_items(items, *, category_name):
    for handler_item in list(items or []):
        if not (isinstance(handler_item, tuple) and len(handler_item) == 2 and callable(handler_item[1])):
            izom_propui_free_log_debug(
                f"Ignoring unexpected generated UI {category_name} handler item {handler_item!r}",
                category='Generated UI',
            )
            continue
        handler_name, handler = handler_item
        handlers = getattr(bpy.app.handlers, str(handler_name or ''), None)
        if handlers is None or handler not in handlers:
            continue
        try:
            handlers.remove(handler)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                f"Could not remove generated UI {category_name} handler {handler_name}",
                category='Generated UI',
                exception=exc,
            )

def _izom_propui_free_prune_portable_registry_classes(namespace, panel_classes):
    stale_classes = set(panel_classes or ())
    if not stale_classes:
        return
    try:
        namespace_keys = list(namespace.keys())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not inspect generated UI registry namespace for pruning",
            category='Generated UI',
            exception=exc,
        )
        return
    for key in namespace_keys:
        key_text = str(key or '').strip()
        if not _izom_propui_free_is_portable_registry_key(key_text):
            continue
        try:
            items = list(namespace.get(key_text, []) or [])
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                f"Could not inspect generated UI registry {key_text}",
                category='Generated UI',
                exception=exc,
            )
            continue
        pruned = [item for item in items if item not in stale_classes]
        if len(pruned) == len(items):
            continue
        try:
            namespace[key_text] = pruned
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                f"Could not prune stale generated panel classes from registry {key_text}",
                category='Generated UI',
                exception=exc,
            )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
