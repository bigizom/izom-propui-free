# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import time

from .generated_registry_classes import (
    _izom_propui_free_portable_registry_class_count,
    _izom_propui_free_portable_registry_classes,
    _izom_propui_free_registered_generated_panel_classes,
    _izom_propui_free_split_portable_registry_items,
)
from .generated_registry_text import (
    _izom_propui_free_data_collection,
    _izom_propui_free_generated_panel_class_names_from_texts,
    _izom_propui_free_is_managed_portable_text_name,
    _izom_propui_free_is_portable_registry_key,
    _izom_propui_free_text_lifecycle_fingerprint,
    _izom_propui_free_text_registry_key_map,
    izom_propui_free_log_debug,
    izom_propui_free_log_warning,
)
import bpy
from .generated_lifecycle import (
    izom_propui_free_compute_generated_lifecycle_status as _izom_propui_free_compute_lifecycle_status_payload,
)
from .generated_naming import (
    _izom_propui_free_generated_registry_key_for_slot,
    _izom_propui_free_generated_script_name_for_slot,
)
from .generated_registry_common import (
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CACHE,
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CHECK_TIMES,
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_SIGNATURES,
)


def _izom_propui_free_portable_script_slots():
    from .generated_portable_slots import _izom_propui_free_portable_script_slots as portable_script_slots

    return portable_script_slots()


def _izom_propui_free_schedule_generated_lifecycle_status_refresh(*args, **kwargs):
    return None


def _izom_propui_free_generated_lifecycle_signature(
    texts=None,
    running_keys=None,
    registered_panel_classes=None,
    *,
    include_source_hash=True,
):
    if texts is None:
        texts = _izom_propui_free_data_collection('texts')
    text_signature = [
        fingerprint
        for fingerprint in (
            _izom_propui_free_text_lifecycle_fingerprint(text, include_source_hash=include_source_hash)
            for text in list(texts or [])
        )
        if fingerprint is not None
    ]
    if running_keys is None:
        running_keys = _izom_propui_free_running_portable_registry_keys()
    if registered_panel_classes is None:
        registered_panel_classes = _izom_propui_free_registered_generated_panel_classes()
    return (
        tuple(sorted(text_signature)),
        tuple(sorted(str(key or '').strip() for key in (running_keys or ()) if str(key or '').strip())),
        tuple(sorted(str(getattr(panel_class, '__name__', '') or '').strip() for panel_class in (registered_panel_classes or ()))),
    )


def _izom_propui_free_stale_running_generated_ui_keys_from(running_keys, text_registry_keys):
    text_keys = {
        str(key or '').strip()
        for key in (text_registry_keys or ())
        if str(key or '').strip()
    }
    return sorted(
        str(key or '').strip()
        for key in (running_keys or ())
        if str(key or '').strip() and str(key or '').strip() not in text_keys
    )


def _izom_propui_free_running_portable_registry_keys():
    try:
        namespace = bpy.app.driver_namespace
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not inspect running generated UI registries",
            category='Generated UI',
            exception=exc,
        )
        return []
    running = set()
    for key in list(namespace.keys()):
        key_text = str(key or '').strip()
        if key_text.endswith(':lifecycle_handlers'):
            suffix = ':lifecycle_handlers'
            base_key = key_text[:-len(suffix)]
            if _izom_propui_free_is_portable_registry_key(base_key) and list(namespace.get(key_text, []) or []):
                running.add(base_key)
            continue
        if not _izom_propui_free_is_portable_registry_key(key_text):
            continue
        classes, unexpected_items = _izom_propui_free_split_portable_registry_items(
            namespace.get(key_text, []) or []
        )
        lifecycle_key = key_text + ':lifecycle_handlers'
        if (
            classes
            or list(namespace.get(lifecycle_key, []) or [])
        ):
            running.add(key_text)
        for unexpected_item in unexpected_items:
            izom_propui_free_log_debug(
                f"Ignoring unexpected generated UI registry item {unexpected_item!r}",
                category='Generated UI',
            )
    return sorted(running)


def izom_propui_free_stale_running_generated_ui_keys():
    return _izom_propui_free_stale_running_generated_ui_keys_from(
        _izom_propui_free_running_portable_registry_keys(),
        _izom_propui_free_text_registry_key_map().keys(),
    )

def izom_propui_free_invalidate_generated_lifecycle_status_cache():
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CACHE.clear()
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_SIGNATURES.clear()
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CHECK_TIMES.clear()
    _izom_propui_free_schedule_generated_lifecycle_status_refresh()


def _izom_propui_free_portable_generated_script_targets(slots=None):
    if slots is None:
        slots = _izom_propui_free_portable_script_slots()
    targets = []
    for slot in slots:
        item = dict(slot or {})
        text_name = str(item.get('script_name', '') or '').strip() or _izom_propui_free_generated_script_name_for_slot(item)
        if text_name:
            targets.append((text_name, _izom_propui_free_generated_registry_key_for_slot(item)))
    return targets


def _izom_propui_free_compute_generated_lifecycle_status(*, deep=False):
    cache_key = 'deep' if deep else 'fast'
    slots = _izom_propui_free_portable_script_slots()
    expected_targets = list(_izom_propui_free_portable_generated_script_targets(slots))
    expected_text_set = {
        str(text_name or '').strip()
        for text_name, _registry_key in expected_targets
        if str(text_name or '').strip()
    }
    texts = _izom_propui_free_data_collection('texts')
    text_list = list(texts or [])
    text_registry_key_map = _izom_propui_free_text_registry_key_map(text_list, use_cached=not deep)
    generated_text_names = set(text_registry_key_map.values())
    existing_text_names = sorted(
        str(getattr(text, 'name', '') or '').strip()
        for text in text_list
        if (
            _izom_propui_free_is_managed_portable_text_name(getattr(text, 'name', ''))
            or str(getattr(text, 'name', '') or '').strip() in expected_text_set
            or str(getattr(text, 'name', '') or '').strip() in generated_text_names
        )
    )
    running_keys = _izom_propui_free_running_portable_registry_keys()
    runner_keys = set()
    stale_keys = _izom_propui_free_stale_running_generated_ui_keys_from(
        running_keys,
        text_registry_key_map.keys(),
    )
    try:
        namespace = bpy.app.driver_namespace
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_debug(
            "Could not inspect generated UI class counts",
            category='Generated UI',
            exception=exc,
        )
        namespace = {}
    registered_panel_classes = ()
    stale_orphan_class_count = 0
    if deep:
        registered_panel_classes = _izom_propui_free_registered_generated_panel_classes()
        text_panel_class_names = _izom_propui_free_generated_panel_class_names_from_texts(text_list)
        stale_registry_classes = {
            panel_class
            for key in stale_keys
            for panel_class in _izom_propui_free_portable_registry_classes(namespace, key)
        }
        stale_orphan_class_count = len([
            panel_class
            for panel_class in registered_panel_classes
            if (
                panel_class not in stale_registry_classes
                and str(getattr(panel_class, '__name__', '') or '').strip() not in text_panel_class_names
            )
        ])
    status = _izom_propui_free_compute_lifecycle_status_payload(
        slots=slots,
        expected_targets=expected_targets,
        existing_text_names=existing_text_names,
        running_keys=running_keys,
        stale_keys=stale_keys,
        namespace=namespace,
        registry_class_count=_izom_propui_free_portable_registry_class_count,
        runner_key=tuple(sorted(runner_keys)),
        log_debug=izom_propui_free_log_debug,
        registered_panel_class_count=(len(registered_panel_classes) if deep else None),
        stale_orphan_class_count=stale_orphan_class_count,
        deep=deep,
    )
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CACHE[cache_key] = dict(status)
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_SIGNATURES[cache_key] = _izom_propui_free_generated_lifecycle_signature(
        text_list,
        running_keys=running_keys,
        registered_panel_classes=registered_panel_classes,
        include_source_hash=deep,
    )
    _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CHECK_TIMES[cache_key] = time.monotonic()
    return status


def izom_propui_free_refresh_generated_lifecycle_status(*, deep=False):
    status = _izom_propui_free_compute_generated_lifecycle_status(deep=deep)
    return status


def izom_propui_free_generated_lifecycle_status(*, deep=False, refresh=False, max_cache_age=0.0):
    cache_key = 'deep' if deep else 'fast'
    if refresh:
        return izom_propui_free_refresh_generated_lifecycle_status(deep=deep)
    cached = _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CACHE.get(cache_key)
    if cached is not None:
        try:
            max_age = max(0.0, float(max_cache_age or 0.0))
        except (TypeError, ValueError):
            max_age = 0.0
        if max_age > 0.0 and not deep:
            last_check = float(_IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CHECK_TIMES.get(cache_key, 0.0) or 0.0)
            if time.monotonic() - last_check < max_age:
                return dict(cached)
        registered_panel_classes = None if deep else ()
        current_signature = _izom_propui_free_generated_lifecycle_signature(
            registered_panel_classes=registered_panel_classes,
            include_source_hash=deep,
        )
        if current_signature != _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_SIGNATURES.get(cache_key):
            return izom_propui_free_refresh_generated_lifecycle_status(deep=deep)
        _IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CHECK_TIMES[cache_key] = time.monotonic()
        return dict(cached)
    return izom_propui_free_refresh_generated_lifecycle_status(deep=deep)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
