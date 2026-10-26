# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from collections import deque
import time

import bpy

from bpy.types import AddonPreferences, Menu, Operator, Panel, PropertyGroup, UIList

from ..core.diagnostics import izom_propui_free_log_error, izom_propui_free_log_warning

# Module-level CLASSES tuples. The concatenation order below decides which
# classes register first within each Blender base-class tier (stable sort).
# PropertyGroup ordering matters because Settings owns CollectionProperties of
# the earlier groups; the panel must register after Settings is on Scene.
from .model_value_labels import CLASSES as _MODEL_VALUE_LABELS_CLASSES
from .model_entries import CLASSES as _MODEL_ENTRIES_CLASSES
from .model_layout import CLASSES as _MODEL_LAYOUT_CLASSES
from .generated_operators_generate import IZOM_PROPUI_FREE_OT_generate_ui
from .generated_handlers import register_generated_handlers, unregister_generated_handlers
from .editor_sections import CLASSES as _EDITOR_SECTIONS_CLASSES
from .editor_session import (
    CLASSES as _EDITOR_SESSION_CLASSES,
    izom_propui_free_register_editor_sessions,
    izom_propui_free_unregister_editor_sessions,
)
from .standalone import CLASSES as _STANDALONE_CLASSES
from .preferences import CLASSES as _PREFERENCES_CLASSES
from .lists import CLASSES as _LISTS_CLASSES
from .operators_bulk import CLASSES as _OPERATORS_BULK_CLASSES
from .operators_diagnostics import CLASSES as _OPERATORS_DIAGNOSTICS_CLASSES
from .operators_entries import CLASSES as _OPERATORS_ENTRIES_CLASSES
from .operators_entry_hierarchy import CLASSES as _OPERATORS_ENTRY_HIERARCHY_CLASSES
from .operators_entry_layout import CLASSES as _OPERATORS_ENTRY_LAYOUT_CLASSES
from .operators_sync import CLASSES as _OPERATORS_SYNC_CLASSES
from .operators_setup_transfer import CLASSES as _OPERATORS_SETUP_TRANSFER_CLASSES
from .operators_value_labels import CLASSES as _OPERATORS_VALUE_LABELS_CLASSES
from .menus import CLASSES as _MENUS_CLASSES

from .standalone import IZOM_PROPUI_FREE_Settings, register_editor_panels, unregister_editor_panels
from .lifecycle import (
    izom_propui_free_cancel_all_lifecycle_timers,
    izom_propui_free_register_lifecycle_timer,
    izom_propui_free_set_lifecycle_active,
    izom_propui_free_unregister_lifecycle_timer,
)


_REGISTRATION_PHASE_ORDER = (
    PropertyGroup,
    AddonPreferences,
    UIList,
    Operator,
    Menu,
    Panel,
)


def _izom_propui_free_phase_index(cls):
    for index, base in enumerate(_REGISTRATION_PHASE_ORDER):
        if issubclass(cls, base):
            return index
    return len(_REGISTRATION_PHASE_ORDER)


# Module concatenation order: dependents come after dependencies. The stable
# sort by Blender base class then re-groups them while preserving this order
# within each tier (so e.g. Settings stays last among PropertyGroups).
_MODULE_CLASSES_IN_DEPENDENCY_ORDER = (
    _MODEL_VALUE_LABELS_CLASSES,
    _MODEL_ENTRIES_CLASSES,
    _MODEL_LAYOUT_CLASSES,
    (IZOM_PROPUI_FREE_OT_generate_ui,),
    _EDITOR_SECTIONS_CLASSES,
    _EDITOR_SESSION_CLASSES,
    _STANDALONE_CLASSES,
    _PREFERENCES_CLASSES,
    _LISTS_CLASSES,
    _OPERATORS_BULK_CLASSES,
    _OPERATORS_DIAGNOSTICS_CLASSES,
    _OPERATORS_ENTRIES_CLASSES,
    _OPERATORS_ENTRY_HIERARCHY_CLASSES,
    _OPERATORS_ENTRY_LAYOUT_CLASSES,
    _OPERATORS_SYNC_CLASSES,
    _OPERATORS_SETUP_TRANSFER_CLASSES,
    _OPERATORS_VALUE_LABELS_CLASSES,
    _MENUS_CLASSES,
)


def _izom_propui_free_build_class_tuple():
    flat = []
    seen = set()
    for module_classes in _MODULE_CLASSES_IN_DEPENDENCY_ORDER:
        for cls in module_classes:
            if cls in seen:
                continue
            seen.add(cls)
            flat.append(cls)
    flat.sort(key=_izom_propui_free_phase_index)
    return tuple(flat)


IZOM_PROPUI_FREE_CLASSES = _izom_propui_free_build_class_tuple()

_IZOM_PROPUI_FREE_REGISTERED_CLASSES = []
_IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING = False
_IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK = None
_IZOM_PROPUI_FREE_STARTUP_WARMUP_TIME_BUDGET = 0.008
_IZOM_PROPUI_FREE_STARTUP_WARMUP_TIMER_NAME = 'startup_warmup'
_IZOM_PROPUI_FREE_REGISTERING = False
_IZOM_PROPUI_FREE_UNREGISTERING = False


def _izom_propui_free_cancel_startup_warmup():
    global _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING, _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK

    callback = _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK
    _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING = False
    _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK = None
    izom_propui_free_unregister_lifecycle_timer(
        _IZOM_PROPUI_FREE_STARTUP_WARMUP_TIMER_NAME,
        callback,
    )


def _izom_propui_free_schedule_startup_warmup():
    global _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING, _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK

    if _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING:
        return
    _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING = True
    warmup_queue = deque()
    warmup_ready = False

    def _warmup_scene_params():
        scenes = getattr(getattr(bpy, 'data', None), 'scenes', None)
        scene_list = list(scenes or [])
        try:
            active_scene = getattr(getattr(bpy, 'context', None), 'scene', None)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS:
            active_scene = None
        if active_scene in scene_list:
            scene_list.remove(active_scene)
            scene_list.insert(0, active_scene)
        params_list = []
        for scene in scene_list:
            params = getattr(scene, 'izom_propui_free', None)
            if params is not None:
                params_list.append(params)
        return params_list

    def _prepare_warmup_queue():
        try:
            from ..core.cache import (
                izom_propui_free_cached_entry_navigation_bundle,
            )
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                "Could not prepare PropUI editor cache warmup",
                category='Registration',
                exception=exc,
            )
            return False
        params_list = _warmup_scene_params()
        for params in params_list:
            warmup_queue.append((izom_propui_free_cached_entry_navigation_bundle, params))
        return True

    def _warmup_chunk():
        global _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING, _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK
        nonlocal warmup_ready

        if not warmup_ready:
            warmup_ready = _prepare_warmup_queue()
            if not warmup_ready:
                _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING = False
                _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK = None
                return None
        deadline = time.perf_counter() + _IZOM_PROPUI_FREE_STARTUP_WARMUP_TIME_BUDGET
        ran_once = False
        while warmup_queue and (not ran_once or time.perf_counter() < deadline):
            callback, params = warmup_queue.popleft()
            try:
                if params is None:
                    callback(refresh=True)
                else:
                    callback(params)
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_warning(
                    "Could not warm part of PropUI editor caches after registration",
                    category='Registration',
                    exception=exc,
                )
            ran_once = True
        if warmup_queue:
            return 0.02
        _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING = False
        _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK = None
        return None

    try:
        _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK = _warmup_chunk
        if not izom_propui_free_register_lifecycle_timer(
            _IZOM_PROPUI_FREE_STARTUP_WARMUP_TIMER_NAME,
            _warmup_chunk,
            first_interval=0.15,
        ):
            raise RuntimeError('PropUI Free lifecycle is not active')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        _IZOM_PROPUI_FREE_STARTUP_WARMUP_PENDING = False
        _IZOM_PROPUI_FREE_STARTUP_WARMUP_CALLBACK = None
        izom_propui_free_log_warning(
            "Could not schedule PropUI startup warmup",
            category='Registration',
            exception=exc,
        )


def _izom_propui_free_clear_core_caches():
    from ..core.cache import izom_propui_free_invalidate_params_cache

    izom_propui_free_invalidate_params_cache(None)


def _izom_propui_free_clear_blender_icons():
    from ..core.constants_icons import _izom_propui_free_clear_blender_icon_cache

    _izom_propui_free_clear_blender_icon_cache()


def _izom_propui_free_clear_diagnostic_records():
    from ..core.diagnostics import izom_propui_free_clear_diagnostics

    izom_propui_free_clear_diagnostics()


def _izom_propui_free_clear_generate_timing():
    from .generated_operators_generate_timing import _izom_propui_free_clear_generate_timing_cache

    _izom_propui_free_clear_generate_timing_cache()


def _izom_propui_free_clear_generated_source_headers():
    from .generated_source_header import _izom_propui_free_clear_generated_source_header_cache

    _izom_propui_free_clear_generated_source_header_cache()


def _izom_propui_free_clear_hierarchy_caches():
    from .operators_entry_hierarchy_common import _izom_propui_free_clear_hierarchy_session_caches

    _izom_propui_free_clear_hierarchy_session_caches()


def _izom_propui_free_clear_runtime_caches():
    from .helper_cache_updates import _izom_propui_free_clear_runtime_session_caches

    _izom_propui_free_clear_runtime_session_caches()


def _izom_propui_free_clear_layout_caches():
    from .helper_layout import _izom_propui_free_clear_layout_session_caches

    _izom_propui_free_clear_layout_session_caches()


def _izom_propui_free_clear_selection_caches():
    from .helper_selection import _izom_propui_free_clear_selection_session_caches

    _izom_propui_free_clear_selection_session_caches()


def _izom_propui_free_clear_value_label_caches():
    from .helper_value_labels import _izom_propui_free_clear_value_label_session_caches

    _izom_propui_free_clear_value_label_session_caches()


def _izom_propui_free_clear_ui_list_caches():
    from .lists import _izom_propui_free_clear_ui_list_session_caches

    _izom_propui_free_clear_ui_list_session_caches()


def _izom_propui_free_clear_proxy_caches():
    from .model_proxies import _izom_propui_free_clear_proxy_session_caches

    _izom_propui_free_clear_proxy_session_caches()


def _izom_propui_free_clear_entry_model_update_caches():
    from .model_entries_updates import _izom_propui_free_clear_entry_model_update_session_caches

    _izom_propui_free_clear_entry_model_update_session_caches()


def _izom_propui_free_clear_target_picker_caches():
    from .target_picker import _izom_propui_free_clear_target_picker_session_caches

    _izom_propui_free_clear_target_picker_session_caches()


_IZOM_PROPUI_FREE_EDITOR_SESSION_CLEANUPS = (
    ("core caches", _izom_propui_free_clear_core_caches),
    ("Blender icon cache", _izom_propui_free_clear_blender_icons),
    ("diagnostics", _izom_propui_free_clear_diagnostic_records),
    ("generate timing cache", _izom_propui_free_clear_generate_timing),
    ("generated source header cache", _izom_propui_free_clear_generated_source_headers),
    ("hierarchy caches", _izom_propui_free_clear_hierarchy_caches),
    ("runtime caches", _izom_propui_free_clear_runtime_caches),
    ("layout caches", _izom_propui_free_clear_layout_caches),
    ("selection caches", _izom_propui_free_clear_selection_caches),
    ("value-label caches", _izom_propui_free_clear_value_label_caches),
    ("UI list caches", _izom_propui_free_clear_ui_list_caches),
    ("proxy caches", _izom_propui_free_clear_proxy_caches),
    ("entry model update caches", _izom_propui_free_clear_entry_model_update_caches),
    ("target picker caches", _izom_propui_free_clear_target_picker_caches),
)


def _izom_propui_free_clear_editor_session_state():
    cleanup_fns = _IZOM_PROPUI_FREE_EDITOR_SESSION_CLEANUPS

    for cleanup_name, cleanup_fn in cleanup_fns:
        try:
            cleanup_fn()
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                f"Could not clear PropUI {cleanup_name}",
                category='Registration',
                exception=exc,
            )


def _izom_propui_free_unregister_registered_classes():
    remaining = list(_IZOM_PROPUI_FREE_REGISTERED_CLASSES)
    _IZOM_PROPUI_FREE_REGISTERED_CLASSES.clear()
    for pass_index in range(2):
        if not remaining:
            break
        failed_in_unregister_order = []
        for cls in reversed(remaining):
            try:
                bpy.utils.unregister_class(cls)
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                class_name = str(getattr(cls, '__name__', '') or '')
                if class_name and getattr(bpy.types, class_name, None) is None:
                    continue
                failed_in_unregister_order.append(cls)
                if pass_index > 0:
                    izom_propui_free_log_warning(
                        f"Could not unregister class {getattr(cls, '__name__', cls)}",
                        category='Registration',
                        exception=exc,
                    )
        remaining = list(reversed(failed_in_unregister_order))
    _IZOM_PROPUI_FREE_REGISTERED_CLASSES.extend(remaining)
    return not remaining


def register():
    global _IZOM_PROPUI_FREE_REGISTERING

    if _IZOM_PROPUI_FREE_REGISTERING or _IZOM_PROPUI_FREE_REGISTERED_CLASSES:
        return
    _IZOM_PROPUI_FREE_REGISTERING = True
    izom_propui_free_cancel_all_lifecycle_timers()
    izom_propui_free_set_lifecycle_active(True)
    try:
        _izom_propui_free_clear_editor_session_state()
        for cls in IZOM_PROPUI_FREE_CLASSES:
            bpy.utils.register_class(cls)
            _IZOM_PROPUI_FREE_REGISTERED_CLASSES.append(cls)
        izom_propui_free_register_editor_sessions()
        bpy.types.Scene.izom_propui_free = bpy.props.PointerProperty(
            type=IZOM_PROPUI_FREE_Settings,
        )
        register_editor_panels()
        register_generated_handlers()
        _izom_propui_free_schedule_startup_warmup()
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_set_lifecycle_active(False)
        izom_propui_free_cancel_all_lifecycle_timers()
        izom_propui_free_log_error(
            "Registration failed; rolling back partial izom PropUI registration",
            category='Registration',
            exception=exc,
        )
        try:
            unregister_generated_handlers()
        except (RuntimeError, ValueError, TypeError, AttributeError, ReferenceError) as cleanup_exc:
            izom_propui_free_log_warning(
                "Could not clean up generated history handlers after registration failure",
                category='Registration',
                exception=cleanup_exc,
            )
        try:
            unregister_editor_panels()
        except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as cleanup_exc:
            izom_propui_free_log_warning(
                "Could not clean up editor panels after registration failure",
                category='Registration',
                exception=cleanup_exc,
            )
        if hasattr(bpy.types.Scene, 'izom_propui_free'):
            try:
                del bpy.types.Scene.izom_propui_free
            except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as cleanup_exc:
                izom_propui_free_log_warning(
                    "Could not remove Scene.izom_propui_free after registration failure",
                    category='Registration',
                    exception=cleanup_exc,
                )
        try:
            izom_propui_free_unregister_editor_sessions()
        except (RuntimeError, ValueError, TypeError, AttributeError, ReferenceError) as cleanup_exc:
            izom_propui_free_log_warning(
                "Could not clean up editor sessions after registration failure",
                category='Registration',
                exception=cleanup_exc,
            )
        _izom_propui_free_unregister_registered_classes()
        _izom_propui_free_clear_editor_session_state()
        raise
    finally:
        _IZOM_PROPUI_FREE_REGISTERING = False


def unregister():
    global _IZOM_PROPUI_FREE_UNREGISTERING

    if _IZOM_PROPUI_FREE_UNREGISTERING:
        return
    _IZOM_PROPUI_FREE_UNREGISTERING = True
    izom_propui_free_set_lifecycle_active(False)
    try:
        izom_propui_free_cancel_all_lifecycle_timers()
        _izom_propui_free_cancel_startup_warmup()
        for cleanup_name, cleanup_fn in (
            ("generated history handlers", unregister_generated_handlers),
            ("editor panels", unregister_editor_panels),
        ):
            try:
                cleanup_fn()
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_warning(
                    f"Could not unregister {cleanup_name}",
                    category='Registration',
                    exception=exc,
                )
        _izom_propui_free_clear_editor_session_state()
        try:
            izom_propui_free_unregister_editor_sessions()
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                "Could not unregister editor sessions",
                category='Registration',
                exception=exc,
            )
        if hasattr(bpy.types.Scene, 'izom_propui_free'):
            try:
                del bpy.types.Scene.izom_propui_free
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_warning(
                    "Could not remove Scene.izom_propui_free",
                    category='Registration',
                    exception=exc,
                )
        if _IZOM_PROPUI_FREE_REGISTERED_CLASSES:
            _izom_propui_free_unregister_registered_classes()
        else:
            for cls in reversed(IZOM_PROPUI_FREE_CLASSES):
                try:
                    bpy.utils.unregister_class(cls)
                except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                    izom_propui_free_log_warning(
                        f"Could not unregister class {getattr(cls, '__name__', cls)}",
                        category='Registration',
                        exception=exc,
                    )
                    continue
        _izom_propui_free_clear_editor_session_state()
    finally:
        izom_propui_free_cancel_all_lifecycle_timers()
        _IZOM_PROPUI_FREE_UNREGISTERING = False
