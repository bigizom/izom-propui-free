# SPDX-License-Identifier: GPL-3.0-or-later
from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS


def izom_propui_free_compute_generated_lifecycle_status(
    *,
    slots,
    expected_targets,
    existing_text_names,
    running_keys,
    stale_keys,
    namespace,
    registry_class_count,
    runner_key,
    log_debug,
    registered_panel_class_count=None,
    stale_orphan_class_count=0,
    deep=False,
):
    expected_text_names = sorted({
        str(text_name or '').strip()
        for text_name, _registry_key in expected_targets
        if str(text_name or '').strip()
    })
    expected_registry_keys = sorted({
        str(registry_key or '').strip()
        for _text_name, registry_key in expected_targets
        if str(registry_key or '').strip()
    })
    existing_text_names = sorted(str(name or '').strip() for name in existing_text_names if str(name or '').strip())
    existing_text_set = set(existing_text_names)
    expected_text_set = set(expected_text_names)
    missing_text_names = sorted(expected_text_set - existing_text_set)
    extra_text_names = sorted(existing_text_set - expected_text_set)

    running_class_count = 0
    for key in running_keys:
        try:
            running_class_count += registry_class_count(namespace, key)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            log_debug(
                f"Could not inspect generated UI registry {key}",
                category='Generated UI',
                exception=exc,
            )

    runner_keys = runner_key if isinstance(runner_key, (list, tuple, set)) else (runner_key,)
    runner_registered = any(
        bool(getattr(namespace.get(str(key or '').strip(), None), 'bl_idname', ''))
        for key in runner_keys
        if str(key or '').strip()
    )
    try:
        stale_orphan_class_count = max(0, int(stale_orphan_class_count or 0))
    except (TypeError, ValueError):
        stale_orphan_class_count = 0
    if registered_panel_class_count is None:
        registered_panel_class_count = running_class_count + stale_orphan_class_count
    else:
        try:
            registered_panel_class_count = max(0, int(registered_panel_class_count or 0))
        except (TypeError, ValueError):
            registered_panel_class_count = running_class_count + stale_orphan_class_count
    return {
        'saved_slot_count': len(slots),
        'expected_text_count': len(expected_text_names),
        'expected_text_names': expected_text_names,
        'expected_registry_keys': expected_registry_keys,
        'existing_text_count': len(existing_text_names),
        'existing_text_names': existing_text_names,
        'missing_text_count': len(missing_text_names),
        'missing_text_names': missing_text_names,
        'extra_text_count': len(extra_text_names),
        'extra_text_names': extra_text_names,
        'running_registry_count': len(running_keys),
        'running_class_count': running_class_count,
        'registered_panel_class_count': registered_panel_class_count,
        'running_registry_keys': running_keys,
        'stale_registry_count': len(stale_keys),
        'stale_orphan_class_count': stale_orphan_class_count,
        'stale_running_count': len(stale_keys) + stale_orphan_class_count,
        'stale_registry_keys': stale_keys,
        'runner_registered': runner_registered,
        'deep': bool(deep),
    }
