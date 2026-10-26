# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_field_clamp_common import (
    _izom_propui_free_entry_field_update_suspended,
)
from ..core.constants_types import izom_propui_free_is_managed_prop_type
from ..core.debug import izom_propui_free_debug_print
from ..core.entry_ids import _izom_propui_free_unique_prop_id
from ..core.text import _izom_propui_free_limit_prop_id_input_text
from ..core.value_labels_thresholds import _izom_propui_free_collection_item_matches
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_PROP_ID_UPDATE_GUARD
from .helper_cache_updates_entry_params import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_find_params_for_entry,
)
from .helper_cache_updates_entry_runtime import _izom_propui_free_sync_entry_list_name
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_runtime_entry_cache



def _izom_propui_free_prop_id_updated(entry, context):
    if _izom_propui_free_entry_field_update_suspended(context):
        return
    prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    if not izom_propui_free_is_managed_prop_type(prop_type):
        current = str(getattr(entry, 'prop_id', '') or '')
        if current:
            guard_key = getattr(entry, 'uid', '') or str(entry.as_pointer())
            if guard_key in _IZOM_PROPUI_FREE_PROP_ID_UPDATE_GUARD:
                return
            _IZOM_PROPUI_FREE_PROP_ID_UPDATE_GUARD.add(guard_key)
            try:
                entry.prop_id = ''
            finally:
                _IZOM_PROPUI_FREE_PROP_ID_UPDATE_GUARD.discard(guard_key)
        return

    guard_key = getattr(entry, 'uid', '') or str(entry.as_pointer())
    if guard_key in _IZOM_PROPUI_FREE_PROP_ID_UPDATE_GUARD:
        return

    raw = _izom_propui_free_limit_prop_id_input_text(getattr(entry, 'prop_id', '')) or 'prop'
    params = _izom_propui_free_find_params_for_entry(entry, context)
    if _izom_propui_free_bulk_entry_updates_suspended(params):
        return

    existing_ids = set()
    if params:
        entry_uid = getattr(entry, 'uid', '')
        for item in getattr(params, 'izom_propui_free_entries', []):
            if _izom_propui_free_collection_item_matches(item, entry) or (entry_uid and getattr(item, 'uid', '') == entry_uid):
                continue
            if not izom_propui_free_is_managed_prop_type(getattr(item, 'prop_type', 'FLOAT')):
                continue
            other_id = str(getattr(item, 'prop_id', '') or '').strip()
            if other_id:
                existing_ids.add(other_id)

    unique = _izom_propui_free_unique_prop_id(raw, existing_ids)
    final_value = unique if params else raw
    current = getattr(entry, 'prop_id', '')
    if final_value == current:
        return

    _IZOM_PROPUI_FREE_PROP_ID_UPDATE_GUARD.add(guard_key)
    try:
        entry.prop_id = final_value
    finally:
        _IZOM_PROPUI_FREE_PROP_ID_UPDATE_GUARD.discard(guard_key)

    if final_value != raw:
        izom_propui_free_debug_print(
            f"IZOM_PROPUI_FREE WARNING: duplicate or blank Property ID auto-renamed to '{final_value}'."
        )
    _izom_propui_free_sync_entry_list_name(entry)
    _izom_propui_free_invalidate_runtime_entry_cache(params)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())
