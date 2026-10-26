# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.app.handlers import persistent

from ..core.diagnostics import (
    IZOM_PROPUI_FREE_RECOVERABLE_ERRORS,
    izom_propui_free_log_error,
    izom_propui_free_log_warning,
)
from .generated_cache import _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE
from .generated_registry_lifecycle import (
    izom_propui_free_invalidate_generated_lifecycle_status_cache,
)
from .generated_registry_scripts import restore_generated_panel_from_scenes
from .generated_portable_slots import _izom_propui_free_portable_script_slots
from .lifecycle import (
    izom_propui_free_lifecycle_is_active,
    izom_propui_free_register_lifecycle_timer,
    izom_propui_free_remove_lifecycle_handler,
    izom_propui_free_replace_lifecycle_handler,
    izom_propui_free_unregister_lifecycle_timer,
)


_IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING = False
_IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_TIMER_NAME = 'generated_history_restore'
_IZOM_PROPUI_FREE_AUTO_RESTORE_WARNING_SHOWN = False


def _izom_propui_free_auto_restore_allowed():
    """Respect Blender's script decision; the restore filters missing Texts per UI."""
    global _IZOM_PROPUI_FREE_AUTO_RESTORE_WARNING_SHOWN

    if bpy.app.autoexec_fail:
        if not _IZOM_PROPUI_FREE_AUTO_RESTORE_WARNING_SHOWN:
            izom_propui_free_log_warning(
                'Blender blocked automatic Python execution for this file; '
                'automatic PropUI Free panel restore was skipped. Inspect the file '
                'before allowing scripts or generating the UI manually.',
                category='Generated UI',
            )
            _IZOM_PROPUI_FREE_AUTO_RESTORE_WARNING_SHOWN = True
        return False

    texts = bpy.data.texts
    missing_count = 0
    for slot in _izom_propui_free_portable_script_slots():
        name = str(slot.get('script_name', '') or '').strip()
        text = texts.get(name) if name else None
        if text is None or not text.use_module:
            missing_count += 1
    if missing_count and not _IZOM_PROPUI_FREE_AUTO_RESTORE_WARNING_SHOWN:
        izom_propui_free_log_warning(
            f'{missing_count} saved PropUI Free generated UI script(s) have no '
            'registered Python Text; those UIs were skipped during automatic '
            'restore. Intact UIs can still restore.',
            category='Generated UI',
        )
    _IZOM_PROPUI_FREE_AUTO_RESTORE_WARNING_SHOWN = bool(missing_count)
    return True


def _izom_propui_free_generated_history_restore_timer():
    global _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING
    if not _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING:
        return None
    _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING = False
    try:
        if _izom_propui_free_auto_restore_allowed():
            restore_generated_panel_from_scenes(cleanup=True, registered_only=True)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_error(
            "Could not reconcile generated panels after Undo/Redo",
            category='Generated UI',
            exception=exc,
        )
    return None


def _izom_propui_free_schedule_generated_history_restore():
    global _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING
    if not izom_propui_free_lifecycle_is_active():
        _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING = False
        return
    if _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING:
        return
    _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING = True
    try:
        if not izom_propui_free_register_lifecycle_timer(
            _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_TIMER_NAME,
            _izom_propui_free_generated_history_restore_timer,
            first_interval=0.05,
        ):
            raise RuntimeError('PropUI Free lifecycle is not active')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING = False
        izom_propui_free_log_warning(
            "Could not schedule generated panel reconciliation after Undo/Redo",
            category='Generated UI',
            exception=exc,
        )


@persistent
def _izom_propui_free_generated_history_post(_dummy):
    """Reconcile Python runtime panels with Blender's restored undo state."""
    _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE.clear()
    izom_propui_free_invalidate_generated_lifecycle_status_cache()
    _izom_propui_free_schedule_generated_history_restore()


def register_generated_handlers():
    for handler_name in ('undo_post', 'redo_post'):
        handlers = getattr(bpy.app.handlers, handler_name, None)
        izom_propui_free_replace_lifecycle_handler(
            handlers,
            f'generated_{handler_name}',
            _izom_propui_free_generated_history_post,
        )


def unregister_generated_handlers():
    global _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING
    _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_PENDING = False
    izom_propui_free_unregister_lifecycle_timer(
        _IZOM_PROPUI_FREE_GENERATED_HISTORY_RESTORE_TIMER_NAME,
        _izom_propui_free_generated_history_restore_timer,
    )
    for handler_name in ('undo_post', 'redo_post'):
        handlers = getattr(bpy.app.handlers, handler_name, None)
        izom_propui_free_remove_lifecycle_handler(
            handlers,
            f'generated_{handler_name}',
            _izom_propui_free_generated_history_post,
        )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
