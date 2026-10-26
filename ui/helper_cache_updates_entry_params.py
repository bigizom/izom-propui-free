# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_cache_updates_common import (
    _IZOM_PROPUI_FREE_BULK_ENTRY_UPDATE_GUARD,
    _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE,
    _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_OWNER_STATE,
    _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE,
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_UPDATE_CALLBACK_SUSPEND_DEPTH,
    bpy,
)
from ..core.cache_common import _izom_propui_free_pointer_guard_key
from ..core.cache_value_labels import izom_propui_free_cached_value_label_owner_map
from ..core.context import izom_propui_free_context_params
from ..core.diagnostics import (
    IZOM_PROPUI_FREE_RECOVERABLE_ERRORS,
    izom_propui_free_log_debug,
    izom_propui_free_log_recovered,
)
from ..core.value_labels_thresholds import _izom_propui_free_collection_item_matches



def _izom_propui_free_cache_entry_params(entry, params):
    if entry is None or params is None:
        return
    try:
        entry_key = _izom_propui_free_pointer_guard_key(entry)
        _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE[entry_key] = params
        _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE[entry_key] = _izom_propui_free_entry_params_owner_state(params)
    except (TypeError, ValueError):
        return


def _izom_propui_free_entry_params_owner_state(params):
    if params is None:
        return (0, 0)
    entries = getattr(params, 'izom_propui_free_entries', None)
    try:
        entries_len = len(entries) if entries is not None else 0
    except (AttributeError, TypeError, ValueError):
        entries_len = 0
    try:
        from .helper_selection import _izom_propui_free_collection_revision

        entries_revision = _izom_propui_free_collection_revision(params, 'izom_propui_free_entries')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_debug(
            "Recovered from exception while reading entry collection revision",
            category='UI',
            exception=exc,
        )
        entries_revision = 0
    return (entries_len, int(entries_revision or 0))


def _izom_propui_free_cache_params_entries(params):
    if params is None:
        return
    entries = getattr(params, 'izom_propui_free_entries', None)
    next_state = _izom_propui_free_entry_params_owner_state(params)
    params_key = _izom_propui_free_pointer_guard_key(params)
    if _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_OWNER_STATE.get(params_key) == next_state:
        return
    for entry in entries or []:
        _izom_propui_free_cache_entry_params(entry, params)
    _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_OWNER_STATE[params_key] = next_state


def _izom_propui_free_clear_cached_entry_params(params=None):
    if params is None:
        _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE.clear()
        _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE.clear()
        _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_OWNER_STATE.clear()
        return
    params_key = _izom_propui_free_pointer_guard_key(params)
    stale_keys = [
        key for key, cached_params in _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE.items()
        if cached_params is params
    ]
    for key in stale_keys:
        _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE.pop(key, None)
        _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE.pop(key, None)
    _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_OWNER_STATE.pop(params_key, None)


def _izom_propui_free_bulk_entry_updates_suspended(params):
    if params is None:
        return False
    return int(_IZOM_PROPUI_FREE_BULK_ENTRY_UPDATE_GUARD.get(_izom_propui_free_pointer_guard_key(params), 0) or 0) > 0


def _izom_propui_free_context_bulk_entry_updates_suspended(context=None):
    seen = set()
    for candidate_context in (context, bpy.context):
        params = izom_propui_free_context_params(candidate_context)
        if params is None:
            continue
        marker = _izom_propui_free_pointer_guard_key(params)
        if marker in seen:
            continue
        seen.add(marker)
        if _izom_propui_free_bulk_entry_updates_suspended(params):
            return True
    return False


def _izom_propui_free_entry_runtime_update_callbacks_suspended():
    return int(_IZOM_PROPUI_FREE_ENTRY_RUNTIME_UPDATE_CALLBACK_SUSPEND_DEPTH or 0) > 0


def _izom_propui_free_suspend_entry_runtime_update_callbacks():
    global _IZOM_PROPUI_FREE_ENTRY_RUNTIME_UPDATE_CALLBACK_SUSPEND_DEPTH
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_UPDATE_CALLBACK_SUSPEND_DEPTH += 1


def _izom_propui_free_resume_entry_runtime_update_callbacks():
    global _IZOM_PROPUI_FREE_ENTRY_RUNTIME_UPDATE_CALLBACK_SUSPEND_DEPTH
    _IZOM_PROPUI_FREE_ENTRY_RUNTIME_UPDATE_CALLBACK_SUSPEND_DEPTH = max(
        0,
        _IZOM_PROPUI_FREE_ENTRY_RUNTIME_UPDATE_CALLBACK_SUSPEND_DEPTH - 1,
    )


def _izom_propui_free_suspend_entry_updates(params):
    if params is None:
        return None
    key = _izom_propui_free_pointer_guard_key(params)
    _IZOM_PROPUI_FREE_BULK_ENTRY_UPDATE_GUARD[key] = int(_IZOM_PROPUI_FREE_BULK_ENTRY_UPDATE_GUARD.get(key, 0) or 0) + 1
    return key


def _izom_propui_free_resume_entry_updates(params):
    if params is None:
        return
    key = _izom_propui_free_pointer_guard_key(params)
    count = int(_IZOM_PROPUI_FREE_BULK_ENTRY_UPDATE_GUARD.get(key, 0) or 0)
    if count <= 1:
        _IZOM_PROPUI_FREE_BULK_ENTRY_UPDATE_GUARD.pop(key, None)
    else:
        _IZOM_PROPUI_FREE_BULK_ENTRY_UPDATE_GUARD[key] = count - 1


def _izom_propui_free_find_params_for_entry(entry, context=None):
    try:
        entry_key = _izom_propui_free_pointer_guard_key(entry)
        try:
            entry_uid = str(getattr(entry, 'uid', '') or '').strip()
        except (AttributeError, TypeError, ValueError):
            entry_uid = ''
        try:
            cached_params = _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE.get(entry_key)
        except (AttributeError, TypeError, ValueError):
            cached_params = None
        if cached_params is not None:
            cached_state = _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE.get(entry_key)
            current_state = _izom_propui_free_entry_params_owner_state(cached_params)
            if cached_state == current_state:
                return cached_params
            entries = getattr(cached_params, 'izom_propui_free_entries', None)
            cache_matches = False
            for item in entries or []:
                try:
                    if (
                        (entry_uid and str(getattr(item, 'uid', '') or '').strip() == entry_uid)
                        or _izom_propui_free_collection_item_matches(item, entry)
                    ):
                        cache_matches = True
                        break
                except RecursionError:
                    continue
                except (AttributeError, TypeError, ValueError):
                    continue
            if cache_matches:
                _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE[entry_key] = current_state
                return cached_params
            _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE.pop(entry_key, None)
            _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE.pop(entry_key, None)

        candidate_params = []
        seen_params = set()
        for candidate_context in (context, bpy.context):
            params = izom_propui_free_context_params(candidate_context)
            if params is None:
                continue
            marker = _izom_propui_free_pointer_guard_key(params)
            if marker in seen_params:
                continue
            seen_params.add(marker)
            candidate_params.append(params)

        for params in candidate_params:
            entries = getattr(params, 'izom_propui_free_entries', None)
            if not entries:
                continue
            if entry_uid:
                for item in entries:
                    try:
                        if str(getattr(item, 'uid', '') or '').strip() == entry_uid:
                            _izom_propui_free_cache_entry_params(entry, params)
                            _izom_propui_free_cache_entry_params(item, params)
                            return params
                    except (AttributeError, TypeError, ValueError):
                        continue
        for params in candidate_params:
            if izom_propui_free_cached_value_label_owner_map(params).get(entry_key) is not None:
                _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE[entry_key] = params
                _IZOM_PROPUI_FREE_ENTRY_PARAMS_CACHE_STATE[entry_key] = _izom_propui_free_entry_params_owner_state(params)
                return params
        for params in candidate_params:
            entries = getattr(params, 'izom_propui_free_entries', None)
            if not entries:
                continue
            for item in entries:
                try:
                    if _izom_propui_free_collection_item_matches(item, entry):
                        _izom_propui_free_cache_params_entries(params)
                        return params
                except RecursionError:
                    continue
                except (AttributeError, TypeError, ValueError):
                    continue
        try:
            scenes = list(bpy.data.scenes)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(category='UI', exception=exc)
            scenes = []
        for scene in scenes:
            params = getattr(scene, 'izom_propui_free', None)
            entries = getattr(params, 'izom_propui_free_entries', None) if params is not None else None
            if not entries:
                continue
            for item in entries:
                try:
                    if (
                        (entry_uid and str(getattr(item, 'uid', '') or '').strip() == entry_uid)
                        or _izom_propui_free_collection_item_matches(item, entry)
                    ):
                        _izom_propui_free_cache_params_entries(params)
                        return params
                except RecursionError:
                    continue
                except (AttributeError, TypeError, ValueError):
                    continue
    except RecursionError:
        return None
    except (AttributeError, TypeError, ValueError):
        return None
    return None

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
