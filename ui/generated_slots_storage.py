# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import json

from .generated_slots_normalize import (
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
    _izom_propui_free_generated_script_name_for_slot,
    _izom_propui_free_normalize_generated_slot,
)
from ..core.diagnostics import izom_propui_free_log_warning
from .generated_cache import (
    _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE,
    _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE_LIMIT,
    _izom_propui_free_cache_remember,
)
from .generated_naming import _izom_propui_free_with_unique_per_ui_script_names
from .generated_slots_common import (
    _izom_propui_free_copy_generated_slots,
    _izom_propui_free_params_key_safe,
)
from .generated_state import _izom_propui_free_data_collection


def _izom_propui_free_generated_slots_from_params(params, *, copy=True):
    if params is None:
        return []
    raw_slots = str(getattr(params, 'izom_propui_free_generated_panels_json', '') or '').strip()
    cache_key = (_izom_propui_free_params_key_safe(params), raw_slots)
    cached_slots = _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE.get(cache_key)
    if cached_slots is not None:
        return _izom_propui_free_copy_generated_slots(cached_slots) if bool(copy) else cached_slots
    slots = []
    if raw_slots:
        try:
            parsed = json.loads(raw_slots)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                "Could not parse saved generated UI panel data",
                category='Generated UI',
                exception=exc,
            )
            parsed = []
        if isinstance(parsed, list):
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                if not str(item.get('source', '') or '').strip():
                    continue
                slots.append(_izom_propui_free_normalize_generated_slot(item))
    slots = _izom_propui_free_with_unique_per_ui_script_names(slots)
    cached_copy = _izom_propui_free_copy_generated_slots(slots)
    _izom_propui_free_cache_remember(
        _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE,
        cache_key,
        cached_copy,
        _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE_LIMIT,
    )
    return _izom_propui_free_copy_generated_slots(cached_copy) if bool(copy) else cached_copy


def _izom_propui_free_global_generated_slot_script_name_by_uid():
    slots = []
    scenes = _izom_propui_free_data_collection('scenes')
    if scenes is None:
        return {}
    for scene in scenes:
        params = getattr(scene, 'izom_propui_free', None)
        if params is None:
            continue
        scene_name = str(getattr(scene, 'name', '') or '').strip()
        for slot in _izom_propui_free_generated_slots_from_params(params, copy=False):
            source = str(slot.get('source', '') or '')
            if not source:
                continue
            item = dict(slot)
            item['scene_name'] = scene_name
            item['script_name'] = _izom_propui_free_generated_script_name_for_slot(item)
            slots.append(item)
    return {
        str(slot.get('uid', '') or '').strip(): str(slot.get('script_name', '') or '').strip()
        for slot in _izom_propui_free_with_unique_per_ui_script_names(slots)
        if str(slot.get('uid', '') or '').strip() and str(slot.get('script_name', '') or '').strip()
    }


def _izom_propui_free_store_generated_slots(params, slots, *, write_scripts=True):
    from .generated_registry import (
        izom_propui_free_invalidate_generated_lifecycle_status_cache,
        _izom_propui_free_write_and_register_portable_generated_script,
    )
    serializable = []
    for item in slots or []:
        if not isinstance(item, dict):
            continue
        if not str(item.get('source', '') or ''):
            continue
        serializable.append(_izom_propui_free_normalize_generated_slot(item))
    serializable = _izom_propui_free_with_unique_per_ui_script_names(serializable)
    params.izom_propui_free_generated_panels_json = json.dumps(serializable, sort_keys=True)
    _IZOM_PROPUI_FREE_GENERATED_SLOTS_CACHE.clear()
    izom_propui_free_invalidate_generated_lifecycle_status_cache()
    if write_scripts:
        _izom_propui_free_write_and_register_portable_generated_script()


def _izom_propui_free_clear_generated_slots(params):
    if params is None:
        return
    _izom_propui_free_store_generated_slots(params, [])

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
