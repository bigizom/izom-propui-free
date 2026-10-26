# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .generated_registry_lifecycle import (
    _izom_propui_free_portable_registry_class_count,
    _izom_propui_free_portable_registry_classes,
    _izom_propui_free_registered_generated_panel_classes,
    _izom_propui_free_running_portable_registry_keys,
    _izom_propui_free_split_portable_registry_items,
    izom_propui_free_invalidate_generated_lifecycle_status_cache,
    izom_propui_free_stale_running_generated_ui_keys,
)
from .generated_registry_text import (
    _izom_propui_free_generated_panel_class_names_from_texts,
    izom_propui_free_log_debug,
    izom_propui_free_log_warning,
)
import bpy
from .generated_registry_classes import (
    _izom_propui_free_prune_portable_registry_classes,
    _izom_propui_free_unregister_generated_panel_class,
    _izom_propui_free_unregister_handler_items,
)


def _izom_propui_free_unregister_portable_registry_key(registry_key, *, remove_namespace_key=False):
    key = str(registry_key or '').strip()
    if not key:
        return
    try:
        namespace = bpy.app.driver_namespace
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not access generated UI registry namespace",
            category='Generated UI',
            exception=exc,
        )
        return
    classes, unexpected_items = _izom_propui_free_split_portable_registry_items(
        namespace.get(key, []) or []
    )
    for unexpected_item in unexpected_items:
        izom_propui_free_log_debug(
            f"Ignoring unexpected generated UI registry item {unexpected_item!r}",
            category='Generated UI',
        )
    lifecycle_key = key + ':lifecycle_handlers'
    _izom_propui_free_unregister_handler_items(
        namespace.get(lifecycle_key, []) or [],
        category_name='lifecycle',
    )
    namespace[lifecycle_key] = []
    for panel_class in reversed(classes):
        _izom_propui_free_unregister_generated_panel_class(panel_class)
    if remove_namespace_key:
        namespace.pop(key, None)
        namespace.pop(lifecycle_key, None)
    else:
        namespace[key] = []
        namespace[lifecycle_key] = []


def izom_propui_free_unregister_stale_running_generated_uis():
    try:
        namespace = bpy.app.driver_namespace
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not inspect running generated UI registries",
            category='Generated UI',
            exception=exc,
        )
        return 0, 0
    stale_keys = izom_propui_free_stale_running_generated_ui_keys()
    text_panel_class_names = _izom_propui_free_generated_panel_class_names_from_texts()
    stale_registry_classes = {
        panel_class
        for key in stale_keys
        for panel_class in _izom_propui_free_portable_registry_classes(namespace, key)
    }
    class_count = 0
    for key in stale_keys:
        class_count += _izom_propui_free_portable_registry_class_count(namespace, key)
        _izom_propui_free_unregister_portable_registry_key(key, remove_namespace_key=True)
    orphan_classes = [
        panel_class
        for panel_class in _izom_propui_free_registered_generated_panel_classes()
        if (
            panel_class not in stale_registry_classes
            and str(getattr(panel_class, '__name__', '') or '').strip() not in text_panel_class_names
        )
    ]
    for panel_class in reversed(orphan_classes):
        if _izom_propui_free_unregister_generated_panel_class(panel_class):
            class_count += 1
    _izom_propui_free_prune_portable_registry_classes(namespace, orphan_classes)
    if stale_keys or orphan_classes:
        izom_propui_free_invalidate_generated_lifecycle_status_cache()
    return len(stale_keys) + len(orphan_classes), class_count


def izom_propui_free_unregister_all_running_generated_uis():
    try:
        namespace = bpy.app.driver_namespace
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not inspect running generated UI registries",
            category='Generated UI',
            exception=exc,
        )
        return 0, 0
    running_keys = _izom_propui_free_running_portable_registry_keys()
    class_count = 0
    for key in running_keys:
        class_count += _izom_propui_free_portable_registry_class_count(namespace, key)
        _izom_propui_free_unregister_portable_registry_key(key, remove_namespace_key=True)
    orphan_classes = _izom_propui_free_registered_generated_panel_classes()
    for panel_class in reversed(orphan_classes):
        if _izom_propui_free_unregister_generated_panel_class(panel_class):
            class_count += 1
    if running_keys or orphan_classes:
        izom_propui_free_invalidate_generated_lifecycle_status_cache()
    return len(running_keys) + len(orphan_classes), class_count

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
